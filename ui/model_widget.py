from __future__ import annotations
import os
from PySide6.QtCore import (
    QObject,
    QEvent,
)

from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QWidget,
    QComboBox,
)

from .designer.ui_model_widget import Ui_ModelWidget

class ModelWidget(QWidget, Ui_ModelWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.widget_onnx_model.set_editable(False)
        self.widget_model_browser.set_parent_widget(self)


        self.clear_fields()
        self.setAcceptDrops(True)
        self.setEnabled(True)
        self.adjustSize()


        self.supported_model_extensions: list[str] = [
            '.engine', '.onnx', '.pt', '.pth'
        ]
        # self.model_browser_widget.combobox_model_fp.installEventFilter(self)


    def clear_fields(self) -> None:
        # self.combobox_model_fp.clear()
        pass


    def dropEvent(self, event: QDropEvent):
        model_fp: str = os.path.abspath(
            os.path.expanduser(event.mimeData().urls()[0].toLocalFile())
        )
        print(f"dropping {model_fp}")
        self.widget_model_browser.combobox_model_fp.clear()
        self.widget_model_browser.combobox_model_fp.setCurrentText(model_fp)
        print(f"dropped: {self.widget_model_browser.combobox_model_fp.currentText()}")


    def dragEnterEvent(self, event: QDragEnterEvent):
        print("dragging")
        is_allowed: bool = False
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            print(event.mimeData().urls())
            if len(urls) == 1:
                extension = os.path.splitext(
                    os.path.abspath(os.path.expanduser(urls[0].toLocalFile()))
                )[1].lower()
                if extension in self.supported_model_extensions:
                    event.acceptProposedAction()
                    is_allowed = True

        if not is_allowed:
            print("Oh noooo!!!")

        # return super().dragEnterEvent(event)

