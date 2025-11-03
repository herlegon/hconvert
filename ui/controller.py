from __future__ import annotations
from copy import deepcopy
import subprocess
from hutils import (
    absolute_path,
    path_basename,
    get_extension,
    lightcyan,
)
import os
from pprint import pprint
import time
from typing import TYPE_CHECKING, Any
from PySide6.QtCore import (
    QObject,
    Signal,
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


    def __init__(self, model_fp: str, dev: bool):
        super().__init__()
        self.view: MainWindow = None

        self.in_model: NnModel = None
        self.initial_model: str = absolute_path(model_fp)
        if not os.path.exists(self.initial_model):
            self.initial_model = ""

        self.is_task_cancellable: bool = False


    def exit(self):
        self.view.close()


    def set_view(self, view: MainWindow):
        self.view = view
        self.view.signal_model_selected.connect(self.parse_model)
        self.view.signal_inject_metadata.connect(self.event_inject_metadata)
        self.view.signal_convert_action.connect(self.event_start_conversion)
        self.view.signal_stop_action.connect(self.event_stop_conversion)

        if self.initial_model:
            self.parse_model(self.initial_model)
            self.initial_model = ""


    def parse_model(self, model_fp: str) -> None:
        alog.debug(f"parse model: {model_fp}")
        ext = get_extension(model_fp)
        trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)

        device = 'cuda' if ext in trt_extensions else 'cpu'
        start_time = time.time()
        self.in_model = None

        cmd = ["python", "backend.py", "-m", model_fp]
        # Start subprocess
        process: subprocess.Popen = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merge stderr into stdout
            text=True,
            bufsize=1,                 # line-buffered
        )

        # Read lines in real time
        for line in process.stdout:
            line = line.rstrip()
            if line:
                # Send each line to GUI widget
                self.signal_progress.emit(line)

        process.wait()  # wait for the process to finish
        if process.returncode != 0:
            self.signal_model_parsed.emit("")
            raise RuntimeError(f"Backend process failed: {process.returncode}")

        # The backend should output the JSON as the last line, for example
        # Option 1: collect all lines and parse last JSON
        process.stdout.seek(0)  # rewind if possible (or buffer lines)
        # better: collect last line while reading
        json_str = None
        for line in process.stdout:
            line = line.rstrip()
            if line.startswith("{") and line.endswith("}"):
                json_str = line

        print(json_str)
        # try:
        #     self.in_model: NnModel = nnlib.open(model_fp, device=device)
        # except Exception as e:
        #     exception = str(e)
        #     print(exception)
        #     raise ValueError(str(e))

        elapsed = time.time() - start_time

        alog.debug(f"parsed in {1000*elapsed:.03f}ms")
        self.emit_ended_signal()

        # Send a null signal because the object cannot be sent via a signal
        if self.in_model is not None:
            self.signal_model_parsed.emit(model_fp)
        else:
            self.signal_model_parsed.emit("")



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
