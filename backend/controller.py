from __future__ import annotations
from copy import deepcopy
import os
from pprint import pprint
import time
from typing import Any
from PySide6.QtCore import (
    QObject,
    Signal,
)
from backend.path_utils import absolute_path, path_basename
from pynnlib.utils import get_extension
from pynnlib import (
    Idtype,
    NnModel,
    nnlib,
    get_supported_model_extensions,
    NnFrameworkType,
    save_as,
    ShapeStrategy,
    ShapeStrategyType,
)
from pynnlib.utils.p_print import lightcyan
from ui.main_window import MainWindow



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
        self.view.signal_model_loaded.connect(self.parse_model)
        self.view.signal_inject_metadata.connect(self.event_inject_metadata)
        self.view.signal_convert_action.connect(self.event_start_conversion)
        self.view.signal_stop_action.connect(self.event_stop_conversion)

        if self.initial_model:
            self.parse_model(self.initial_model)
            self.initial_model = ""


    def parse_model(self, model_fp: str) -> None:
        ext = get_extension(model_fp)
        trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)

        device = 'cuda' if ext in trt_extensions else 'cpu'
        start_time = time.time()
        self.in_model = None
        try:
            self.in_model: NnModel = nnlib.open(model_fp, device=device)
        except Exception as e:
            raise ValueError(str(e))
        elapsed = time.time() - start_time

        self.emit_ended_signal()
        print(f"parsed in {1000*elapsed:.03f}ms")
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
        try:
            save_as(model_fp=model_fp, model=self.in_model)
        except Exception as e:
            self.signal_task_ended.emit(str(e))
            return

        self.parse_model(model_fp)
        self.signal_task_ended.emit("")


    def emit_start_signal(self, cancellable: bool) -> None:
        self.is_task_cancellable = cancellable
        self.signal_progress.emit(
            {
                'state': 'running',
                'type': 'undetermined',
                'progress': 0,
                'cancelable': cancellable,
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
        print(lightcyan("Start conversion"))
        pprint(settings)
        saved_metadata = deepcopy(self.in_model.metadata)
        self.in_model.metadata = settings['metadata']
        exception: str = ""
        to: str = settings['to']

        if to == 'safetensors':
            self.emit_start_signal(False)
            os.makedirs(settings['out_dir'], exist_ok=True)
            out_model_fp: str = os.path.join(
                settings['out_dir'], f"{path_basename(self.in_model.filepath)}.safetensors"
            )
            print(f"out path: {out_model_fp}")
            try:
                save_as(model_fp=out_model_fp, model=self.in_model)
            except Exception as e:
                exception = str(e)
                print(exception)


        elif to == 'onnx':
            self.emit_start_signal(False)
            # use the first gpu that supports fp16. Requires sysinfo
            args = settings['values']
            device: str = 'cpu'
            if args['dtype'] != 'fp32':
                device = 'cuda:0'

            # try:
            nnlib.convert_to_onnx(
                model=self.in_model,
                opset=args['opset'],
                dtype=args['dtype'],
                device=device,
                shape_strategy=ShapeStrategy(
                    type=args['shape_strategy'],
                    opt_size=args['shape']
                ),
                out_dir=settings['out_dir']
            )
            # except Exception as e:
            #     exception = str(e)
            self.signal_task_ended.emit(exception)
            if exception:
                self.emit_cancelled_signal()
            else:
                self.emit_ended_signal()

        elif to == 'tensorrt':
            self.emit_start_signal(False)
            self.convert_to_tensorrt(settings)

        else:
            exception = f"NotImplementedError: conversion to {to}"

        self.signal_task_ended.emit(exception)
        if exception:
            self.emit_cancelled_signal()
        else:
            self.emit_ended_signal()

        self.in_model.metadata = saved_metadata


    def convert_to_tensorrt(self, settings: dict[str, str | dict[str, Any]]):
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

        nnlib.convert_to_tensorrt(
            model=self.in_model,
            shape_strategy=shape_strategy,
            dtype=dtype,
            force_weak_typing=args['typing'],
            # optimization_level=,
            opset=args['opset'],
            device=device,
            out_dir=settings['out_dir'],
            overwrite=True,
        )


        # # raise NotImplementedError("tensorrt not implemented yet")
        # import sys
        # sys.exit()
        # pass

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
