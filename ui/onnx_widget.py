from __future__ import annotations
from pprint import pprint
from hutils import (
    red
)
from pynnlib import (
    NnModel,
    NnFrameworkType,
)
from .common import (
    DEFAULT_SIZE,
    predefined_shapes_inv,
    ShapeStrategyName,
)

from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QRadioButton,
    QWidget,
)
from .designer.ui_onnx_widget import Ui_OnnxWidget



class OnnxWidget(QWidget, Ui_OnnxWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setupUi(self)

        self.shape_strategy: ShapeStrategyName = 'dynamic'

        self.clear()
        self.adjustSize()
        self.setEnabled(False)


    def clear(self) -> None:
        for r in self.findChildren(QRadioButton):
            r.setChecked(False)
        for l in self.findChildren(QLineEdit):
            l.clear()
        self.label_resolution.clear()


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        if model is None or model.framework.type != NnFrameworkType.ONNX:
            self.setEnabled(False)
            return

        self.setEnabled(True)
        self.lineedit_opset.setText(f"{model.opset}")

        for r in self.findChildren(QRadioButton):
            r.setEnabled(True)

        # datatypes
        if 'fp32' in model.dtypes and 'fp16' in model.dtypes:
            print(red("ERRROR, onnx has both fp16 and fp32"))

        if model.io_dtypes['input'] == 'fp32':
            self.radiobutton_fp32.setChecked(True)
        elif model.io_dtypes['input'] == 'fp16':
            self.radiobutton_fp16.setChecked(True)
        elif model.io_dtypes['input'] == 'bf16':
            self.radiobutton_bf16.setChecked(True)
        else:
            print("unknow datatype")

        # Shape strategy
        if model.shape_strategy.type == 'static':
            print(red("STATIC"))
            self.radiobutton_static.setChecked(True)
            size = " x ".join(map(str, model.shape_strategy.opt_size))
            self.lineedit_shape.setText(size)
            self.label_resolution.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), ""))

        else:
            print(red("dyna"))
            self.radiobutton_dynamic.setChecked(True)

        # Do not allow clicking on a Qadiobutton or selectin a text
        for r in self.findChildren(QRadioButton):
            r.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            r.setEnabled(False)
        for l in self.findChildren(QLineEdit):
            l.setEnabled(False)

        self.setStyleSheet("""
            QRadioButton:disabled { color: black; }
            QLineEdit:disabled { color: black; }
        """)

