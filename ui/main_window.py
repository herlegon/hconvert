from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, Any
from PySide6.QtCore import (
    Signal,
    QThread,
    Qt,
)
from PySide6.QtGui import (
    QCloseEvent,
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)

from backend.path_utils import absolute_path, get_extension
from ui.common import SUPPORTED_MODEL_EXTENSIONS

from .inject_metadata_dialog import inject_metadata_dialog

from .designer.ui_main_window import Ui_MainWindow
if TYPE_CHECKING:
    from backend.controller import Controller
    from backend.user_preferences import UserPreferences

from pynnlib import (
    NnModel,
    NnFrameworkType,
)
from pynnlib.utils.p_print import *


class MainWindow(QMainWindow, Ui_MainWindow):
    signal_preview_modified = Signal(dict)
    signal_convert_action = Signal(dict)
    signal_model_loaded = Signal(str)
    signal_inject_metadata = Signal(dict)


    def __init__(self, controller: Controller):
        super().__init__()
        self.setupUi(self)
        self.controller: Controller = controller
        self._is_loading: bool = False
        self.is_closing: bool = False
        self.is_converting: bool = False

        self.init_gui()
        # set_stylesheet(self)
        self.widget_tensorrt_model.set_parent(self)
        self.widget_metadata.signal_inject_metadata.connect(self.event_inject_metadata)
        self.widget_conversion.set_main_window(self)

        # Signals from the backend
        self.controller.signal_model_parsed.connect(self.event_model_parsed)
        self.controller.signal_task_ended.connect(self.event_task_ended)

        # Other events
        self.installEventFilter(self)

        # Drop model in the windo, whatever the position
        self.setAcceptDrops(True)

        self._thread = QThread()
        self.controller.moveToThread(self._thread)
        self._thread.start()



    def init_gui(self):
        # Put here all initialization settings fro each widget.
        # so that it will be easier for refactoring
        self.widget_model_browser.set_parent_widget(self)

        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()

        self.button_convert.clicked.connect(self.event_convert)


    def apply_user_preferences(self, user_preferences: UserPreferences):
        try:
            w: list[int] = user_preferences.settings['window']['geometry']
            self.setGeometry(*w)
        except:
            pass
        self.widget_conversion.apply_user_preferences(user_preferences)
        self.show()


    def get_user_preferences(self) -> dict:
        preferences = {
            'window': {
                'screen': 0,
                'geometry': self.geometry().getRect()
            },
            'user': {},
        }
        return preferences


    def closeEvent(self, event: QCloseEvent):
        self.close_event()
        super().closeEvent(event)


    def close_event(self):
        if not self.is_closing:
            self.is_closing = True
            self.controller.exit()
            self.close_all_widgets()
            self._thread.quit()
            self._thread.wait()


    def close_all_widgets(self):
        for widget in QApplication.topLevelWidgets():
            widget.close()
        self.close()


    def dropEvent(self, event: QDropEvent):
        if self._is_loading:
            return
        model_fp: str = absolute_path(event.mimeData().urls()[0].toLocalFile())
        self.widget_model_browser.combobox_model_fp.clear()
        self.widget_model_browser.combobox_model_fp.setCurrentText(model_fp)
        self.model_loaded_event(model_fp=model_fp)


    def dragEnterEvent(self, event: QDragEnterEvent):
        if self._is_loading:
            return

        is_allowed: bool = False
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                extension = get_extension(absolute_path(urls[0].toLocalFile()))
                if extension in SUPPORTED_MODEL_EXTENSIONS:
                    event.acceptProposedAction()
                    is_allowed = True

            event.setDropAction(Qt.DropAction.MoveAction)
        if not is_allowed:
            print("Oh noooo!!!")


    def model_loaded_event(self, model_fp: str) -> None:
        self._is_loading = True
        self.setEnabled(False)
        self.signal_model_loaded.emit(model_fp)


    def adjust_height(self) -> None:
        print(f"Adjust height")
        self.setMaximumHeight(4096)
        w = self.geometry().width()
        self.centralWidget().adjustSize()
        self.adjustSize()
        x, y, _, h = self.geometry().getRect()
        self.setGeometry(x, y, w, h)
        self.setMaximumHeight(h)



    def get_conversion_settings(self) -> dict:
        return {}


    def event_convert(self) -> None:
        # Can be either start or cancel
        if not self.is_converting:
            self.is_converting = True
            self.widget_conversion.started(False)
            self.button_convert.setEnabled(False)
            conversion_values: dict[str, dict[str, Any]] = self.widget_conversion.settings()
            self.signal_convert_action.emit(conversion_values)
            print("start converting")
            pprint(conversion_values)

            # remove this once backend send ack
            self.button_convert.setText("Cancel")
            self.button_convert.setEnabled(True)

        else:
            self.widget_conversion.started(True)
            self.signal_convert_action.emit("stop")

            # remove this once backend send ack
            self.button_convert.setText("Convert")
            self.button_convert.setEnabled(True)
            self.is_converting = False


    def event_convert_state_changed(self, status: dict) -> None:
        # status: dict(
        #   'state': Literal['stopped', 'running'],
        #   'type': Literal['progress', 'undetermined'],
        #   'progress': int,
        # )
        if status['state'] == 'stopped':
            self.button_convert.setText("Convert")
            self.button_convert.setEnabled(True)

        elif status['state'] == 'running':
            self.button_convert.setText("Cancel")
            self.button_convert.setEnabled(True)



    def refresh_model_info(self, model: NnModel) -> None:
        self.widget_pytorch_model.refresh_model_info(model)
        if model is None:
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.hide()

        elif model.framework.type == NnFrameworkType.PYTORCH:
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.hide()

        elif model.framework.type == NnFrameworkType.ONNX:
            self.widget_onnx_model.show()
            self.widget_tensorrt_model.hide()

        if model.framework.type == NnFrameworkType.TENSORRT:
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.show()

        self.widget_onnx_model.refresh_model_info(model)
        self.widget_tensorrt_model.refresh_model_info(model)
        self.widget_metadata.refresh_model_info(model)


    def event_model_parsed(self, model_fp: str) -> None:
        self._is_loading = False
        self.widget_model_browser.update_model_fp(model_fp=model_fp)
        model: NnModel = self.controller.get_in_model_info()

        self.setEnabled(True)
        self.refresh_model_info(model=model)
        self.widget_conversion.refresh_conversion_selection(model=model)
        self.adjust_height()


    def event_inject_metadata(self, metadata: dict[str, str]) -> None:
        model: NnModel = self.controller.get_in_model_info()
        model_fp: str | None = inject_metadata_dialog(self, model_fp=model.filepath)
        if model_fp is not None:
            self.progress.show()
            self.progress.setRange(0, 0)
            self.progress.setValue(0)

            self.setEnabled(False)
            print("Injection started")
            self.signal_inject_metadata.emit({
                'filepath': model_fp,
                'metadata': metadata
            })


    def event_task_ended(self, exception: str | None) -> None:
        print("Injection ended")
        # self.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()

        self.setEnabled(True)
        self.widget_metadata.injection_done()

        if exception is not None and exception:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save model.\n{exception}",
                QMessageBox.StandardButton.Ok
            )

