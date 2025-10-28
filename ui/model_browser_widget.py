from __future__ import annotations
import os
from pathlib import Path
from pprint import pprint
import sys
from typing import TYPE_CHECKING, Type
from hutils import (
    absolute_path,
    get_extension,
    parent_directory,
)
from PySide6.QtCore import (
    QObject,
    QEvent,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QKeySequence,
)
from PySide6.QtWidgets import (
    QWidget,
    QComboBox,
    QFileDialog,
    QLineEdit,
    QSizePolicy,
    QLayout,
)

from hwidgets import HStyle


from .common import SUPPORTED_MODEL_EXTENSIONS
from .designer.ui_model_browser_widget import Ui_ModelBrowserWidget
if TYPE_CHECKING:
    from .main_window import MainWindow



def _get_widget_parent_layout(widget: QWidget) -> QLayout | None:
    """Find the direct parent layout of a widget."""
    parent = widget.parentWidget()
    if not parent:
        return None

    def find_in_layout(layout: QLayout):
        if layout is None:
            return None
        item: QLayout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() == widget:
                return layout
            if item.layout():
                result = find_in_layout(item.layout())
                if result:
                    return result
        return None

    return find_in_layout(parent.layout())



class ReadOnlyComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        if sys.platform == 'linux':
            # fuck stupid shitty ubuntu
            self.lineEdit().installEventFilter(self)
            self.installEventFilter(self)

    # def eventFilter(self, obj, event: QEvent):
    #     # Intercept key events on the line edit
    #     if obj is self.lineEdit():
    #         if event.type() == QEvent.Type.KeyPress:
    #             print(f"key event: {event}")
    #             key_event = event
    #             # Allow only navigation and copy
    #             if key_event.matches(QKeySequence.Copy):
    #                 return super().eventFilter(obj, event)
    #             if key_event.key() in (
    #                 Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Home, Qt.Key.Key_End
    #             ):
    #                 return super().eventFilter(obj, event)
    #             # Block editing keys (typing, paste, delete, etc.)
    #             return True
    #     return super().eventFilter(obj, event)



    def eventFilter(self, obj, event: QEvent):
        if obj is self.lineEdit():
            if event.type() == QEvent.KeyPress:
                # print(f"key event: {event}")
                ke = event  # type: QKeyEvent
                # ✅ Allow copy shortcuts
                if ke.matches(QKeySequence.Copy):
                    return False  # let Qt handle it
                # ✅ Allow navigation keys
                if ke.key() in (
                    Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End,
                    Qt.Key_Shift, Qt.Key_Control, Qt.Key_C,
                ):
                    return False
                # 🚫 Block everything else (typing, delete, paste, etc.)
                return True

            elif event.type() == QEvent.InputMethod or event.type() == QEvent.KeyRelease:
                return True  # block IME and release events

            elif event.type() == QEvent.MouseButtonPress:
                # ✅ Allow mouse selection
                return False

        return super().eventFilter(obj, event)



class ModelBrowserWidget(QWidget, Ui_ModelBrowserWidget):
    signal_model_loaded = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._main_window: MainWindow = None
        self.popup_visible = False
        self.max_items: int = 10

        # Replace the QComboBox by a customized one that allow selction/Ctrl+C only
        # self.replace_combobox()
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


    def replace_combobox(self):
        old_combo = self.combobox_model_fp

        layout = _get_widget_parent_layout(old_combo)
        new_combo = ReadOnlyComboBox(old_combo.parentWidget())
        new_combo.setObjectName(old_combo.objectName())
        new_combo.addItems([old_combo.itemText(i) for i in range(old_combo.count())])
        new_combo.setCurrentIndex(old_combo.currentIndex())

        new_combo.setSizePolicy(old_combo.sizePolicy())
        new_combo.setMinimumSize(old_combo.minimumSize())
        new_combo.setMaximumSize(old_combo.maximumSize())
        new_combo.setFont(old_combo.font())
        new_combo.setStyleSheet(old_combo.styleSheet())

        # Replace it in the layout
        for i in range(layout.count()):
            if layout.itemAt(i).widget() is old_combo:
                layout.replaceWidget(old_combo, new_combo)
                break
        old_combo.deleteLater()

        self.combobox_model_fp = new_combo
        layout.activate()
        self.updateGeometry()
        self.adjustSize()


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
        # Select in the list if already exists
        index: int = self.combobox_model_fp.findText(model_fp)
        if index >= 0:
            self.combobox_model_fp.setCurrentIndex(index)
        else:
            self.combobox_model_fp.insertItem(0, model_fp)

        while self.combobox_model_fp.count() > self.max_items:
            self.combobox_model_fp.removeItem(self.combobox_model_fp.count() - 1)


    def update_model_fp(self, filepath: str = "") -> None:
        self.combobox_model_fp.blockSignals(True)
        if filepath:
            model_fp: Path = Path(filepath)
            self.append_to_combobox(model_fp)
            self.previous_directory = parent_directory(str(model_fp))

        else:
            self.combobox_model_fp.lineEdit().clear()

        self.combobox_model_fp.blockSignals(False)


    def event_selection_changed(self, index: int) -> None:
        if index < 0:
            return
        self.combobox_model_fp.blockSignals(True)
        model_fp = self.combobox_model_fp.itemText(index)
        self.combobox_model_fp.blockSignals(False)
        self.signal_model_loaded.emit(model_fp)


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
            self.combobox_model_fp.lineEdit().setText(str(Path(model_fp)))
            file_dialog.close()
            self.signal_model_loaded.emit(model_fp)


    def set_filepath(self, model_fp: str) -> None:
        # Set combobox lineedit without adding to the combobox
        # it will be done only once the model is a valid one
        print(f"set_filepath: {model_fp}")
        self.combobox_model_fp.lineEdit().setText(model_fp)


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # if isinstance(watched, QComboBox | QLineEdit):
        #     print(watched)
        #     print(event)
        #     print()

        if watched == self.combobox_model_fp:

            if event.type() == QEvent.Type.DragEnter:
                self._main_window.dragEnterEvent(event)
                return True

            elif event.type() == QEvent.Type.Drop:
                self._main_window.dropEvent(event)
                return True

            # elif event.type() == QEvent.Type.MouseButtonPress:
            #     if self.popup_visible:
            #         self.combobox_model_fp.hidePopup()
            #         self.popup_visible = False
            #     else:
            #         self.combobox_model_fp.showPopup()
            #         self.popup_visible = True
            #     return True

            # elif event.type() == QEvent.Type.Hide:
            #     self.popup_visible = False
            # elif event.type() == QEvent.Type.Show:
            #     self.popup_visible = True
        return super().eventFilter(watched, event)

