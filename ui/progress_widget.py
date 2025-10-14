from __future__ import annotations
from functools import partial
from pprint import pprint
from typing import Any, Literal, TYPE_CHECKING
from .user_settings import UserSettings
from pynnlib import (
    NnModel,
    NnFrameworkType,
)
from pynnlib.utils.p_print import *

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QSizePolicy,
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
        self.set_visible(False)
        self.is_converting: bool = False

        self.button_convert.released.connect(self.event_convert_button_clicked)


    def set_visible(self, b: bool) -> None:
        self.gpu_usage.setVisible(b)
        self.label.setVisible(b)
        self.lineEdit_out_model_fp.setVisible(b)
        self.button_containing_folder.setVisible(b)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(b)
        self.updateGeometry()
        self.adjustSize()


    def is_visible(self) -> bool:
        # Use a single widget to reduce complexity
        return self.lineEdit_out_model_fp.isVisible()


    def start(self, action: str = '') -> None:
        print("start")
        self.setEnabled(True)
        self.set_visible(True)
        self.button_convert.setEnabled(False)
        self.lineEdit_out_model_fp.setText(f"A:\\DFGHJKJHGFDGHJ")
        if action == 'metadata':
            pass
        elif action == 'convert':
            self.button_convert.setText("Cancel")


    def ended(self) -> None:
        self.set_visible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.button_convert.setText("Convert")
        self.button_convert.setEnabled(True)
        self.is_converting = False


    def stop(self) -> None:
        # Stop without showing progress/path/usage
        self.set_visible(False)
        self.button_convert.setText("Convert")
        self.button_convert.setEnabled(True)
        self.is_converting = False



    def event_convert_button_clicked(self) -> None:
        self.button_convert.setEnabled(False)
        state: str = ''
        if self.is_converting:
            # Stop conversion
            state = 'stop'
            self.is_converting = False
            self.button_convert.setText("Convert")
        else:
            state = 'start'
            self.is_converting = True
            self.button_convert.setText("Stop")

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
        if status['state'] == 'cancelled':
            self.stop()

        elif status['state'] == 'ended':
            self.ended()

        elif status['state'] == 'running':
            self.button_convert.setText("Stop")
            self.set_visible(True)
            if status['type'] == 'undetermined' and status['progress'] == 0:
                print(red("underhdguhsjds"))
                self.progress_bar.setRange(0, 0)
                self.progress_bar.setValue(0)

            if status['cancelable']:
                self.button_convert.setText("Stop")
                self.button_convert.setEnabled(True)
            else:
                self.button_convert.setText("Convert")
                self.button_convert.setEnabled(False)
