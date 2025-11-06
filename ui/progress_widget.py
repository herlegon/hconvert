from __future__ import annotations
import os
import sys
from hutils import (
    parent_directory,
    yellow,
)
from hwidgets import HStyle
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .main_window import MainWindow
from .logger import alog

from PySide6.QtCore import (
    QTimer,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QMessageBox,
)
from .designer.ui_progress_widget import Ui_ProgressWidget



class ProgressWidget(QWidget, Ui_ProgressWidget):
    signal_start_stop_clicked = Signal(str)

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self.progress_bar = self.h_indeterminate_progress
        self.gpu_usage = self.h_radial_progress_bar_gpu
        self.gpu_usage.setFixedSize(64, 64)


        self._main_window: MainWindow = None
        self.progress_bar.setVisible(True)
        self.set_visible(False)
        self.is_converting: bool = False
        self.out_model_fp: str = ""

        self.original_stylesheet = self.label_save_as.styleSheet()
        self.end_stylesheet = self.original_stylesheet + "\nQLabel { color: green; }"

        self.button_convert.released.connect(self.event_convert_button_clicked)
        self.button_containing_folder.released.connect(self.event_open_containing_folder)


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def adjust_height(self) -> None:
        if self.progress_bar.isVisible():
            self.blockSignals(True)
            alog.debug(yellow("adjust_weight"))
            self.updateGeometry()
            self.adjustSize()
            self.blockSignals(False)
            QTimer.singleShot(0, self._main_window.adjust_height)


    def set_visible(self, b: bool) -> None:
        alog.debug(f"set progress widget visible: {b}")
        self.gpu_usage.setVisible(b)
        self.label_save_as.setVisible(b)
        self.lineEdit_out_model_fp.setVisible(b)
        self.button_containing_folder.setVisible(b)
        # self.progress_bar.setValue(0)
        if b:
            self._main_window.reset_widget_monitor()
        if b and self.progress_bar.isVisible() != b:
            self.adjust_height()
        self.progress_bar.setVisible(b)
        self.updateGeometry()
        self.adjustSize()


    def is_visible(self) -> bool:
        # Use a single widget to reduce complexity
        return self.lineEdit_out_model_fp.isVisible()


    def hide_progress(self) -> None:
        if self.lineEdit_out_model_fp.isVisible():
            alog.debug(f"hide progress widget")
            self.button_convert.setText("Convert")
            self.button_convert.setEnabled(True)
            self.progress_bar.setEnabled(False)
            self.set_visible(False)


    def ended(self) -> None:
        alog.debug(f"{__class__.__name__} ended")
        # self.set_visible(True)
        if self.is_converting:
            self.progress_bar.stop()
            # self.button_convert.setText("Convert")
            # self.button_convert.setEnabled(True)
            self.is_converting = False
            self.label_save_as.setEnabled(True)
            self.label_save_as.setText("Saved as")
            self.label_save_as.setStyleSheet(self.end_stylesheet)
            self.lineEdit_out_model_fp.setEnabled(True)
            self.button_containing_folder.setEnabled(True)


    def stop(self) -> None:
        # Stop without showing progress/path/usage
        alog.error(f"{__class__.__name__} stop")
        self.set_visible(False)
        self.button_convert.setText("Convert")
        self.button_convert.setEnabled(True)
        self.progress_bar.setEnabled(False)
        self.is_converting = False
        self.label_save_as.setEnabled(False)
        self.label_save_as.setStyleSheet(self.original_stylesheet)
        self.lineEdit_out_model_fp.clear()
        self.lineEdit_out_model_fp.setEnabled(False)
        self.button_containing_folder.setEnabled(False)


    def event_convert_shortkey(self, action: Literal['start', 'stop']) -> None:
        if action == 'start' and not self.is_converting:
            self.event_convert_button_clicked()
        elif action =='stop' and self.is_converting:
            self.event_cancel_button_clicked()


    def event_cancel_button_clicked(self) -> None:
        self.button_convert.setEnabled(False)
        if self.is_converting:
            # Stop conversion
            alog.error(f"{__class__.__name__} event_cancel_button_clicked")
            state = 'stop'
            self.is_converting = False
            self.button_convert.setText("Convert")
            self.label_save_as.setStyleSheet(self.original_stylesheet)
            self.lineEdit_out_model_fp.clear()
            self.signal_start_stop_clicked.emit(state)


    def event_convert_button_clicked(self) -> None:
        if self.is_converting:
            self.event_cancel_button_clicked()
            return

        self.button_convert.setEnabled(False)
        state = 'start'
        self.is_converting = True
        self.button_convert.setText("Stop")
        self.label_save_as.setEnabled(False)
        self.label_save_as.setStyleSheet(self.original_stylesheet)
        self.lineEdit_out_model_fp.setEnabled(False)
        self.signal_start_stop_clicked.emit(state)


    def event_open_containing_folder(self):
        if self.out_model_fp:
            directory: str = parent_directory(self.out_model_fp)
            try:
                if sys.platform == "win32":
                    os.startfile(directory)
                elif sys.platform == "Darwin":
                    os.system(f'open "{directory}"')
                else:
                    os.system(f'xdg-open "{directory}"')
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open directory:\n{e}")


    def set_conversion_enabled(self, b: bool) -> None:
        alog.debug(f"set_conversion_enabled: {b}")
        self.button_convert.setEnabled(b)


    def event_progress(self, status: dict) -> None:
        # Called once the controller confirmed that the
        # conversion is running/stopped

        # status: dict(
        #   'state': Literal['stopped', 'running'],
        #   'type': Literal['progress', 'undetermined'],
        #   'progress': int,
        #   'cancelable': bool,
        #   'out_model_fp': str
        # )

        if 'state' not in status:
            alog.error(f"{__class__.__name__} Missing \'state\' ")
            return

        if status['state'] == 'cancelled' and self.is_converting:
            self.stop()

        elif status['state'] == 'ended' and self.is_converting:
            self.ended()
            self.progress_bar.setEnabled(False)

        elif status['state'] == 'running':
            self.button_convert.setText("Stop")

            if status['type'] == 'undetermined' and status['progress'] == 0:
                self.progress_bar.start()
                # self.progress_bar.setEnabled(True)
                self.progress_bar.setEnabled(False)

            if status['cancelable']:
                self.button_convert.setText("Stop")
                self.button_convert.setEnabled(True)
                self.progress_bar.setEnabled(False)

            else:
                self.button_convert.setText("Convert")
                self.button_convert.setEnabled(False)
                self.progress_bar.setEnabled(False)

            self.out_model_fp = status['out_model_fp']
            self.label_save_as.setText("Saving as")
            self.lineEdit_out_model_fp.setText(self.out_model_fp)
            self.lineEdit_out_model_fp.setToolTip(self.out_model_fp)

            self.set_visible(True)

        elif self.is_converting:
            alog.error(f"{__class__.__name__} unknown state: {status['state']} while converting")
