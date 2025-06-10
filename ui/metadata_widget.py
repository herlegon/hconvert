from __future__ import annotations
from pynnlib import (
    NnModel,
)

from PySide6.QtCore import (
    Qt,
)

from PySide6.QtWidgets import (
    QWidget,
)

from .designer.ui_metadata_widget import Ui_MetadataWidget

class MetadataWidget(QWidget, Ui_MetadataWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.clear()
        self.setEnabled(False)
        self.pushbutton_inject.setEnabled(False)
        self.adjustSize()


    def clear(self) -> None:
        pass


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        self.pushbutton_inject.setEnabled(False)

        if model is None:
            self.setEnabled(False)
            return

        self.lineedit_name.setText(model.metadata.get("name", ""))
        self.lineedit_date.setText(model.metadata.get("date", ""))
        self.lineedit_version.setText(model.metadata.get("version", ""))
        self.lineedit_author.setText(model.metadata.get("author", ""))
        self.lineedit_license.setText(model.metadata.get("license", ""))
        self.textedit_comment.setText(model.metadata.get("comment", ""))

        self.setEnabled(True)
