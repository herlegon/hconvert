from copy import deepcopy
from typing import Type
from hwidgets import HStyle

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
    QSizePolicy,
)
from .designer.ui_header_widget import Ui_HeaderWidget
from .pynnlib_api import (
    NnModel,
)
from .logger import alog


class HeaderWidget(QWidget, Ui_HeaderWidget):
    signal_visibility_changed = Signal(bool)
    signal_settings_clicked = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent)

        hrl_style = HStyle()
        self.setupUi(self, hrl_style)

        self.h_button_log.toggled.connect(self.event_change_visibility)
        self.h_button_settings.released.connect(self.event_settings_clicked)


    def block_signals(self, b: bool) -> None:
        self.h_button_log.blockSignals(b)


    def clear(self) -> None:
        pass


    def set_enabled(self, b: bool) -> None:
        pass


    def set_log_button_state(self, b: bool) -> None:
        self.block_signals(True)
        self.h_button_log.setChecked(b)
        self.block_signals(False)


    def event_change_visibility(self, b: bool) -> None:
        alog.debug(f"log button clicked")
        self.signal_visibility_changed.emit(
            self.h_button_log.isChecked()
        )


    def event_settings_clicked(self) -> None:
        self.signal_settings_clicked.emit()
