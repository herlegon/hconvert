from __future__ import annotations
from pynnlib import (
    NnModel,
    NnFrameworkType,
    PyTorchModel,
)

from PySide6.QtCore import (
    QCoreApplication,
)

from PySide6.QtWidgets import (
    QTableWidgetItem,
    QWidget,
    QCheckBox,
    QHBoxLayout,
    QSlider,
    QAbstractSpinBox,
    QLineEdit,
    QComboBox,
)

from .designer.ui_tensorrt_widget import Ui_TensorRTWidget

class TensorRTWidget(QWidget, Ui_TensorRTWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.clear_fields()

        self.setEnabled(False)
        self.adjustSize()


    def clear_fields(self) -> None:
        self.checkbox_dynamic.setChecked(False)
        self.checkbox_dynamic.setCheckable(False)
        self.checkbox_static.setChecked(False)
        self.checkbox_static.setCheckable(False)
        self.lineedit_shape.clear()
        self.lineedit_shape.setReadOnly(True)


    def display_model_info(self, model: NnModel | None) -> None:
        if model.framework.type != NnFrameworkType.TENSORRT:
            self.clear_fields()
            return

        self.checkbox_dynamic.setChecked(True)

        # w, h = model.size_constraint.min
        # self.lineedit_shape.setText(f"{w}x{h}")

