from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, Any
from backend.path_utils import absolute_path, get_extension
from pynnlib import (
    NnModel,
    NnFrameworkType,
)
from pynnlib.utils.p_print import *

from .user_settings import UserSettings
from .common import SUPPORTED_MODEL_EXTENSIONS
from .inject_metadata_dialog import inject_metadata_dialog
from .designer.ui_main_window import Ui_MainWindow
if TYPE_CHECKING:
    from backend.controller import Controller
from PySide6.QtCore import (
    Signal,
    QThread,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QCloseEvent,
    QCursor,
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
)


class MainWindow(QMainWindow, Ui_MainWindow):
    signal_preview_modified = Signal(dict)
    signal_convert_action = Signal(dict)
    signal_cancel_action = Signal()
    signal_model_loaded = Signal(str)
    signal_inject_metadata = Signal(dict)


    def __init__(self, controller: Controller):
        super().__init__()
        self.setupUi(self)
        self.controller: Controller = controller
        self.user_settings: UserSettings = UserSettings()

        self._is_loading: bool = False
        self.is_closing: bool = False
        self.is_converting: bool = False

        self.init_gui()
        # set_stylesheet(self)
        self.widget_model_browser.set_main_window(self)
        self.widget_tensorrt_model.set_main_window(self)
        self.widget_conversion.set_main_window(self)

        self.widget_model_browser.signal_model_loaded.connect(self.event_model_loaded)
        self.widget_metadata.signal_inject_metadata.connect(self.event_inject_metadata)

        # Signals from the backend
        self.controller.signal_model_parsed.connect(self.event_model_parsed)
        self.controller.signal_task_ended.connect(self.event_task_ended)

        # Drop model in the windo, whatever the position
        self.setAcceptDrops(True)

        self.apply_user_settings()

        self._thread = QThread()
        self.controller.moveToThread(self._thread)
        self._thread.start()



    def init_gui(self):
        # Put here all initialization settings fro each widget.
        # so that it will be easier for refactoring
        self.button_convert.clicked.connect(self.event_convert)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()


    def apply_user_settings(self):
        settings: dict[str, Any] = self.user_settings.settings
        try:
            w: list[int] = settings['window']['geometry']
            self.setGeometry(*w)
        except:
            primary_screen = QApplication.screens()[0]
            screen_width = primary_screen.size().width()
            screen_height = primary_screen.size().height()
            self.setGeometry(50, 50, screen_width - 200, screen_height - 100)
            self.adjustSize()

        user_settings = settings.get('user', {})
        for w in (
            self.widget_model_browser,
            self.widget_conversion,
            self.widget_conversion.widget_select_out_dir,
        ):
            w.apply_user_settings(user_settings)
        self.show()
        self.widget_conversion.adjust_height()
        self.adjust_height()


    def save_user_settings(self) -> None:
        user_settings: dict[str, Any] = {
            'window': {
                'screen': 0,
                'geometry': list(self.geometry().getRect())
            },
            'user': {
                **self.widget_model_browser.get_user_settings(),
                **self.widget_conversion.get_user_settings(),
                **self.widget_conversion.widget_select_out_dir.get_user_settings(),
            },
        }

        self.user_settings.save(user_settings)


    def closeEvent(self, event: QCloseEvent):
        self.save_user_settings()
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


    def set_min_max_width(self):
        self.setMinimumWidth(0)
        self.setMaximumWidth(2000)


    def adjust_height(self) -> None:
        current_width = self.width()

        self.setMinimumSize(0, 0)
        self.centralWidget().adjustSize()
        content_size = self.centralWidget().sizeHint()

        # Account for window frame and margins
        new_height = content_size.height() + self.menuBar().height()
        self.setMinimumHeight(new_height)

        # Resize window to minimum height, keeping width unchanged
        self.resize(current_width, new_height)
        self.setFixedHeight(new_height)

        QTimer.singleShot(100, lambda: self.set_min_max_width)



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


    def event_model_loaded(self, model_fp: str) -> None:
        self._is_loading = True
        self.setEnabled(False)
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        for w in (
            self.widget_pytorch_model,
            self.widget_onnx_model,
            self.widget_tensorrt_model,
            self.widget_metadata,
        ):
            w.clear()
        self.signal_model_loaded.emit(model_fp)


    def event_model_parsed(self, model_fp: str) -> None:
        QApplication.restoreOverrideCursor()
        self._is_loading = False
        self.widget_model_browser.update_model_fp(filepath=model_fp)
        model: NnModel = self.controller.get_in_model_info()

        self.setEnabled(True)
        self.refresh_model_info(model=model)
        self.widget_conversion.refresh_conversion_selection(model=model)
        # self.adjust_height()


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
        else:
            self.widget_conversion.widget_select_out_dir.conversion_ended()


    def event_convert(self) -> None:
        # Can be either start or cancel
        if not self.is_converting:
            conversion_settings: dict[str, dict[str, Any]] = self.widget_conversion.settings()
            if conversion_settings is None:
                return
            self.button_convert.setEnabled(False)
            conversion_settings.update({
                'metadata': self.widget_metadata.values()
            })
            print("start converting")
            pprint(conversion_settings)
            self.is_converting = True
            self.widget_conversion.started(False)
            self.button_convert.setEnabled(False)

            # remove this once backend send ack
            self.button_convert.setText("Cancel")


            self.progress.show()
            self.progress.setRange(0, 0)
            self.progress.setValue(0)

            self.setEnabled(False)

            self.signal_convert_action.emit(conversion_settings)
            self.button_convert.setEnabled(True)


        else:
            self.signal_cancel_action.emit()
            self.widget_conversion.started(True)

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




    def dropEvent(self, event: QDropEvent):
        if self._is_loading:
            return
        model_fp: str = absolute_path(event.mimeData().urls()[0].toLocalFile())
        self.widget_model_browser.set_filepath(model_fp=model_fp)
        self.event_model_loaded(model_fp=model_fp)


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
