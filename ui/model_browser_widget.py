from __future__ import annotations
from typing import TYPE_CHECKING
from backend.path_utils import absolute_path, parent_directory
from pynnlib import (
    NnModel,
)

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

from .common import SUPPORTED_MODEL_EXTENSIONS
from .designer.ui_model_browser_widget import Ui_ModelBrowserWidget
if TYPE_CHECKING:
    from .main_window import MainWindow


class ModelBrowserWidget(QWidget, Ui_ModelBrowserWidget):
    signal_model_loaded = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._main_window: MainWindow = None

        # self.setAcceptDrops(True)
        self.combobox_model_fp.setAcceptDrops(True)
        self.combobox_model_fp.setEditable(True)
        self.combobox_model_fp.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.clearEditText()
        self.combobox_model_fp.lineEdit().setReadOnly(True)

        self.clear()
        self.setEnabled(True)
        self.adjustSize()

        self.combobox_model_fp.installEventFilter(self)
        self.button_browse.released.connect(self.model_picker_event)

        self.previous_directory: str = absolute_path("~")
        extensions = ' '.join([f"*{ext}" for ext in SUPPORTED_MODEL_EXTENSIONS])
        self.file_filter = f"Model ({extensions})"


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def clear(self) -> None:
        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.blockSignals(False)


    def update_model_fp(self, model_fp: str) -> None:
        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.lineEdit().setText(model_fp)
        self.combobox_model_fp.blockSignals(False)


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.combobox_model_fp:

            if event.type() == QEvent.Type.DragEnter:
                self._main_window.dragEnterEvent(event)
                return True

            elif event.type() == QEvent.Type.Drop:
                self._main_window.dropEvent(event)
                return True

            elif event.type() == QEvent.Type.MouseButtonPress:
                self.model_picker_event()
                return True

        return super().eventFilter(watched, event)


    def model_picker_event(self):
        file_dialog = QFileDialog(
            parent=self,
            fileMode=QFileDialog.FileMode.ExistingFile,
            directory=absolute_path(self.previous_directory)
        )
        model_fp = file_dialog.getOpenFileName(
            self,
            caption="Open model...",
            filter=self.file_filter
        )[0]
        print(model_fp)
        self.previous_directory = parent_directory(model_fp)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.setCurrentText(model_fp)
        file_dialog.close()
        del file_dialog
        self.signal_model_loaded.emit(model_fp)
