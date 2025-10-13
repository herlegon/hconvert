from __future__ import annotations
import os
from pprint import pprint
from typing import TYPE_CHECKING
from backend.path_utils import absolute_path, get_extension, parent_directory
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
        self.combobox_model_fp.lineEdit().setReadOnly(False)
        self.max_items: int = 10

        self.clear()
        self.setEnabled(True)
        self.adjustSize()

        self.previous_directory: str = absolute_path("~")
        extensions = ' '.join([f"*{ext}" for ext in SUPPORTED_MODEL_EXTENSIONS])
        self.file_filter = f"Model ({extensions})"

        self.combobox_model_fp.installEventFilter(self)
        self.button_browse.released.connect(self.model_picker_event)
        self.combobox_model_fp.currentIndexChanged.connect(self.event_selection_changed)


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def apply_user_preferences(self, prefs: dict) -> None:
        history = prefs.get('in_models_history', [])
        if not history:
            return

        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.lineEdit().clear()
        for f in history[:self.max_items]:
            if f and os.path.isfile(f) and get_extension(f) in SUPPORTED_MODEL_EXTENSIONS:
                self.combobox_model_fp.addItem(f)
        self.combobox_model_fp.blockSignals(False)


    def get_user_preferences(self) -> dict:
        return {
            'in_models_history': list([
                self.combobox_model_fp.itemText(i)
                for i in range(self.combobox_model_fp.count())
            ])
        }


    def clear(self) -> None:
        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.blockSignals(False)


    def update_model_fp(self, model_fp: str = "") -> None:
        self.combobox_model_fp.blockSignals(True)
        if model_fp:
            self.combobox_model_fp.lineEdit().setText(model_fp)

            index: int = self.combobox_model_fp.findText(model_fp)
            if index >= 0:
                self.combobox_model_fp.removeItem(index)
            self.combobox_model_fp.insertItem(0, model_fp)
            self.combobox_model_fp.setCurrentIndex(0)

            while self.combobox_model_fp.count() > self.max_items:
                self.combobox_model_fp.removeItem(self.combobox_model_fp.count() - 1)

            self.previous_directory = parent_directory(model_fp)

        else:
            self.combobox_model_fp.lineEdit().clear()

        self.combobox_model_fp.blockSignals(False)


    def event_selection_changed(self, index: int) -> None:
        if index <= 0:
            return

        self.combobox_model_fp.blockSignals(True)
        model_fp = self.combobox_model_fp.itemText(index)
        self.combobox_model_fp.removeItem(index)
        self.combobox_model_fp.insertItem(0, model_fp)
        self.combobox_model_fp.setCurrentIndex(0)
        self.combobox_model_fp.blockSignals(False)
        self.signal_model_loaded.emit(model_fp)


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

        self.previous_directory = parent_directory(model_fp)
        self.combobox_model_fp.lineEdit().setText(model_fp)
        file_dialog.close()
        del file_dialog
        self.signal_model_loaded.emit(model_fp)


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

