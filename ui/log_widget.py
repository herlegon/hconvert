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
from .designer.ui_log_widget import Ui_LogWidget
from .pynnlib_api import (
    NnModel,
)

class LogWidget(QWidget, Ui_LogWidget):
    signal_inject_metadata = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._editable_widgets: list[type[QWidget]] = [
            *self.findChildren(QLineEdit),
            *self.findChildren(QTextEdit),
        ]


    def block_signals(self, b: bool) -> None:
        pass


    def editable_widgets(self) -> list[Type[QWidget]]:
        return self._editable_widgets


    def clear(self) -> None:
        for w in self._editable_widgets:
            w.clear()


    def set_enabled(self, b: bool) -> None:
        pass


