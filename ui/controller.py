from __future__ import annotations
from argparse import Namespace
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from threading import Event, Thread
import threading
from hutils import (
    absolute_path,
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
from typing import TYPE_CHECKING, Any, Optional
from PySide6.QtCore import (
    QObject,
    Signal,
    QTimer,
    Slot,
)
from pynnlib import (
    generate_out_model_fp,
    get_supported_model_extensions,
    Idtype,
    NnModel,
    nnlib,
    NnFrameworkType,
    save_as,
    ShapeStrategy,
    ShapeStrategyType,
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

        self.separate_backend: bool = True

        # Websocket
        self._uri: str = uri
        self._loop = None
        self._ws: ClientConnection = None
        self._running = False
        self._last_pong = time.time()

        self.connect_signals()


    def connect_signals(self):
        self.view.signal_model_selected.connect(self.parse_model)
        self.view.signal_inject_metadata.connect(self.event_inject_metadata)
        self.view.signal_convert_action.connect(self.convert_model)
        self.view.signal_stop_action.connect(self.event_stop_conversion)


    def exit(self):
        self.view.close()


    @Slot()
    def start(self):
        """Start the asyncio loop
        """
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
            self._loop.run_until_complete(self._main())

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
        self._running = False
        if getattr(self, "_loop", None):
            if not self._loop.is_closed():
                try:
                    self._loop.call_soon_threadsafe(self._loop.stop)
                    alog.info("asked to stop the asyncio loop")
                except RuntimeError:
                    # Loop may already be closing/closed
                    pass


    async def _main(self):
        retries = 0
        delay = 3
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
                await asyncio.sleep(3)
                alog.error(f"Connection error ({retries}): {e}")
                self.signal_log.emit(f"Connection error ({retries}): {e}")

                # Stop controller loop until GUI decides
                self._running = False
                self._ws = None

            finally:
                try:
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
            # self._running = True
            # self._loop.call_soon_threadsafe(
            #     lambda: asyncio.create_task(self._main())
            # )
        else:
            self.signal_log.emit("Retry requested but controller already running.")


    async def _recv_loop(self):
        try:
            async for msg in self._ws:
                data = json.loads(msg)
                msg_type = data.get("type")
                if msg_type == "pong":
                    alog.debug(f"<<< {msg_type}")
                    self._last_pong = time.time()

                elif msg_type == "progress":
                    self.signal_progress.emit(data.get("data", {}))

                elif msg_type == "result":
                    self.signal_result.emit(data.get("data", {}))

                elif msg_type == "log":
                    self.signal_log.emit(data.get("data", ""))

                elif msg_type == "system_usage":
                    self.signal_system_usage.emit(data)

                else:
                    self.signal_log.emit(f"Unknown message type: {msg_type}")

        except Exception as e:
            self.signal_log.emit(f"Recv loop ended: {e}")
            self.signal_backend_status.emit()


    async def _heartbeat_loop(self):
        while self._running and self._ws:
            alog.info(f">>> ping")
            try:
                await self.send({"cmd": "heartbeat"})
                # if no pong in 10s, mark backend down
                if time.time() - self._last_pong > 10:
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
            alog.debug(f">>> data: {data}")
            asyncio.run_coroutine_threadsafe(self.send(data), self._loop)


    @Slot()
    def cancel_task(self):
        alog.debug(f">>> cancel: {data}")
        self.send_command({"cmd": "cancel"})


    @Slot(str)
    def parse_model(self, model_fp: str) -> None:
        alog.debug(f"parse model: {model_fp}")
        ext = get_extension(model_fp)
        trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)

        device = 'cuda' if ext in trt_extensions else 'cpu'
        start_time = time.time()
        self.in_model = None

        if self.separate_backend:
            self.send_command({"cmd": "parse", "payload": {"path": model_fp}})

        else:
            try:
                self.in_model: NnModel = nnlib.open(model_fp, device=device)
            except Exception as e:
                exception = str(e)
                print(exception)
                raise ValueError(str(e))


        elapsed = time.time() - start_time

        alog.debug(f"parsed in {1000*elapsed:.03f}ms")
        self.emit_ended_signal()

        # Send a null signal because the object cannot be sent via a signal
        self.signal_model_parsed.emit(model_fp)


    def get_in_model_info(self) -> NnModel:
        # Use this function to avoid converting to/from dict
        return self.in_model


    def event_inject_metadata(self, action: dict[str, str | dict[str, str]]) -> None:
        self.in_model.metadata = action['metadata'].copy()
        model_fp: str = action['filepath']
        # try:
        save_as(model_fp=model_fp, model=self.in_model, autonaming=False)
        # except Exception as e:
        #     self.signal_task_ended.emit(str(e))
        #     return

        self.parse_model(model_fp)
        self.signal_task_ended.emit("")


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

        self.send_command({"cmd": "convert", "payload": settings})

        if to == 'safetensors':
            out_model_fp: str = os.path.join(
                settings['out_dir'], f"{path_basename(self.in_model.filepath)}.safetensors"
            )
            self.emit_start_signal(False, out_model_fp)
            try:
                os.makedirs(settings['out_dir'], exist_ok=True)
                save_as(model_fp=out_model_fp, model=self.in_model)
            except Exception as e:
                exception = str(e)

        elif to == 'onnx':
            # use the first gpu that supports fp16. Requires sysinfo
            args = settings['values']
            device: str = 'cpu'
            if args['dtype'] != 'fp32':
                device = 'cuda:0'

            common_kwargs = dict(
                model=self.in_model,
                opset=args['opset'],
                dtype=args['dtype'],
                device=device,
                shape_strategy=ShapeStrategy(
                    type=args['shape_strategy'],
                    opt_size=args['shape']
                ),
                out_dir=settings['out_dir'],
            )

            out_model_fp = generate_out_model_fp(to=NnFrameworkType.ONNX, **common_kwargs)
            self.emit_start_signal(False, out_model_fp)
            alog.debug(f"out model: {out_model_fp}")

            try:
                nnlib.convert_to_onnx(**common_kwargs)
            except Exception as e:
                exception = str(e)

        elif to == 'tensorrt':
            exception = self.convert_to_tensorrt(settings)

        else:
            exception = f"NotImplementedError: conversion to {to}"

        self.signal_task_ended.emit(exception)
        if exception:
            alog.error(exception)
            self.emit_cancelled_signal()
        else:
            self.emit_ended_signal()

        self.in_model.metadata = saved_metadata


    def convert_to_tensorrt(self, settings: dict[str, str | dict[str, Any]]) -> str:
        exception: str = ""
        args: dict[str, str | dict[str, Any]]
        args = settings['values']

        shape_strategy: ShapeStrategy = ShapeStrategy(
            type=args['shape_strategy'],
            min_size=args['shape_min'],
            opt_size=args['shape_min'],
            max_size=args['shape_min'],
        )

        device = args['gpu']
        device = device if device else "cuda"
        dtype: Idtype = 'fp32'
        if 'fp16' in args['dtypes']:
            dtype = 'fp16'
        elif 'bf16' in args['dtypes']:
            dtype = 'bf16'

        common_kwargs = dict(
            model=self.in_model,
            shape_strategy=shape_strategy,
            dtype=dtype,
            force_weak_typing=bool(args['typing'] == 'weak'),
            # optimization_level=,
            opset=args['opset'],
            device=device,
            out_dir=settings['out_dir'],
        )

        out_model_fp = generate_out_model_fp(to=NnFrameworkType.TENSORRT, **common_kwargs)
        self.emit_start_signal(False, out_model_fp)

        # try:
        #     nnlib.convert_to_tensorrt(**common_kwargs)
        # except Exception as e:
        #     exception = str(e)
        nnlib.convert_to_tensorrt(**common_kwargs)

        return exception

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
