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
from .designer.ui_metadata_widget import Ui_MetadataWidget
from .pynnlib_api import (
    NnModel,
)

class MetadataWidget(QWidget, Ui_MetadataWidget):
    signal_inject_metadata = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self.button_cancel = self.h_button_cancel
        self.button_save_as = self.h_button_save_as
        self.button_edit = self.h_button_edit


        self.button_cancel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.button_cancel.setToolTip("Discard modifications (Ctrl+U)")
        self.button_save_as.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.button_save_as.setToolTip("Save(Ctrl+S)")

        self.button_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.button_edit.setToolTip("Modify the model's info")


        self.setEnabled(False)
        self.button_cancel.setEnabled(False)
        self.button_save_as.setEnabled(False)
        self.button_edit.setEnabled(False)

        self.initial_metadata: dict[str, str] | None = None
        self.current_widget: QWidget | None = None
        self.text_widgets = (
            *self.findChildren(QLineEdit, options=Qt.FindChildOption.FindChildrenRecursively),
            *self.findChildren(QPlainTextEdit, options=Qt.FindChildOption.FindChildrenRecursively),
            *self.findChildren(QTextEdit, options=Qt.FindChildOption.FindChildrenRecursively)
        )
        self.textedit_purpose.setAcceptDrops(False)

        self.clear()
        self.adjustSize()
        # self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # self.setFixedHeight(self.sizeHint().height())

        for w in self.text_widgets:
            w: QLineEdit | QTextEdit
            w.setAcceptDrops(False)
            # w.textChanged.connect(self.event_edition_started)
        self.textedit_purpose.textChanged.connect(self.event_edition_started)
        self.button_cancel.released.connect(self.event_cancel)
        self.button_save_as.released.connect(self.event_save_as)
        self.button_edit.toggled.connect(self.event_edition_started)


    def block_signals(self, b: bool) -> None:
        for w in (
            *self.text_widgets,
            self.button_save_as,
            self.button_cancel,
            self.button_edit,
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
        self.button_cancel.setEnabled(b)
        self.button_save_as.setEnabled(b)
        self.button_edit.setEnabled(b)


    def fill_fields(self, metadata: dict[str, str]) -> None:
        self.block_signals(True)
        if metadata is not None:
            self.lineedit_name.setText(metadata.get("name", ""))
            self.lineedit_author.setText(metadata.get("author", ""))
            self.lineedit_license.setText(metadata.get("license", ""))
            self.textedit_purpose.setPlainText(metadata.get("purpose", ""))

        self.button_edit.setChecked(False)
        for w in self.text_widgets:
            w.setReadOnly(False)

        self.block_signals(False)


    def values(self) -> dict[str, str]:
        return {
            'name': self.lineedit_name.text(),
            'author': self.lineedit_author.text(),
            'license': self.lineedit_license.text(),
            'purpose': self.textedit_purpose.toPlainText(),
        }


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        self.button_save_as.setEnabled(False)
        self.button_cancel.setEnabled(False)

        if model is None:
            self.setVisible(False)
            return
        self.setVisible(True)

        self.initial_metadata = deepcopy(model.metadata)
        self.fill_fields(self.initial_metadata)
        self.button_edit.setEnabled(True)
        self.button_edit.setChecked(False)
        self.event_edition_started()
        self.setEnabled(True)


    def event_cancel(self) -> None:
        self.clear()
        self.button_save_as.setEnabled(False)
        self.button_cancel.setEnabled(False)
        self.button_edit.setChecked(False)
        self.fill_fields(self.initial_metadata)
        if (
            self.current_widget is not None
            and self.current_widget in self.text_widgets
        ):
            self.current_widget.setFocus()


    def event_save_as(self) -> None:
        self.block_signals(True)
        self.button_save_as.setEnabled(False)
        self.button_cancel.setEnabled(False)
        self.button_edit.setChecked(False)
        if (
            self.current_widget is not None
            and self.current_widget in self.text_widgets
        ):
            self.current_widget.setFocus()
        self.block_signals(False)
        self.signal_inject_metadata.emit(self.values())


    def event_edition_started(self) -> None:
        edit: bool = self.button_edit.isChecked()
        self.button_save_as.setEnabled(edit)
        self.button_cancel.setEnabled(edit)
        for w in self.text_widgets:
            w.setReadOnly(not edit)
        if not edit:
            for w in self.text_widgets:
                w.clearFocus()
        self.current_widget = QApplication.focusWidget()


    def injection_done(self) -> None:
        if (
            self.current_widget is not None
            and self.current_widget in self.text_widgets
        ):
            self.current_widget.setFocus()


