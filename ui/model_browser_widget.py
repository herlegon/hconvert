from __future__ import annotations
import os
from typing import Type
from PySide6.QtCore import (
    QObject,
    QEvent,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QComboBox,
    QFileDialog,
)

from .designer.ui_model_browser_widget import Ui_ModelBrowserWidget
from pynnlib import (
    NnModel,
)


class ModelBrowserWidget(QWidget, Ui_ModelBrowserWidget):
    signal_model_loaded = Signal(str)


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

        self.clear_fields()
        self.setEnabled(True)
        self.adjustSize()

        self.combobox_model_fp.installEventFilter(self)
        self.button_browse.released.connect(self.model_picker_event)

        self.previous_directory: str = "~/ml_models"
        self.supported_model_extensions: list[str] = [
            ".engine",
            ".trtzip",
            ".onnx",
            ".pt",
            ".pth",
            ".safetensor",
            ".param",
        ]

        extensions = ' '.join([f"*{ext}" for ext in self.supported_model_extensions])
        self.file_filter = f"Model ({extensions})"
        print(self.file_filter)


    def set_parent_widget(self, parent: Type[QWidget]) -> None:
        self._parent = parent


    def clear_fields(self) -> None:
        self.combobox_model_fp.clear()


    def update_model_fp(self, model_fp: str) -> None:
        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.lineEdit().setText(model_fp)
        self.combobox_model_fp.blockSignals(False)


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.combobox_model_fp:

            if event.type() == QEvent.Type.DragEnter:
                self._parent.dragEnterEvent(event)
                return True

            elif event.type() == QEvent.Type.Drop:
                self._parent.dropEvent(event)
                return True

            elif event.type() == QEvent.Type.MouseButtonPress:
                self.model_picker_event()
                return True

        return super().eventFilter(watched, event)


    def model_picker_event(self):
        file_dialog = QFileDialog(
            parent=self,
            fileMode=QFileDialog.FileMode.ExistingFile,
            directory=os.path.abspath(
                os.path.expanduser(self.previous_directory)
            )
        )
        model_fp = file_dialog.getOpenFileName(
            self,
            caption="Open model...",
            filter=self.file_filter
        )[0]
        print(model_fp)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.setCurrentText(model_fp)
        file_dialog.close()
        del file_dialog
        self.signal_model_loaded.emit(model_fp)
