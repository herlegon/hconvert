from __future__ import annotations
from argparse import Namespace
import asyncio
from copy import deepcopy
from ui.deserialize import deserialize_model
import json
import subprocess
import sys
import threading
from hytils import (
    lightgreen,
    path_basename,
    get_extension,
    lightcyan,
    purple,
    red,
    yellow,
)
import os
from pprint import pprint
import time
from typing import TYPE_CHECKING, Any
from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from .pynnlib_helpers import get_supported_model_extensions
from .pynnlib_api import (
    NnFrameworkType,
    NnModel,
    ShapeStrategy,
    Hdtype,
)

if TYPE_CHECKING:
    from ui.main_window import MainWindow

from ui.logger import alog
from websockets import (
    connect,
    ClientConnection,
    ConnectionClosedError,
    ConnectionClosedOK,
)



# Controller as a regular QObject (not a QThread)
# Created in the main thread, then moved to another thread
# !!! The Controller's slots will execute in the worker thread!!!
# Better separation of concerns - Controller focuses on work, QThread manages the thread
# More flexible: move the object back or to different threads
# Allows better testing (can test Controller without threading)
# Recommended approach by Qt documentation

class Controller(QObject):
    signal_progress: Signal = Signal(dict)
    signal_out_fp: Signal = Signal(dict)
    signal_model_parsed: Signal = Signal(str)
    signal_task_ended: Signal = Signal(str)

    signal_model_parsing_started: Signal = Signal(str)
    signal_model_injection_started: Signal = Signal(str)

    # Signals to update GUI
    signal_log = Signal(str)
    signal_result = Signal(dict)
    signal_system_usage = Signal(dict)
    # status: 'running', 'stopped'
    signal_backend_status = Signal(str)


    def __init__(
        self,
        view: MainWindow,
        args: Namespace,
        uri: str="ws://127.0.0.1:8442"
    ):
        super().__init__()

        dev: bool = False
        try:
            dev = args.dev
        except:
            pass

        self.view: MainWindow = view
        self.in_model: NnModel = None

        # Websocket
        self._uri: str = uri
        self._loop = None
        self._ws: ClientConnection = None
        self._running = False
        self._last_pong = None
        self._is_shutting_down = False
        self._is_server_ready: bool = False
        self._server_ready_event: threading.Event = threading.Event()

        self._backend_process: subprocess.Popen | None = None
        self._backend_thread: threading.Thread | None = None

        self.connect_signals()


    def connect_signals(self):
        self.view.signal_model_selected.connect(self.parse_model)
        self.view.signal_inject_metadata.connect(self.event_inject_metadata)
        self.view.signal_convert_action.connect(self.convert_model)
        self.view.signal_stop_action.connect(self.event_stop_conversion)


    def exit(self):
        print(red("controller exit: why?"))
        self.view.close()


    @Slot()
    def start_backend(self, backend_script: str, dev_mode: bool = False) -> None:
        """Starts backend subprocess in a thread and forward stdout/stderr.
        ignored if dev_mode. No need to catch trace
        """
        if not dev_mode:
            print(f"start_backend")
            if self._backend_process and self._backend_process.poll() is None:
                self.signal_log.emit("Backend is already running")
                print("Backend is already running")
                return

            # Clear the ready event before starting
            self._server_ready_event.clear()
            self._is_server_ready = False

            self._backend_thread = threading.Thread(
                target=self._backend_runner, args=(backend_script,), daemon=True
            )
            self._backend_thread.start()
            self.signal_log.emit(f"Starting backend: {backend_script}")

        else:
            # COnsider that the server is already running
            self._last_pong = time.time()
            self._is_server_ready = True
            self._server_ready_event.set()
            self.signal_log.emit("Backend is ready")


    def _backend_runner(self, backend_script: str):
        """Run the backend process and forward output to GUI / terminal."""
        print(f"_backend_runner")
        try:
            self._backend_process = subprocess.Popen(
                [sys.executable, "-u", backend_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,  # gives str lines, cross-platform
                start_new_session=False,  # keeps it tied to parent process group
            )

            # Wait until backend prints "READY"
            for line in iter(self._backend_process.stdout.readline, ""):
                sys.stdout.write(line)
                sys.stdout.flush()
                if "READY" in line:
                    print("ready!!!!!")
                    self._last_pong = time.time()
                    self._is_server_ready = True
                    self._server_ready_event.set()  # Signal that server is ready
                    self.signal_log.emit("Backend is ready")
                    break


            # Forward stdout
            def forward(stream, target):
                for line in iter(stream.readline, ""):
                    target.write(line)
                    target.flush()
                    line = line.rstrip()
                    # print(line)
                    # try:
                    #     self.signal_log.emit(line)
                    # except:
                    #     pass
                stream.close()

            threads = [
                threading.Thread(target=forward, args=(self._backend_process.stdout, sys.stdout)),
                threading.Thread(target=forward, args=(self._backend_process.stderr, sys.stderr)),
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            return_code = self._backend_process.wait()
            self.signal_log.emit(f"Backend exited with code {return_code}")

        finally:
            self._backend_process = None


    @Slot()
    def stop_backend(self):
        """Terminate backend process if running."""
        print(f"stop_backend")

        if self._backend_process and self._backend_process.poll() is None:
            self.signal_log.emit("Stopping backend...")
            self._backend_process.terminate()
            try:
                self._backend_process.wait(timeout=5)

            except subprocess.TimeoutExpired:
                self._backend_process.kill()
                self._backend_process.wait()
            self._backend_process = None

        self._is_server_ready = False
        self._server_ready_event.clear()


    @Slot()
    def start(self):
        """Start the asyncio loop
        """
        print("controller: start")
        if self._running:
            alog.info("The asyncio loop is already running. Ignore.")
            return
        self._running = True
        alog.info("Start a new asyncio loop")
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop_runner, daemon=True).start()
        alog.info("started")


    def _loop_runner(self):
        try:
            asyncio.set_event_loop(self._loop)
            result = self._loop.run_until_complete(self._main())
            if result is not None:
                alog.info(f"Controller _main result: {result}")

        except Exception as e:
            self.signal_log.emit(f"Controller loop crashed: {e}")

        finally:
            # Clean shutdown
            if self._loop and not self._loop.is_closed():
                # Cancel all pending tasks cleanly
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                try:
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass

                try:
                    self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                except Exception:
                    pass
                self._loop.close()

        if self._running:
            self.signal_log.emit("Controller loop stopped")
        alog.info("The asyncio loop has been stopped")


    @Slot()
    def stop(self):
        self._is_shutting_down = True
        self._running = False
        if getattr(self, "_loop", None):
            if not self._loop.is_closed():
                try:
                    self._loop.call_soon_threadsafe(self._loop.stop)
                    alog.info("asked to stop the asyncio loop")
                except RuntimeError:
                    # Loop may already be closing/closed
                    pass


    @Slot()
    def shutdown(self):
        """Handle graceful shutdown when the window is closed"""
        self._is_shutting_down = True
        alog.info("Shutting down the backend...")

        # Send a shutdown command to the backend (if needed)
        if self._ws:
            print(yellow(f"{__class__.__name__} shutdown"))
            try:
                shutdown_command = {"cmd": "shutdown"}  # Example shutdown command
                asyncio.run_coroutine_threadsafe(self.send(shutdown_command), self._loop)
                alog.info("Shutdown command sent to server")
            except Exception as e:
                alog.error(f"Failed to send shutdown command: {e}")

        if self._backend_process and self._backend_process.poll() is None:
            alog.info("Terminating backend process...")
            self._backend_process.terminate()

        if self._backend_process is not None:
            try:
                self._backend_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                alog.warning("Backend didn't stop, killing...")
                self._backend_process.kill()

        # Stop the asyncio loop
        self.stop()  # This calls the stop method that you've already implemented
        alog.info("Controller stopped")


    async def _wait_for_server_ready(self, timeout: float = 30.0):
        """Wait for the server to be ready, with timeout."""
        start_time = time.time()
        while self._running and not self._is_shutting_down:
            if self._server_ready_event.wait(timeout=0.5):
                return True

            # Check for timeout
            if time.time() - start_time > timeout:
                self.signal_log.emit("Timeout waiting for backend to be ready")
                return False

            # Check if backend process died
            if self._backend_process and self._backend_process.poll() is not None:
                self.signal_log.emit("Backend process terminated before becoming ready")
                return False

        return False


    async def _main(self):
        retries = 0
        delay = 3

        # Wait for server to be ready before attempting connection
        self.signal_log.emit("Waiting for backend to be ready...")
        if not await self._wait_for_server_ready():
            self.signal_log.emit("Backend failed to start")
            self._running = False
            return

        while self._running:
            try:
                alog.info(f"Connecting to {self._uri}")
                self.signal_log.emit(f"Connecting to {self._uri}")
                ws: ClientConnection
                async with connect(
                    uri=self._uri,
                    proxy=None,
                    ping_interval=3,
                    ping_timeout=2,
                ) as ws:
                    retries = 0
                    self._ws = ws
                    self.signal_log.emit("Connected to backend")
                    self.signal_backend_status.emit('running')

                    # Update pong timestamp when we receive a pong
                    ws.pong_handler = lambda _: setattr(self, "_last_pong", time.time())

                    await asyncio.gather(
                        self._recv_loop(),
                        self._heartbeat_loop(),
                    )

            except (ConnectionClosedError, ConnectionClosedOK) as e:
                alog.warning(f"WebSocket closed: {e}")
                self.signal_log.emit(f"Connection closed: {e}")

            except Exception as e:
                retries += 1
                # await asyncio.sleep(3)
                alog.error(f"Connection error ({retries}): {e}")
                self.signal_log.emit(f"Connection error ({retries}): {e}")

                # Stop controller loop until GUI decides
                self._running = False
                self._ws = None
                await asyncio.sleep(3)

            finally:
                try:
                    if not self._is_shutting_down:
                        self.signal_backend_status.emit("stopped")
                except:
                    pass
                self._ws = None

                if self._running:
                    await asyncio.sleep(3)  # small retry delay

        self._running = False
        self._ws = None
        alog.info("asyncio loop has been terminated")


    def retry_connect(self):
        if not self._running:
            self.start()
        else:
            self.signal_log.emit("Retry requested but controller already running.")


    async def _recv_loop(self):
        """Receive messages from the WebSocket."""
        try:
            async for message in self._ws:
                if self._is_shutting_down:
                    break

                try:
                    data = json.loads(message)
                    await self._handle_message(data)

                except json.JSONDecodeError as e:
                    alog.error(f"Invalid JSON received: {e}")

                except Exception as e:
                    alog.error(f"Error handling message: {e}")

        except Exception as e:
            alog.error(f"Receive loop error: {e}")
            raise


    async def _handle_message(self, data: dict):
        """Handle incoming messages from the backend."""
        msg_type = data.get("type")
        payload = data.get("payload", {})
        # alog.debug(lightcyan(f"<<< {msg_type}"))

        if msg_type == "pong":
            # alog.debug(f"<<< {msg_type}")
            self._last_pong = time.time()

        elif msg_type == "error":
            print(red("DO IT RIGHT NOW"))
            self.signal_task_ended.emit(payload)
            self.emit_cancelled_signal()

            # self.emit_ended_signal()


        elif msg_type == "parsed":
            print(yellow(f"<<< {msg_type}"))
            model_json = payload.get("model")

            # Deserialize JSON back into Python object
            self.in_model = deserialize_model(model_json)
            alog.debug(f"Model parsed and received from backend")
            # pprint(self.in_model)

            self.emit_ended_signal()
            self.signal_model_parsed.emit(self.in_model.filepath)

        elif msg_type == "progress":
            if payload['state'] == 'started':
                self.emit_start_signal(False, payload['model_fp'])

            self.signal_progress.emit(payload)


        elif msg_type == "injected":
            # Task completed
            # task_name = payload.get("type", "")
            print(yellow(f"<<< {msg_type}"))
            model_json = payload.get("model")
            self.in_model = deserialize_model(model_json)
            self.emit_ended_signal()
            self.signal_model_parsed.emit(self.in_model.filepath)


        elif msg_type == "log":
            # Log message from backend
            log_msg = payload.get("message", "")
            self.signal_log.emit(log_msg)

        elif msg_type == "system_usage":
            # System usage statistics
            self.signal_system_usage.emit(payload)

        else:
            alog.warning(f"Unknown message type: {msg_type}")



    async def _heartbeat_loop(self):
        while self._running and self._ws:
            # alog.info(f">>> ping")
            try:
                await self.send({"cmd": "heartbeat"})
                # if no pong in 10s, mark backend down
                if self._last_pong is None:
                    self._last_pong = time.time()

                elif time.time() - self._last_pong > 10:
                    self.signal_log.emit("Backend unresponsive")
                    self.signal_backend_status.emit()
                    break
                await asyncio.sleep(3)

            except Exception:
                break


    async def send(self, data: dict):
        if not self._ws:
            alog.warning(f"Try to send a command while not connected to the backend")
            return
        try:
            await self._ws.send(json.dumps(data))
        except Exception as e:
            self.signal_log.emit(f"Send failed: {e}")


    # Public slots to call from GUI threads
    @Slot(dict)
    def send_command(self, data: dict):
        if self._loop:
            alog.debug(lightgreen(f">>> data: {data}"))
            asyncio.run_coroutine_threadsafe(self.send(data), self._loop)


    @Slot()
    def cancel_task(self):
        alog.debug(f">>> cancel")
        self.send_command({"cmd": "cancel"})


    @Slot(str)
    def parse_model(self, model_fp: str) -> None:
        alog.debug(f"parse model: {model_fp}")
        ext = get_extension(model_fp)
        trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)
        device = 'cuda' if ext in trt_extensions else 'cpu'

        self.send_command(
            {
                "cmd": "parse",
                "payload": {
                    "path": model_fp
                }
            }
        )

        # Emit that parsing has started
        self.signal_model_parsing_started.emit(model_fp)


    def get_in_model_info(self) -> NnModel:
        # Use this function to avoid converting to/from dict
        return self.in_model


    def event_inject_metadata(self, action: dict[str, str | dict[str, str]]) -> None:
        self.in_model.metadata = action['metadata'].copy()
        model_fp: str = action['filepath']
        alog.debug(f"inject metadata: {model_fp}")

        self.send_command(
            {
                "cmd": "inject",
                "payload": {
                    "in_model_fp": self.in_model.filepath,
                    "out_model_fp": model_fp,
                    "metadata": self.in_model.metadata,
                }
            }
        )

        # Emit that injection has started
        self.signal_model_injection_started.emit(model_fp)


    def emit_start_signal(self, cancellable: bool, out_model_fp: str) -> None:
        self.is_task_cancellable = cancellable
        self.signal_progress.emit(
            {
                'state': 'running',
                'type': 'undetermined',
                'progress': 0,
                'cancelable': cancellable,
                'out_model_fp': out_model_fp,
            }
        )


    def emit_cancelled_signal(self) -> None:
        self.signal_progress.emit(
            {
                'state': 'cancelled',
                'type': 'undetermined',
                'progress': 100,
                'cancelable': True,
            }
        )


    def emit_ended_signal(self) -> None:
        self.signal_progress.emit(
            {
                'state': 'ended',
                'type': 'undetermined',
                'progress': 100,
                'cancelable': True,
            }
        )


    def event_stop_conversion(self) -> None:
        if self.is_task_cancellable:
            self.signal_progress.emit(
                {
                    'state': 'stopped',
                    'type': 'undetermined',
                    'progress': 100,
                    'cancelable': True,
                }
            )


    @Slot(dict)
    def convert_model(self, settings: dict[str, str | dict[str, Any]]) -> None:
        alog.debug("event_start_conversion")
        alog.debug(f"{settings}")

        saved_metadata = deepcopy(self.in_model.metadata)
        self.in_model.metadata = settings['metadata']
        exception: str = ""
        to: str = settings['to']
        out_model_fp: str = ""

        if to == 'safetensors':
            out_model_fp: str = os.path.join(
                settings['out_dir'], f"{path_basename(self.in_model.filepath)}.safetensors"
            )

        self.send_command(
            {
                "cmd": "convert",
                "payload": {
                    'in_model_fp': self.in_model.filepath,
                    'out_model_fp': out_model_fp,
                    'settings': settings,
                }

            }
        )

        self.emit_start_signal(False, out_model_fp)


        # self.signal_task_ended.emit(exception)
        # if exception:
        #     alog.error(exception)
        #     self.emit_cancelled_signal()
        # else:
        #     self.emit_ended_signal()

        # self.in_model.metadata = saved_metadata


# import asyncio
# from PySide6.QtCore import QObject, Signal
# from qasync import QEventLoop, asyncSlot
# from PySide6.QtWidgets import QApplication

# class Worker(QObject):
#     started = Signal()

#     def __init__(self):
#         super().__init__()
#         self.task = None
#         self.started.connect(self.on_started)

#     @asyncSlot()
#     async def on_started(self):
#         print("Worker signal received, starting async task...")

#         async def do_work():
#             try:
#                 for i in range(5):
#                     print(f"Working... {i}")
#                     await asyncio.sleep(1)
#                 print("Async task finished.")
#             except asyncio.CancelledError:
#                 print("Task cancelled!")

#         self.task = asyncio.create_task(do_work())

# # ---- Run the application and asyncio loop ----
# if __name__ == "__main__":
#     import sys
#     from qasync import QEventLoop

#     app = QApplication(sys.argv)
#     loop = QEventLoop(app)
#     asyncio.set_event_loop(loop)

#     worker = Worker()
#     worker.started.emit()  # Fire the signal to trigger the async task

#     with loop:
#         loop.run_forever()
