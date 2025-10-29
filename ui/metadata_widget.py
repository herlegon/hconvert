from copy import deepcopy
from typing import Type
from hwidgets import HStyle
from pynnlib import (
    NnModel,
)
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
)
from .designer.ui_metadata_widget import Ui_MetadataWidget


class MetadataWidget(QWidget, Ui_MetadataWidget):
    signal_inject_metadata = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self.button_undo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.button_undo.setToolTip("Undo modifications (Ctrl+U)")
        self.button_save_as.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.button_save_as.setToolTip("Save or overwrite(Ctrl+S)")

        self.setEnabled(False)
        self.button_undo.setEnabled(False)
        self.button_save_as.setEnabled(False)
        self.adjustSize()

        self.initial_metadata: dict[str, str] | None = None
        self.current_widget: QWidget | None = None
        self.text_widgets = (
            *self.findChildren(QLineEdit, options=Qt.FindChildOption.FindChildrenRecursively),
            *self.findChildren(QPlainTextEdit, options=Qt.FindChildOption.FindChildrenRecursively),
            *self.findChildren(QTextEdit, options=Qt.FindChildOption.FindChildrenRecursively)
        )
        self.textedit_comment.setAcceptDrops(False)

        self.clear()

        for w in self.text_widgets:
            w: QLineEdit | QTextEdit
            w.setAcceptDrops(False)
            w.textChanged.connect(self.event_edition_started)
        self.textedit_comment.textChanged.connect(self.event_edition_started)
        self.button_undo.released.connect(self.event_undo)
        self.button_save_as.released.connect(self.event_save_as)


    def block_signals(self, b: bool) -> None:
        for w in (
            *self.text_widgets,
            self.button_save_as,
            self.button_undo,
        ):
            w.blockSignals(b)


    def editable_widgets(self) -> list[Type[QWidget]]:
        editable_widgets: list[type[QWidget]] = [
            *self.findChildren(QLineEdit),
            *self.findChildren(QTextEdit),
        ]
        return editable_widgets


    def clear(self) -> None:
        for w in self.text_widgets:
            w.clear()


    def set_enabled(self, b: bool) -> None:
        self.button_undo.setEnabled(b)
        self.button_save_as.setEnabled(b)


    def fill_fields(self, metadata: dict[str, str]) -> None:
        self.block_signals(True)
        if metadata is not None:
            self.lineedit_name.setText(metadata.get("name", ""))
            self.lineedit_date.setText(metadata.get("date", ""))
            self.lineedit_version.setText(metadata.get("version", ""))
            self.lineedit_author.setText(metadata.get("author", ""))
            self.lineedit_license.setText(metadata.get("license", ""))
            self.textedit_comment.setPlainText(metadata.get("comment", ""))
        self.block_signals(False)


    def values(self) -> dict[str, str]:
        return {
            'name': self.lineedit_name.text(),
            'date': self.lineedit_date.text(),
            'version': self.lineedit_version.text(),
            'author': self.lineedit_author.text(),
            'license': self.lineedit_license.text(),
            'comment': self.textedit_comment.toPlainText(),
        }


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        self.button_save_as.setEnabled(False)
        self.button_undo.setEnabled(False)

        if model is None:
            self.setEnabled(False)
            return

        self.initial_metadata = deepcopy(model.metadata)
        self.fill_fields(self.initial_metadata)
        self.setEnabled(True)


    def event_undo(self) -> None:
        self.clear()
        self.button_save_as.setEnabled(False)
        self.button_undo.setEnabled(False)
        self.fill_fields(self.initial_metadata)
        if (
            self.current_widget is not None
            and self.current_widget in self.text_widgets
        ):
            self.current_widget.setFocus()


    def event_save_as(self) -> None:
        self.button_save_as.setEnabled(False)
        self.button_undo.setEnabled(False)
        if (
            self.current_widget is not None
            and self.current_widget in self.text_widgets
        ):
            self.current_widget.setFocus()
        self.signal_inject_metadata.emit(self.values())


    def event_edition_started(self) -> None:
        self.button_save_as.setEnabled(True)
        self.button_undo.setEnabled(True)
        self.current_widget = QApplication.focusWidget()


    def injection_done(self) -> None:
        if (
            self.current_widget is not None
            and self.current_widget in self.text_widgets
        ):
            self.current_widget.setFocus()
