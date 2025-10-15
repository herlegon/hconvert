from __future__ import annotations
from pynnlib import (
    NnModel,
    NnFrameworkType,
)

from PySide6.QtCore import (
    QCoreApplication,
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
)
from .designer.ui_pytorch_widget import Ui_PyTorchWidget


class PyTorchWidget(QWidget, Ui_PyTorchWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.clear()
        self.setEnabled(False)
        self.lineedit_arch_name.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pushbutton_link.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_scale.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_type.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_size_constraints_min.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_size_constraints_modulo.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.adjustSize()


    def clear(self) -> None:
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


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        if model is None:
            self.setEnabled(False)
            return

        self.setEnabled(True)

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
            self.lineedit_scale.setText(f"{model.scale}")
        else:
            self.lineedit_scale.setText("?")

        if model.size_constraint is not None:
            w, h = model.size_constraint.min
            self.lineedit_size_constraints_min.setText(f"{w} x {h}")
            self.lineedit_size_constraints_modulo.setText(f"{model.size_constraint.modulo}")

