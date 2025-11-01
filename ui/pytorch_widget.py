from __future__ import annotations
import os
from hutils import get_extension, parent_directory
from hwidgets import (
    HStyle,
)
from pynnlib import (
    NnModel,
    NnFrameworkType,
)

from PySide6.QtCore import (
    QCoreApplication,
    Qt,
)
from PySide6.QtGui import (
    QPixmap,
)
from PySide6.QtWidgets import (
    QWidget,
)

from .common import load_png_scaled
from .designer.ui_pytorch_widget import Ui_PyTorchWidget




class PyTorchWidget(QWidget, Ui_PyTorchWidget):
    def __init__(self, parent):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self.clear()
        self.setEnabled(False)
        self.lineedit_arch_name.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pushbutton_link.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_scale.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_type.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_size_constraints_min.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lineedit_size_constraints_modulo.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.lineedit_size_constraints_min.setClearButtonEnabled(False)
        self.lineedit_size_constraints_min.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_height: int = 24
        self.framework_logo.clear()
        self.framework_logo.setFixedHeight(logo_height)
        self.framework_name.clear()

        self.framework_img: dict[str, QPixmap] = {
            'onnx': load_png_scaled("onnx_32px.png", height=logo_height),
            'safetensors': load_png_scaled("safetensors_32px.png", height=logo_height),
            'pytorch': load_png_scaled("pytorch_32px.png", height=logo_height),
            'tensorrt': load_png_scaled("tensorrt_24px_transparent.png", height=logo_height),
        }
        self.framework_logo.setStyleSheet("background: transparent;")
        self.framework_logo.setAttribute(Qt.WA_TranslucentBackground, True)
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

        framework_name: str = str(model.framework.type.value)
        if get_extension(model.filepath) == '.safetensors':
            framework_name = 'safetensors'

        if framework_name == 'tensorrt':
            self.framework_name.setText(framework_name)
        else:
            self.framework_name.clear()
        self.framework_logo.setPixmap(self.framework_img[framework_name.lower()])


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

