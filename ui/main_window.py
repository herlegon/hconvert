from __future__ import annotations
from argparse import Namespace
from functools import partial
import os
from pprint import pprint
from typing import Any, Literal, Type
from hwidgets import HStyle, HVerticalDivider
from .pynnlib_api import (
    NnFrameworkType,
    NnModel,
)
from hytils import (
    absolute_path,
    get_extension,
    lightcyan,
    red,
)

from .common import SUPPORTED_MODEL_EXTENSIONS
from .user_settings import UserSettings
from .widget_monitor import WidgetMonitor
from .inject_metadata_dialog import inject_metadata_dialog
from .designer.ui_main_window import Ui_MainWindow
from .controller import Controller
from PySide6.QtCore import (
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
    QRect,
)
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QCursor,
    QDragEnterEvent,
    QDropEvent,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QMainWindow,
    QMessageBox,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy
)
from .logger import alog

from ui.header_widget import HeaderWidget
from ui.log_widget import LogWidget
from ui.model_browser_widget import ModelBrowserWidget
from ui.conversion_widget import ConversionWidget
from ui.metadata_widget import MetadataWidget
from ui.onnx_widget import OnnxWidget
from ui.progress_widget import ProgressWidget
from ui.pytorch_widget import PyTorchWidget
from ui.tensorrt_widget import TensorRTWidget

DEBUG_HEIGHT: bool = False


class MainWindow(QMainWindow):
    signal_preview_modified = Signal(dict)
    signal_convert_action = Signal(dict)
    signal_stop_action = Signal()
    signal_model_selected = Signal(str)
    signal_inject_metadata = Signal(dict)


    def __init__(self, args: Namespace):
        super().__init__()
        hrl_style = HStyle()
        self.setupUi(hrl_style)

        self.setStyleSheet(f"""
            background-color: {hrl_style.window_bgd};
            color: {hrl_style.text_color};
        """)

        # self.h_vertical_divider.set_line_color(hrl_style.widget_bgd)

        self.widget_model_browser.set_main_window(self)
        self.widget_tensorrt_model.set_main_window(self)
        self.widget_conversion.set_main_window(self)
        if self.widget_progress:
            self.widget_progress.set_main_window(self)
        self.event_log_visibility_changed(False)

        self.setAcceptDrops(True)

        self.user_settings: UserSettings = UserSettings()

        self._is_loading: bool = False
        self.is_closing: bool = False

        self.dev_mode: bool = False
        if args.dev:
            self.dev_mode = True

        self.initial_model: str = ""
        if args.model:
            self.initial_model = args.model


        monitored_widgets: list[Type[QWidget]] = [
            widget
            for w in (
                self.widget_model_browser,
                self.widget_conversion,
                self.widget_metadata
            )
            for widget in w.editable_widgets()
        ]
        if self.widget_progress:
            self.widget_monitor = WidgetMonitor(
                monitored_widgets, self.widget_progress.hide_progress
            )

        self.widget_model_browser.signal_model_selected.connect(self.event_model_selected)
        self.widget_metadata.signal_inject_metadata.connect(self.event_inject_metadata)
        if self.widget_progress:
            self.widget_progress.signal_start_stop_clicked.connect(self.event_convert)

        self.widget_conversion.signal_settings_modified.connect(
            self.event_conversion_settings_modified
        )

        self.widget_header.signal_visibility_changed.connect(
            self.event_log_visibility_changed
        )

        self.action_open: QAction
        self.set_keyboard_shorcuts()

        self.setEnabled(False)

        # Controller
        self.controller = Controller(view=self, args=args)
        self.controller_thread = QThread()
        self.controller.moveToThread(self.controller_thread)
        self.controller_thread.setObjectName("ControllerThread")
        self.controller_thread.start()

        # Signals from the controller
        self.controller.signal_model_parsed.connect(self.event_model_parsed)
        self.controller.signal_task_ended.connect(self.event_task_ended)
        self.controller.signal_progress.connect(self.event_progress)
        self.controller.signal_backend_status.connect(self.on_backend_status)

        # Connect signals
        # controller.signal_progress.connect(update_progress_bar)
        # controller.signal_system_usage.connect(update_telemetry)
        # controller.signal_log.connect(print_log)

        self.controller.start_backend(
            absolute_path(os.path.join(__file__, os.pardir, os.pardir, "backend", "server.py")),
            dev_mode=self.dev_mode,
        )

        # Start the Thread
        self.controller.start()

        self.apply_user_settings()
        # set_stylesheet(self)



    def setupUi(self, hstyle: HStyle) -> None:

        self.FIXED_LOG_WIDTH = 500

        # Main widget and layout
        main_widget = QWidget()
        main_widget.setObjectName("main_widget")
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setSpacing(24)
        self.main_layout.setContentsMargins(12, 12, 12, 12)


        self.widget_header = HeaderWidget(main_widget)
        self.widget_header.setObjectName("widget_header")
        self.widget_header.setFixedHeight(32)
        self.widget_header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.widget_model_browser = ModelBrowserWidget(main_widget)
        self.widget_model_browser.setObjectName("widget_model_browser")
        self.widget_model_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.widget_pytorch_model = PyTorchWidget(main_widget)
        self.widget_pytorch_model.setObjectName("widget_pytorch_model")
        self.widget_pytorch_model.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.widget_onnx_model = OnnxWidget(main_widget)
        self.widget_onnx_model.setObjectName("widget_onnx_model")
        self.widget_onnx_model.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.widget_tensorrt_model = TensorRTWidget(main_widget)
        self.widget_tensorrt_model.setObjectName("widget_tensorrt_model")
        self.widget_tensorrt_model.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        self.widget_metadata = MetadataWidget(main_widget)
        self.widget_metadata.setObjectName("widget_metadata")
        self.widget_metadata.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.widget_conversion = ConversionWidget(main_widget)
        self.widget_conversion.setObjectName("widget_conversion")
        self.widget_conversion.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        self.widget_log = LogWidget(main_widget)
        self.widget_progress = None
        # self.widget_progress = ProgressWidget(main_widget)


        # Left section (all widgets except log)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        left_layout.addWidget(self.widget_header)
        left_layout.addWidget(self.widget_model_browser)


        # Bottom section with grid layout
        bottom_widget = QWidget()
        self.grid_layout = QGridLayout(bottom_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(12)

        # Left column: model widgets (width calculated from content)
        column = 0
        self.models_widget = QWidget()
        models_layout = QVBoxLayout(self.models_widget)
        models_layout.setContentsMargins(0, 0, 0, 0)
        models_layout.setSpacing(12)

        models_layout.addWidget(self.widget_pytorch_model, alignment=Qt.AlignmentFlag.AlignTop)
        models_layout.addWidget(self.widget_onnx_model, alignment=Qt.AlignmentFlag.AlignTop)
        models_layout.addWidget(self.widget_tensorrt_model, alignment=Qt.AlignmentFlag.AlignTop)
        # models_layout.addStretch()

        # Calculate maximum width of model widgets
        QApplication.processEvents()
        max_width = max(
            self.widget_pytorch_model.sizeHint().width(),
            self.widget_onnx_model.sizeHint().width(),
            self.widget_tensorrt_model.sizeHint().width()
        )
        self.models_widget.setFixedWidth(max_width)

        self.grid_layout.addWidget(self.models_widget, 0, column, 2, 1, Qt.AlignmentFlag.AlignTop)

        # Add a divider to grid layout in column 1 (between 0 and 1)
        column = 1
        self.h_vertical_divider = HVerticalDivider(main_widget, hstyle=hstyle)
        self.h_vertical_divider.setObjectName(u"h_vertical_divider")
        self.h_vertical_divider.setFrameShadow(QFrame.Shadow.Plain)
        self.h_vertical_divider.setFrameShape(QFrame.Shape.VLine)
        self.grid_layout.addWidget(self.h_vertical_divider, 0, column, 2, 1)

        # Right column
        column = 2
        # metadata
        self.grid_layout.addWidget(self.widget_metadata, 0, column, Qt.AlignmentFlag.AlignTop)
        self.grid_layout.setVerticalSpacing(48)

        # conversion
        self.conversion_container = QWidget()
        self.conversion_layout = QVBoxLayout(self.conversion_container)
        self.conversion_layout.setContentsMargins(0, 0, 0, 0)
        self.conversion_layout.setSpacing(0)
        self.conversion_layout.addWidget(self.widget_conversion)
        self.conversion_layout.addStretch()

        self.conversion_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,  # Use Minimum instead of Maximum
        )
        self.grid_layout.addWidget(self.conversion_container, 1, column, Qt.AlignmentFlag.AlignTop)

        # Set column stretch
        self.grid_layout.setColumnStretch(0, 0)  # Fixed width column
        self.grid_layout.setColumnStretch(1, 1)  # Expandable column

        left_layout.addWidget(bottom_widget, 1)

        self.main_layout.addWidget(left_widget, 1)

        self.h_vertical_divider_log = HVerticalDivider(main_widget, hstyle=hstyle)
        self.h_vertical_divider_log.setObjectName(u"h_vertical_divider_log")
        self.widget_log.setFixedWidth(self.FIXED_LOG_WIDTH)
        self.widget_log.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.h_vertical_divider_log)
        self.main_layout.addWidget(self.widget_log)


    def save_user_settings(self) -> None:
        window_width = self.width()
        if self.widget_log.isVisible():
            log_width = (
                self.widget_log.width()
                + 2 * self.main_layout.spacing()
                + self.h_vertical_divider_log.width()
            )
            window_width -= log_width

        x, y, _, h = list(self.geometry().getRect())

        user_settings: dict[str, Any] = {
            'window': {
                'screen': 0,
                'geometry': [x, y, window_width, h]
            },
            'user': {
                **self.widget_model_browser.get_user_settings(),
                **self.widget_conversion.get_user_settings(),
                **self.widget_conversion.widget_select_out_dir.get_user_settings(),
            },
        }

        self.user_settings.save(user_settings)


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

        # Hide log
        self.widget_header.block_signals(True)
        self.widget_header.h_button_log.setChecked(False)
        self.widget_header.block_signals(False)
        self.widget_log.hide()
        self.h_vertical_divider_log.hide()

        # Send to other widgets
        user_settings = settings.get('user', {})
        for w in (
            self.widget_model_browser,
            self.widget_conversion,
            self.widget_conversion.widget_select_out_dir,
        ):
            w.apply_user_settings(user_settings)

        # Hide all widgets until model loaded
        self.refresh_model_info(model=None)

        alog.debug("apply user settings: geometry")
        alog.debug(f"  torch: {self.widget_pytorch_model.geometry().width()}")
        alog.debug(f"  onnx: {self.widget_onnx_model.geometry().width()}")
        alog.debug(f"  tensorrt: {self.widget_tensorrt_model.geometry().width()}")
        self.show()
        self.widget_conversion.adjust_height()
        self.adjust_height()


    def closeEvent(self, event: QCloseEvent):
        self.save_user_settings()
        if not self.is_closing:
            self.is_closing = True
            self.controller.shutdown()
            self.controller_thread.quit()
            self.controller_thread.wait()
            # self.close_all_widgets()
        super().closeEvent(event)


    def close_all_widgets(self):
        for widget in QApplication.topLevelWidgets():
            widget.close()
        self.close()


    def event_log_visibility_changed(self, b: bool) -> None:
        window_width = self.width()
        log_width = (
            self.widget_log.width()
            + 2 * self.main_layout.spacing()
            + self.h_vertical_divider_log.width()
        )
        was_visible: bool = self.widget_log.isVisible()

        self.blockSignals(True)
        if not was_visible and b:
            new_width = window_width + log_width
            self.widget_log.show()
            self.h_vertical_divider_log.show()
            self.resize(new_width, self.height())

        elif was_visible and not b:
            new_width = window_width - log_width
            self.h_vertical_divider_log.hide()
            self.widget_log.hide()
            self.resize(new_width, self.height())

            self.setMaximumWidth(window_width - log_width)
            QTimer.singleShot(0, self.adjust_size_after_log_hide)

        self.blockSignals(False)


    def adjust_size_after_log_hide(self):
        self.main_layout.update()
        self.adjustSize()
        self.setMaximumWidth(65535)


    def event_open(self):
        alog.debug("open")


    def set_keyboard_shorcuts(self):
        # On macOS Ctrl vs Meta differences: Meta (⌘)

        self.action_open = QAction("Open", self)
        self.action_open.setShortcut(QKeySequence("Ctrl+O"))
        self.action_open.triggered.connect(self.widget_model_browser.button_browse.click)
        self.addAction(self.action_open)

        self.action_save_metadata = QAction("Save Metadata", self)
        self.action_save_metadata.setShortcut(QKeySequence("Ctrl+s"))
        self.action_save_metadata.triggered.connect(self.widget_metadata.button_save_as.click)
        self.addAction(self.action_save_metadata)

        self.action_undo_metadata = QAction("Undo Metadata", self)
        self.action_undo_metadata.setShortcut(QKeySequence("Ctrl+z"))
        self.action_undo_metadata.triggered.connect(self.widget_metadata.button_cancel.click)
        self.addAction(self.action_undo_metadata)

        self.shortcut_safetensors = QShortcut(QKeySequence("S"), self)
        self.shortcut_safetensors.activated.connect(
            partial(self.widget_conversion.select, 'safetensors')
        )

        self.shortcut_onnx = QShortcut(QKeySequence("O"), self)
        self.shortcut_onnx.activated.connect(
            partial(self.widget_conversion.select, 'onnx')
        )

        self.shortcut_tensorrt = QShortcut(QKeySequence("T"), self)
        self.shortcut_tensorrt.activated.connect(
            partial(self.widget_conversion.select, 'tensorrt')
        )

        if self.widget_progress:
            self.shortcut_start_conversion = QShortcut(QKeySequence("F5"), self)
            self.shortcut_start_conversion.activated.connect(
                partial(self.widget_progress.event_convert_shortkey, 'start')
            )

            self.shortcut_cancel_conversion = QShortcut(QKeySequence("F6"), self)
            self.shortcut_cancel_conversion.activated.connect(
                partial(self.widget_progress.event_convert_shortkey, 'stop')
            )


    def adjust_height(self) -> None:
        current_width = self.width()
        if DEBUG_HEIGHT:
            alog.debug(f"adjust height; current width = {current_width}")
            alog.debug(f"   conversion widget height: {self.widget_conversion.height()}")
            alog.debug(f"   container widget height: {self.conversion_container.height()}")

        # Reset height constraints first
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)

        # Force the container to update its size
        self.conversion_container.adjustSize()
        self.conversion_container.updateGeometry()

        # CRITICAL: Invalidate the grid layout
        if self.grid_layout:
            self.grid_layout.invalidate()
            self.grid_layout.activate()

        # Force layout recalculation from bottom up
        self.centralWidget().adjustSize()
        self.centralWidget().updateGeometry()

        # Process events to ensure layouts are updated
        QApplication.processEvents()

        if DEBUG_HEIGHT:
            alog.debug(f"   -> container widget height: {self.conversion_container.height()}")

            # Debug all widget heights
            alog.debug(f"   Header: {self.widget_header.minimumSizeHint().height()}")
            alog.debug(f"   Model Browser: {self.widget_model_browser.minimumSizeHint().height()}")
            alog.debug(f"   Models Widget: {self.models_widget.minimumSizeHint().height()}")
            alog.debug(f"   Metadata: {self.widget_metadata.minimumSizeHint().height()}")
            alog.debug(f"   Conversion Container: {self.conversion_container.minimumSizeHint().height()}")
            alog.debug(f"   Log Widget: {self.widget_log.minimumSizeHint().height()}")
            alog.debug(f"   Central Widget minimumSizeHint: {self.centralWidget().minimumSizeHint().height()}")
            alog.debug(f"   Central Widget sizeHint: {self.centralWidget().sizeHint().height()}")

        # Get the minimum size needed for content
        content_size = self.centralWidget().minimumSizeHint()  # Use minimumSizeHint instead of sizeHint

        # Account for window frame and margins
        new_height = content_size.height() + self.menuBar().height()

        self.blockSignals(True)

        if DEBUG_HEIGHT:
            alog.debug(f"set new height: {new_height}")

        # Set fixed height
        self.setFixedHeight(new_height)
        self.resize(current_width, new_height)
        self.blockSignals(False)

        if DEBUG_HEIGHT:
            alog.debug(f"   ** container widget height: {self.conversion_container.height()}")



    def refresh_model_info(self, model: NnModel) -> None:
        alog.debug(
            f"refresh model info: {'none' if model is None else model.framework.type}"
        )
        if model is None:
            self.widget_pytorch_model.hide()
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.hide()

        elif model.framework.type == NnFrameworkType.PYTORCH:
            self.widget_pytorch_model.show()
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.hide()

        elif model.framework.type == NnFrameworkType.ONNX:
            self.widget_pytorch_model.show()
            self.widget_onnx_model.show()
            self.widget_tensorrt_model.hide()

        elif model.framework.type == NnFrameworkType.TENSORRT:
            self.widget_pytorch_model.show()
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.show()

        else:
            alog.error(f"{model.framework.type} is not a supported framework")
            model = None
            self.widget_pytorch_model.hide()
            self.widget_onnx_model.hide()
            self.widget_tensorrt_model.hide()

        self.widget_pytorch_model.refresh_model_info(model)
        self.widget_onnx_model.refresh_model_info(model)
        self.widget_tensorrt_model.refresh_model_info(model)
        self.widget_metadata.refresh_model_info(model)
        self.widget_conversion.refresh_conversion_selection(model=model)
        if self.widget_progress:
            self.widget_progress.setVisible(bool(model is not None))
        # self.h_vertical_divider.setVisible(bool(model is not None))


    def event_model_selected(self, model_fp: str) -> None:
        alog.debug(f"selected: {model_fp}")
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
        if self.widget_progress:
            self.widget_progress.set_visible(False)
        self.widget_model_browser.set_filepath(model_fp=model_fp)
        self.signal_model_selected.emit(model_fp)


    def event_model_parsed(self, model_fp: str) -> None:
        alog.debug("Model has been parsed")
        QApplication.restoreOverrideCursor()
        self._is_loading = False
        model: NnModel = self.controller.get_in_model_info()

        self.refresh_model_info(model=model)
        self.widget_model_browser.update_model_fp(
            filepath=model_fp,
            is_valid=bool(model is not None),
        )
        self.setEnabled(True)

        if model is not None and self.widget_progress:
            if model.framework.type == NnFrameworkType.TENSORRT:
                self.widget_progress.set_conversion_enabled(False)
            else:
                self.widget_progress.set_conversion_enabled(True)
        self.adjust_height()
        alog.debug("model parsed, window updated")


    def event_inject_metadata(self, metadata: dict[str, str]) -> None:
        model: NnModel = self.controller.get_in_model_info()
        model_fp: str | None = inject_metadata_dialog(self, model_fp=model.filepath)
        if model_fp is not None:
            self.setEnabled(False)
            alog.debug("Injection started")
            self.signal_inject_metadata.emit({
                'filepath': model_fp,
                'metadata': metadata
            })
        else:
            self.widget_metadata.set_enabled(True)


    def reset_widget_monitor(self) -> None:
        self.widget_monitor.reset()


    @Slot(dict)
    def event_progress(self, status: dict) -> None:
        alog.debug(f"signal_progress: {status}")
        # status: dict(
        #   'state': Literal['stopped', 'running'],
        #   'type': Literal['progress', 'undetermined'],
        #   'progress': int,
        #   'cancelable': bool,
        #   'out_model_fp': str,
        # )
        if self.widget_progress:
            self.widget_progress.event_progress(status=status)
        if 'state' not in status:
            return

        if status['state'] != 'running':
            self.widget_model_browser.setEnabled(True)


    def event_task_ended(self, exception: str | None) -> None:
        alog.debug("received signal_task_ended")
        # self.setEnabled(True)
        self.widget_conversion.setEnabled(True)
        self.widget_metadata.setEnabled(True)
        self.widget_metadata.injection_done()

        if self.widget_progress:
            if exception is not None and exception:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to save model.\n{exception}",
                    QMessageBox.StandardButton.Ok
                )
                self.widget_progress.stop()
            else:
                self.widget_progress.ended()
                self.widget_conversion.widget_select_out_dir.conversion_ended()


    def event_convert(self, state: str) -> None:
        # Can be either start or cancel
        if state == 'start':
            conversion_settings: dict[str, dict[str, Any]] = self.widget_conversion.settings()
            if conversion_settings is None:
                self.widget_progress.stop()
                return
            # self.button_convert.setEnabled(False)
            conversion_settings.update({
                'metadata': self.widget_metadata.values()
            })
            alog.debug("start converting")

            self.widget_conversion.setEnabled(False)
            self.widget_metadata.setEnabled(False)
            self.widget_model_browser.setEnabled(False)
            self.signal_convert_action.emit(conversion_settings)

        else:
            self.signal_stop_action.emit()
            self.widget_progress.stop()
            self.widget_model_browser.setEnabled(True)
            self.widget_conversion.setEnabled(True)
            self.widget_metadata.setEnabled(True)


    def event_conversion_settings_modified(self) -> None:
        alog.debug("signal received: modified settings")
        if self.widget_progress:
            self.widget_progress.ended()
            self.widget_progress.hide_progress()
        self.widget_conversion.setEnabled(True)


    def dropEvent(self, event: QDropEvent):
        if self._is_loading:
            return
        model_fp: str = absolute_path(event.mimeData().urls()[0].toLocalFile())
        self.widget_model_browser.set_filepath(model_fp=model_fp)
        self.event_model_selected(model_fp=model_fp)


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
            alog.warning("Oh noooo!!!")


    # @Slot(str)
    def on_backend_status(self, status: Literal['running', 'stopped']) -> None:
        if status == 'running':
            if not self.isEnabled():
                self.setEnabled(True)

            if  self.initial_model:
                self.event_model_selected(self.initial_model)
                self.initial_model = ""

        elif status == 'stopped':
            if self.dev_mode:
                self.controller.retry_connect()

            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Backend Offline")
                msg.setText("The backend is not reachable.")
                msg.setInformativeText("Do you want to restart it or quit the application?")
                retry_btn = msg.addButton("Retry", QMessageBox.ButtonRole.AcceptRole)
                quit_btn = msg.addButton("Quit", QMessageBox.ButtonRole.RejectRole)
                msg.setDefaultButton(retry_btn)
                msg.exec()

                if msg.clickedButton() == retry_btn:
                    self.controller.retry_connect()
                else:
                    self.close()

        else:
            alog.error(f"unknow backend status: \'{status}\'")
