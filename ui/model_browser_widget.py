from __future__ import annotations
import os
from pathlib import Path
from typing import TYPE_CHECKING, Type
from hytils import (
    absolute_path,
    get_extension,
    parent_directory,
)
from hwidgets import HStyle

from .common import SUPPORTED_MODEL_EXTENSIONS
from .designer.ui_model_browser_widget import Ui_ModelBrowserWidget
from .logger import alog
if TYPE_CHECKING:
    from .main_window import MainWindow

from PySide6.QtCore import (
    QObject,
    QEvent,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QComboBox,
    QFileDialog,
)


class ModelBrowserWidget(QWidget, Ui_ModelBrowserWidget):
    signal_model_selected = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._main_window: MainWindow = None
        self.popup_visible = False
        self.max_items: int = 10
        self._wheel_scrolling = False

        # Replace the QComboBox by a customized one that allow selction/Ctrl+C only
        self.combobox_model_fp.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.combobox_model_fp.setAcceptDrops(True)
        self.combobox_model_fp.setMaxCount(10)
        self.combobox_model_fp.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.clearEditText()
        self.combobox_model_fp.setEditable(False)

        self.clear()
        self.setEnabled(True)
        self.adjustSize()

        self.previous_directory: str = absolute_path("~")
        extensions = ' '.join([f"*{ext}" for ext in SUPPORTED_MODEL_EXTENSIONS])
        self.file_filter = f"Model ({extensions})"

        # self.combobox_model_fp.installEventFilter(self)
        # self.combobox_model_fp.lineEdit().installEventFilter(self)
        self.button_browse.released.connect(self.event_model_picker)
        self.combobox_model_fp.currentIndexChanged.connect(self.event_selection_changed)


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def apply_user_settings(self, prefs: dict) -> None:
        history = prefs.get('in_models_history', [])
        if not history:
            return
        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.clearEditText()
        for f in history[:self.max_items]:
            if f and os.path.isfile(f) and get_extension(f) in SUPPORTED_MODEL_EXTENSIONS:
                self.combobox_model_fp.addItem(str(Path(f)))
        self.combobox_model_fp.setCurrentIndex(-1)
        self.combobox_model_fp.blockSignals(False)


    def get_user_settings(self) -> dict:
        return {
            'in_models_history': list([
                Path(self.combobox_model_fp.itemText(i)).as_posix()
                for i in range(self.combobox_model_fp.count())
            ])
        }


    def editable_widgets(self) -> list[Type[QWidget]]:
        editable_widgets: list[Type[QWidget]] = [
            self.combobox_model_fp,
            self.combobox_model_fp.lineEdit(),
        ]
        return editable_widgets


    def clear(self) -> None:
        self.combobox_model_fp.blockSignals(True)
        self.combobox_model_fp.clear()
        self.combobox_model_fp.blockSignals(False)


    def append_to_combobox(self, filepath: Path) -> None:
        model_fp: str = str(filepath)

        # Remove existing entry if present
        index: int = self.combobox_model_fp.findText(model_fp)
        if index >= 0:
            self.combobox_model_fp.removeItem(index)

        # Insert at top
        self.combobox_model_fp.insertItem(0, model_fp)
        self.combobox_model_fp.setCurrentIndex(0)

        # Trim excess items
        while self.combobox_model_fp.count() > self.max_items:
            self.combobox_model_fp.removeItem(self.combobox_model_fp.count() - 1)

    # def append_to_combobox(self, filepath: Path) -> None:
    #     model_fp: str = str(filepath)
    #     # Select in the list if already exists
    #     index: int = self.combobox_model_fp.findText(model_fp)
    #     if index >= 0:
    #         self.combobox_model_fp.setCurrentIndex(index)
    #     else:
    #         self.combobox_model_fp.insertItem(0, model_fp)

    #     while self.combobox_model_fp.count() > self.max_items:
    #         self.combobox_model_fp.removeItem(self.combobox_model_fp.count() - 1)


    def update_model_fp(self, filepath: str = "", is_valid: bool = True) -> None:
        self.combobox_model_fp.blockSignals(True)
        alog.warning(f"model_fp={filepath}, valid={is_valid}")
        if filepath and is_valid:
            model_fp: Path = Path(filepath)
            self.append_to_combobox(model_fp)
            self.previous_directory = parent_directory(str(model_fp))

        elif not filepath or not is_valid:
            line_edit = self.combobox_model_fp.lineEdit()
            if line_edit is not None:
                self.combobox_model_fp.lineEdit().clear()
            self.combobox_model_fp.clearEditText()
            self.combobox_model_fp.setCurrentIndex(-1)

        if not is_valid:
            index: int = self.combobox_model_fp.findText(filepath)
            if index >= 0:
                alog.warning(f"remove item, index={index}")
                self.combobox_model_fp.removeItem(index)

        self.combobox_model_fp.blockSignals(False)


    # def event_selection_changed(self, index: int) -> None:
    #     if index < 0:
    #         return
    #     self.combobox_model_fp.blockSignals(True)
    #     model_fp = self.combobox_model_fp.itemText(index)
    #     self.combobox_model_fp.blockSignals(False)
    #     self.signal_model_selected.emit(model_fp)


    def event_selection_changed(self, index: int) -> None:
        if index < 0:
            return

        # Only move item to top if the selection was not caused by wheel scrolling
        if not self._wheel_scrolling:
            self.combobox_model_fp.blockSignals(True)
            model_fp = self.combobox_model_fp.itemText(index)
            self.append_to_combobox(Path(model_fp))  # moves to top
            self.combobox_model_fp.blockSignals(False)
            self.signal_model_selected.emit(model_fp)
        else:
            model_fp = self.combobox_model_fp.itemText(index)
            self.signal_model_selected.emit(model_fp)


    def event_model_picker(self):
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

        if model_fp:
            self.previous_directory = parent_directory(model_fp)
            print(model_fp)
            self.combobox_model_fp.setCurrentText(model_fp)
            file_dialog.close()
            self.signal_model_selected.emit(model_fp)


    def set_filepath(self, model_fp: str) -> None:
        self.combobox_model_fp.setCurrentText(model_fp)


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.combobox_model_fp:
            if event.type() == QEvent.Type.Wheel:
                self._wheel_scrolling = True
            elif event.type() == QEvent.Type.Wheel and event.type() == QEvent.Type.Leave:
                self._wheel_scrolling = False

            elif event.type() == QEvent.Type.DragEnter:
                self._main_window.dragEnterEvent(event)
                return True

            elif event.type() == QEvent.Type.Drop:
                self._main_window.dropEvent(event)
                return True
        return super().eventFilter(watched, event)

