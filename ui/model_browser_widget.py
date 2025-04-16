from __future__ import annotations
import os
from typing import Type
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
    QAbstractItemView,
)

from .designer.ui_model_browser_widget import Ui_ModelBrowserWidget


class DragForwarder(QObject):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget

    def eventFilter(self, obj, event: QEvent):
        if event.type() == QEvent.DragEnter:
            print("Redirected dragEnterEvent to parent")
            self.parent_widget.dragEnterEvent(event)
            return True  # Optional: stop event propagation
        if event.type() == QEvent.Type.Drop:
            print("Redirected dragEnterEvent to parent")
            self.parent_widget.dragEnterEvent(event)
            return True  # Optional: stop event propagation

        print(f"{event.type():02x}")
        return False



class ModelBrowserWidget(QWidget, Ui_ModelBrowserWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._parent: type[QWidget] = None

        # self.setAcceptDrops(True)
        self.combobox_model_fp.setAcceptDrops(True)
        self.combobox_model_fp.setEditable(True)
        self.combobox_model_fp.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.clearEditText()
        self.combobox_model_fp.lineEdit().setReadOnly(True)
        self.button_browse.clicked.connect(self.event_in_model_picker)

        self.clear_fields()
        self.setEnabled(True)
        self.adjustSize()

        self.combobox_model_fp.installEventFilter(self)

    def set_parent_widget(self, parent: Type[QWidget]) -> None:
        self._parent = parent


    def clear_fields(self) -> None:
        self.combobox_model_fp.clear()


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # if watched == self.combobox_model_fp:

        if event.type() == QEvent.Type.DragEnter:
            print(f"filtered, DragEnter")
            self._parent.dragEnterEvent(event)
            return True

        elif event.type() == QEvent.Type.Drop:
            print(f"filtered, Drop {event.mimeData().urls()}")
            self._parent.dropEvent(event)
            return True


        return super().eventFilter(watched, event)


    def event_in_model_picker(self):
        pass