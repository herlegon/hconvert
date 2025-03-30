from __future__ import annotations
import sys
from typing import TYPE_CHECKING
from PySide6.QtCore import (
    Signal,
    Slot,
    QEvent,
    QObject,
    Slot,
)
from PySide6.QtGui import (
    QCloseEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMessageBox,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from .designer.ui_main_window import Ui_MainWindow
if TYPE_CHECKING:
    from backend.controller import Controller


class MainWindow(QMainWindow, Ui_MainWindow):
    signal_k_ep_p_refreshed = Signal(dict)
    signal_preview_modified = Signal(dict)

    def __init__(self, controller: Controller):
        super().__init__()
        self.setupUi(self)
        self.controller: Controller = controller
        self.is_closing: bool = False

        self.installEventFilter(self)


    def apply_user_preferences(self, user_preferences: dict):
        try:
            w: list[int] = user_preferences['window']
            self.setGeometry(*w[self.app_type])
        except:
            self.setGeometry(0, 0, 640, 800)
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


    def close_event(self):
        if not self.is_closing:
            self.is_closing = True
            self.controller.exit()
            self.close_all_widgets()


    def close_all_widgets(self):
        for widget in QApplication.topLevelWidgets():
            widget.close()
        self.close()
        # Not clean but avoid ghost processes: clean this
        sys.exit()
