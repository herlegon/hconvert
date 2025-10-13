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
from backend.path_utils import absolute_path, path_basename, path_split
from backend.user_preferences import UserPreferences
from pynnlib.utils import get_extension
from pynnlib import (
    NnModel,
    nnlib,
    get_supported_model_extensions,
    NnFrameworkType,
    save_as,
    ShapeStrategy,
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

        self.user_prefs: UserPreferences = UserPreferences()
        self.user_prefs.settings['system']['dev'] = dev

        self.initial_model: str = absolute_path(model_fp)
        if not os.path.exists(self.initial_model):
            self.initial_model = ""


    def exit(self):
        print(f"{__name__}:exit")
        p = self.view.get_user_preferences()
        self.user_prefs.save(p)
        self.view.close()


    def get_user_preferences(self):
        return self.user_prefs.settings


    # def save_user_preferences(self, preferences: dict):
    #     preferences = self.view.get_user_preferences()
    #     self.user_prefs.save(preferences)


    def set_view(self, view: MainWindow):
        self.view = view
        view.apply_user_preferences(self.user_prefs)
        self.view.signal_model_loaded.connect(self.parse_model)
        self.view.signal_inject_metadata.connect(self.event_inject_metadata)
        self.view.signal_convert_action.connect(self.event_start_conversion)

        if self.initial_model:
            self.parse_model(self.initial_model)
            self.initial_model = ""


    def parse_model(self, model_fp: str) -> None:
        self.signal_progress.emit(
            {'action': 'start', 'progress': 0}
        )

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

        self.signal_progress.emit(
            {'action': 'stop', 'progress': 100}
        )
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


    def event_start_conversion(self, settings: dict[str, str | dict[str, Any]]) -> None:
        print(lightcyan("Start conversion"))
        pprint(settings)
        saved_metadata = deepcopy(self.in_model.metadata)
        self.in_model.metadata = settings['metadata']

        if settings['to'] == 'safetensors':
            out_model_fp: str = os.path.join(
                settings['out_dir'], f"{path_basename(self.in_model.filepath)}.safetensors"
            )
            print(f"out path: {out_model_fp}")
            save_as(model_fp=out_model_fp, model=self.in_model)
            self.signal_task_ended.emit("")

        elif settings['to'] == 'onnx':
            # use the first gpu that supports fp16. Requires sysinfo
            args = settings['values']
            device: str = 'cpu'
            if args['dtype'] != 'fp32':
                device = 'cuda:0'

            exception: str = ""
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


        elif settings['to'] == 'tensorrt':
            self.convert_to_tensorrt(settings['values'])

        self.in_model.metadata = saved_metadata



    def convert_to_tensorrt(self, args: dict[str, str | dict[str, Any]]):
        pass

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
