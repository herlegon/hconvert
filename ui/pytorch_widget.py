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

from .designer.ui_pytorch_widget import Ui_PyTorchWidget

class PyTorchWidget(QWidget, Ui_PyTorchWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.clear_fields()

        self.setEnabled(False)
        self.adjustSize()


    def clear_fields(self) -> None:
        self.lineedit_arch_name.clear()
        self.lineedit_arch_name.setReadOnly(True)
        self.pushbutton_link.setVisible(False)
        self.pushbutton_link.setEnabled(False)
        self.lineedit_scale.clear()
        self.lineedit_scale.setReadOnly(True)
        self.lineedit_type.clear()
        self.lineedit_type.setReadOnly(True)
        self.lineedit_size_constraints_min.clear()
        self.lineedit_size_constraints_min.setReadOnly(True)
        self.lineedit_size_constraints_modulo.clear()
        self.lineedit_size_constraints_modulo.setReadOnly(True)


    def display_model_info(self, model: NnModel | None) -> None:
        if model is None:
            self.clear_fields()
            return

        if model.framework.type == NnFrameworkType.PYTORCH:
            title = QCoreApplication.translate("PyTorchWidget", u"PyTorch", None)
        else:
            title = QCoreApplication.translate("PyTorchWidget", u"Model", None)
        self.groupbox_pytorch_model.setTitle(title)


        self.lineedit_arch_name.setText(model.arch_name)
        if model.arch_name not in ("unknown", "generic"):
            self.pushbutton_link.setEnabled(True)
        else:
            self.pushbutton_link.setEnabled(False)

        if model.scale != 0:
            self.lineedit_scale.setText(model.scale)
        else:
            self.lineedit_scale.setText("?")

        w, h = model.size_constraint.min
        self.lineedit_size_constraints_min.setText(f"{w}x{h}")
        self.lineedit_size_constraints_modulo.setText(f"{model.size_constraint.modulo}")

