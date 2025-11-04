from __future__ import annotations
from argparse import Namespace
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from threading import Event, Thread
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




class Controller(QObject):
    signal_progress: Signal = Signal(dict)
    signal_out_fp: Signal = Signal(dict)
    signal_model_parsed: Signal = Signal(str)
    signal_task_ended: Signal = Signal(str)


    stdout_message = Signal(dict)   # JSON messages from backend stdout
    stderr_line = Signal(str)       # plain log lines from backend stderr
    backend_down = Signal()         # emitted when backend stops responding


    def __init__(self, view: MainWindow, args: Namespace):
        super().__init__()

        dev: bool = False
        try:
            dev = args.dev
        except:
            pass

        self.view: MainWindow = None

        self.in_model: NnModel = None

        self.is_task_cancellable: bool = False

        self.separate_backend = True

        #  cmd = ["python", "backend.py", "-m", model_fp]
        backend_path = Path(__file__).resolve().parent.parent.joinpath("backend", "backend_pipes.py")
        print(red(f"{backend_path}"))

        self.backend_cmd = [sys.executable, "-u", str(backend_path)]
        print(self.backend_cmd)
        heartbeat_interval: float = 3
        pong_timeout: float = 3

        self.heartbeat_interval = heartbeat_interval
        self.pong_timeout = pong_timeout

        # Thread & loop state
        self._thread: Optional[Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_ready = Event()

        # Async process & tasks (created inside event loop)
        self._proc = None                   # asyncio.subprocess.Process (only used inside loop)
        self._tasks = []                    # list of asyncio.Task inside loop
        self._last_pong = time.time()
        self._stop_requested = False

        self.set_view(view)


    def set_view(self, view: MainWindow):
        self.view = view
        self.view.signal_model_selected.connect(self.parse_model)
        self.view.signal_inject_metadata.connect(self.event_inject_metadata)
        self.view.signal_convert_action.connect(self.event_start_conversion)
        self.view.signal_stop_action.connect(self.event_stop_conversion)




    def start(self):
        """Start the controller thread and its asyncio loop."""
        print(yellow("start"))
        if self._thread and self._thread.is_alive():
            return
        self._stop_requested = False
        self._thread = Thread(target=self._thread_main, name="ControllerThread", daemon=True)
        self._thread.start()
        # wait for loop to be ready
        self._loop_ready.wait(timeout=5.0)
        if not self._loop:
            raise RuntimeError("Failed to start asyncio loop for controller")

        # schedule the process manager coroutine
        asyncio.run_coroutine_threadsafe(self._proc_manager(), self._loop)


    def stop(self):
        """Stop the controller and shutdown the backend."""
        self._stop_requested = True
        if self._loop:
            fut = asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
            try:
                fut.result(timeout=5.0)
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=2.0)



    def _thread_main(self):
        """Target for the controller thread: create and run an asyncio loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._loop_ready.set()
        try:
            loop.run_forever()
        finally:
            # Clean up pending tasks
            pending = asyncio.all_tasks(loop=loop)
            for t in pending:
                t.cancel()
            try:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            loop.close()
            self._loop = None
            self._loop_ready.clear()


    # --------------------------
    # Public API (sync wrappers)
    # --------------------------
    def start_task(self, task_id: int, filepath: str, settings: dict[str, Any]):
        """Start a long-running task in the backend."""
        coro = self._send_command({"cmd": "start_task", "id": task_id, "filepath": filepath, "settings": settings})
        return self._submit(coro)

    def kill_task(self):
        """Request backend to kill current task."""
        coro = self._send_command({"cmd": "kill_task"})
        return self._submit(coro)

    def send_raw_command(self, obj: dict[str, Any]):
        """Send arbitrary command to backend (NDJSON)."""
        coro = self._send_command(obj)
        return self._submit(coro)

    def request_quit(self):
        """Ask backend to quit; controller will also shutdown."""
        coro = self._send_command({"cmd": "quit"})
        fut = self._submit(coro)
        # also schedule local shutdown
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
        return fut


    # --------------------------
    # Internal helpers
    # --------------------------
    def _submit(self, coro):
        """Schedule a coroutine on the controller loop and return a concurrent Future."""
        if not self._loop:
            raise RuntimeError("Controller loop not running")
        return asyncio.run_coroutine_threadsafe(coro, self._loop)


    async def _shutdown(self):
        """Cleanup inside the event loop: cancel tasks, terminate process, stop loop."""
        # stop tasks
        for t in list(self._tasks):
            if not t.done():
                t.cancel()
        await asyncio.sleep(0)  # allow cancellations to propagate

        # terminate process
        if self._proc:
            try:
                # best effort: ask backend to quit
                try:
                    line = json.dumps({"cmd": "quit"}, separators=(",", ":")) + "\n"
                    self._proc.stdin.write(line.encode())
                    await self._proc.stdin.drain()
                except Exception:
                    pass
                await asyncio.wait_for(self._proc.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            except Exception:
                pass
            self._proc = None

        # stop the loop
        loop = asyncio.get_event_loop()
        loop.stop()


    async def _proc_manager(self):
        """Create the backend subprocess and spawn readers + heartbeat task."""
        print("_proc_manager")
        if self._proc:
            print(red("error"))
            return

        # launch backend as subprocess with pipes
        self._proc = await asyncio.create_subprocess_exec(
            *self.backend_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # spawn readers and heartbeat monitor
        t_stdout = asyncio.create_task(self._stdout_reader(self._proc.stdout))
        t_stderr = asyncio.create_task(self._stderr_reader(self._proc.stderr))
        t_hb = asyncio.create_task(self._heartbeat_loop())

        self._tasks.extend([t_stdout, t_stderr, t_hb])

        # wait for process to exit; when it does, emit backend_down
        async def wait_proc():
            try:
                await self._proc.wait()
            finally:
                # emit signal to GUI thread
                try:
                    self.backend_down.emit()
                except Exception:
                    pass

        t_wait = asyncio.create_task(wait_proc())
        self._tasks.append(t_wait)


    async def _stdout_reader(self, stream: asyncio.StreamReader):
        """Read lines from backend stdout, parse JSON, emit signals."""
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode(errors="replace").strip()
                print(f"<<< {text}")
                if not text:
                    continue
                try:
                    obj = json.loads(text)
                except Exception:
                    # non-json line -> emit as stderr_line to show raw
                    try:
                        self.stderr_line.emit(f"Non-JSON stdout: {text}")
                    except Exception:
                        pass
                    continue

                # update last pong on pong
                if obj.get("type") == "pong":
                    self._last_pong = time.time()

                # emit parsed JSON to GUI
                try:
                    self.stdout_message.emit(obj)
                except Exception:
                    pass
        except asyncio.CancelledError:
            return
        except Exception as e:
            try:
                self.stderr_line.emit(f"stdout_reader error: {e}")
            except Exception:
                pass


    async def _stderr_reader(self, stream: asyncio.StreamReader):
        """Relay backend stderr lines to GUI."""
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode(errors="replace").rstrip("\n")
                try:
                    self.stderr_line.emit(text)
                    print(text)
                except Exception:
                    pass
        except asyncio.CancelledError:
            return
        except Exception as e:
            try:
                self.stderr_line.emit(f"stderr_reader error: {e}")
            except Exception:
                pass

    async def _send_command(self, obj: dict[str, Any]):
        """Write NDJSON into backend stdin."""
        if not self._proc or not self._proc.stdin:
            raise RuntimeError("Backend process not running")
        try:
            line = json.dumps(obj, separators=(",", ":")) + "\n"
            self._proc.stdin.write(line.encode())
            await self._proc.stdin.drain()
        except Exception as e:
            # propagate as exception to caller (future)
            raise

    async def _heartbeat_loop(self):
        """Periodically send heartbeat and check pong timeliness."""
        try:
            while True:
                # send heartbeat
                try:
                    if self._proc and self._proc.stdin:
                        line = json.dumps({"cmd": "heartbeat"}, separators=(",", ":")) + "\n"
                        self._proc.stdin.write(line.encode())
                        print(f">>> ping")
                        await self._proc.stdin.drain()
                except Exception:
                    # backend likely dead; emit backend_down and break
                    try:
                        self.backend_down.emit()
                    except Exception:
                        pass
                    break

                # check pong freshness
                now = time.time()
                if now - self._last_pong > self.pong_timeout:
                    try:
                        self.stderr_line.emit("No pong from backend (timeout)")
                        print(red("No pong from backend (timeout)"))
                        self.backend_down.emit()
                    except Exception:
                        pass
                    # Optionally: attempt restart by re-running proc_manager
                    # For now, break out; external code may call start() to restart.
                    break

                await asyncio.sleep(self.heartbeat_interval)
        except asyncio.CancelledError:
            return
        except Exception as e:
            try:
                self.stderr_line.emit(f"heartbeat error: {e}")
            except Exception:
                pass



    def exit(self):
        self.view.close()




    def parse_model(self, model_fp: str) -> None:
        alog.debug(f"parse model: {model_fp}")
        ext = get_extension(model_fp)
        trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)

        device = 'cuda' if ext in trt_extensions else 'cpu'
        start_time = time.time()
        self.in_model = None

        if self.separate_backend:
            self.start_task(
                task_id=42,
                filepath=model_fp,
                settings={}
            )
        #     cmd = ["python", "backend.py", "-m", model_fp]
        #     # Start subprocess
        #     process: subprocess.Popen = subprocess.Popen(
        #         cmd,
        #         stdout=subprocess.PIPE,
        #         stderr=subprocess.STDOUT,  # merge stderr into stdout
        #         text=True,
        #         bufsize=1,                 # line-buffered
        #     )

        #     # Read lines in real time
        #     for line in process.stdout:
        #         line = line.rstrip()
        #         if line:
        #             # Send each line to GUI widget
        #             # self.signal_progress.emit(line)
        #             print(purple(line))

        #     process.wait()  # wait for the process to finish
        #     if process.returncode != 0:
        #         self.signal_model_parsed.emit(model_fp)
        #         alog.error(f"Backend process failed: {process.returncode}")

        #     else:
        #         # The backend should output the JSON as the last line, for example
        #         # Option 1: collect all lines and parse last JSON
        #         process.stdout.seek(0)  # rewind if possible (or buffer lines)
        #         # better: collect last line while reading
        #         json_str = None
        #         for line in process.stdout:
        #             line = line.rstrip()
        #             if line.startswith("{") and line.endswith("}"):
        #                 json_str = line

        #     # print(json_str)
        #     # try:
        #     #     self.in_model: NnModel = nnlib.open(model_fp, device=device)
        #     # except Exception as e:
        #     #     exception = str(e)
        #     #     print(exception)
        #     #     raise ValueError(str(e))
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


    def event_start_conversion(self, settings: dict[str, str | dict[str, Any]]) -> None:
        alog.debug("event_start_conversion")
        alog.debug(f"{settings}")

        saved_metadata = deepcopy(self.in_model.metadata)
        self.in_model.metadata = settings['metadata']
        exception: str = ""
        to: str = settings['to']

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
