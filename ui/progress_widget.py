from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import (
    QTimer,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
)
from .designer.ui_progress_widget import Ui_ProgressWidget
if TYPE_CHECKING:
    from .main_window import MainWindow



class ProgressWidget(QWidget, Ui_ProgressWidget):
    signal_start_stop_clicked = Signal(str)

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setupUi(self)
        self._main_window: MainWindow = None
        self.progress_bar.setVisible(True)
        self.set_visible(False)
        self.is_converting: bool = False

        self.button_convert.released.connect(self.event_convert_button_clicked)


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def adjust_height(self) -> None:
        self.updateGeometry()
        self.adjustSize()
        QTimer.singleShot(0, self._main_window.adjust_height)


    def set_visible(self, b: bool) -> None:
        self.gpu_usage.setVisible(b)
        self.label.setVisible(b)
        self.lineEdit_out_model_fp.setVisible(b)
        self.button_containing_folder.setVisible(b)
        self.progress_bar.setValue(0)
        if b:
            self._main_window.reset_widget_monitor()
        if self.progress_bar.isVisible() != b:
            self.adjust_height()
            self._main_window.widget_conversion.adjust_height()
        self.progress_bar.setVisible(b)
        self.updateGeometry()
        self.adjustSize()


    def is_visible(self) -> bool:
        # Use a single widget to reduce complexity
        return self.lineEdit_out_model_fp.isVisible()


    def hide_progress(self) -> None:
        print("hide!!!!!!!")
        if self.lineEdit_out_model_fp.isVisible():
            self.button_convert.setText("Convert")
            self.button_convert.setEnabled(True)
            self.progress_bar.setEnabled(False)
            self.set_visible(False)


    def ended(self) -> None:
        self.set_visible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        # self.button_convert.setText("Convert")
        # self.button_convert.setEnabled(True)
        self.is_converting = False
        self.label.setEnabled(True)
        self.lineEdit_out_model_fp.setEnabled(True)
        self.button_containing_folder.setEnabled(True)


    def stop(self) -> None:
        # Stop without showing progress/path/usage
        self.set_visible(False)
        self.button_convert.setText("Convert")
        self.button_convert.setEnabled(True)
        self.progress_bar.setEnabled(False)
        self.is_converting = False
        self.label.setEnabled(False)
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
            state = 'stop'
            self.is_converting = False
            self.button_convert.setText("Convert")
            self.signal_start_stop_clicked.emit(state)


    def event_convert_button_clicked(self) -> None:
        if self.is_converting:
            self.event_cancel_button_clicked()
            return

        self.button_convert.setEnabled(False)
        state = 'start'
        self.is_converting = True
        self.button_convert.setText("Stop")
        self.label.setEnabled(False)
        self.lineEdit_out_model_fp.setEnabled(False)
        self.signal_start_stop_clicked.emit(state)


    def set_conversion_enabled(self, b: bool) -> None:
        self.button_convert.setEnabled(b)


    def event_progress(self, status: dict) -> None:
        # Called once the controller confirmed that the
        # conversion is running/stopped

        # status: dict(
        #   'state': Literal['stopped', 'running'],
        #   'type': Literal['progress', 'undetermined'],
        #   'progress': int,
        #   'cancelable': bool,
        # )

        if status['state'] == 'cancelled' and self.is_converting:
            self.stop()

        elif status['state'] == 'ended' and self.is_converting:
            self.ended()
            self.progress_bar.setEnabled(False)

        elif status['state'] == 'running':
            self.button_convert.setText("Stop")
            self.set_visible(True)
            if status['type'] == 'undetermined' and status['progress'] == 0:
                self.progress_bar.setRange(0, 0)
                self.progress_bar.setValue(0)
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
