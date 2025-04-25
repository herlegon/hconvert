from __future__ import annotations
from pprint import pprint
from pynnlib import (
    NnModel,
    NnFrameworkType,
    OnnxModel,
    SizeConstraint,
)

from PySide6.QtCore import (
        QSize,
        Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QAbstractSpinBox,
    QLineEdit,
    QComboBox,
    QSizePolicy,
)

from pynnlib.utils.p_print import red
from .designer.ui_onnx_widget import Ui_OnnxWidget


predefined_shapes: dict[str, tuple[int, int]] = {
    "480p 16:9 (DVD)": (854, 480),
    "480p 4:3": (640, 480),
    "480p NTSC": (720, 480),
    "576p 4:3 sq": (768, 576),
    "720p 4:3": (960, 720),
    "720p (HD ready)": (1280, 720),
    "1080p (Full HD)": (1920, 1080),
    "2160p (4K UHDTV)": (3840, 2160)
}

predefined_shapes_inv: dict[str, str] = {
    "x".join(map(str, v)): k for k, v in predefined_shapes.items()
}


class OnnxWidget(QWidget, Ui_OnnxWidget):
    def __init__(self, parent, editable: bool | None = None):
        super().__init__(parent)
        self.setupUi(self)
        self.editable: bool | None = editable
        self.saved_shape: dict[str, str] = {}

        for w in (self.lineedit_w, self.lineedit_h,):
            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for w in (
            self.spinbox_opset,
            self.spinbox_w,
            self.spinbox_h,
            self.combobox_resolution,
        ):
            w.setFocusPolicy(Qt.FocusPolicy.WheelFocus)

        self.combobox_resolution.clear()
        self.combobox_resolution.addItems(list(predefined_shapes.keys()))
        self.combobox_resolution.setCurrentIndex(1)
        self.combobox_resolution.setCurrentText("")

        self.clear()
        self.setEnabled(False)
        self.adjustSize()

        self.combobox_resolution.currentIndexChanged.connect(self.resolution_selected)
        self.spinbox_h.valueChanged.connect(self.resolution_changed)
        self.radiobutton_fp16.toggled.connect(self.datatype_changed)


    def block_signals(self, b: bool) -> None:
        self.radiobutton_fp32.blockSignals(b)
        self.radiobutton_fp16.blockSignals(b)
        self.spinbox_w.blockSignals(b)
        self.spinbox_h.blockSignals(b)
        self.combobox_resolution.blockSignals(b)


    def clear(self) -> None:
        self.spinbox_opset.clear()
        spinbox_width = 50
        self.radiobutton_dynamic.setChecked(False)
        self.radiobutton_static.setChecked(False)

        if self.editable:
            self.block_signals(True)
            self.spinbox_opset.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
            self.radiobutton_fp32.setChecked(False)
            self.radiobutton_fp16.setChecked(False)
            self.spinbox_w.lineEdit().clear()
            self.spinbox_h.lineEdit().clear()
            self.spinbox_w.clear()
            self.spinbox_h.clear()
            self.combobox_resolution.setCurrentText("")
            self.block_signals(False)

        if not self.editable:
            self.spinbox_opset.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spinbox_width = 35
            self.lineedit_w.clear()
            self.lineedit_h.clear()
            self.label_resolution.clear()
        self.spinbox_opset.setMinimumWidth(spinbox_width)
        self.spinbox_opset.setMaximumWidth(spinbox_width)


    def set_editable(self, editable: bool) -> None:
        # Allow once only
        if self.editable is not None:
            return

        self.spinbox_opset.lineEdit().setReadOnly(not editable)
        self.spinbox_opset.lineEdit().setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if editable:
            self.main_layout.removeRow(4)
        else:
            self.main_layout.removeRow(3)
            self.main_layout.removeRow(1)

        self.editable = editable
        self.clear()


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        print(model)
        if model is None or model.framework.type != NnFrameworkType.ONNX:
            return

        self.setEnabled(True)
        self.spinbox_opset.setValue(model.opset)

        if 'static' in model.shape_strategy.type:
            self.radiobutton_static.setChecked(True)
            self.lineedit_w.setText(str(model.shape_strategy.opt_size[0]))
            self.lineedit_h.setText(str(model.shape_strategy.opt_size[1]))

        else:
            self.radiobutton_dynamic.setChecked(True)

        if 'fp32' in model.dtypes and 'fp16' in model.dtypes:
            print(red("ERRROR, onnx has both fp16 and fp32"))

        self.setEnabled(False)



    def enable_conversion(self, model: NnModel) -> None:
        self.clear()

        # PyTorch only
        # Conversion must be possible for the arch
        if (
            not self.editable
            or model.framework.type != NnFrameworkType.PYTORCH
            or model.arch.to_onnx is None
        ):
            self.setEnabled(False)
            return

        self.spinbox_opset.lineEdit().setText(str(self.spinbox_opset.value()))
        self.radiobutton_fp32.setChecked(True)
        self.radiobutton_dynamic.setChecked(True)
        if self.radiobutton_static:
            self.spinbox_h.lineEdit().setText(str(self.spinbox_h.value()))
            self.spinbox_w.lineEdit().setText(str(self.spinbox_w.value()))
        for w in (
            self.spinbox_opset,
            self.spinbox_w,
            self.spinbox_h,
        ):
            w.setReadOnly(False)
            w.setEnabled(True)
            w.lineEdit().setReadOnly(False)

        pprint(model.arch)
        if "fp16" in model.arch.dtypes:
            self.radiobutton_fp16.setCheckable(True)
            self.radiobutton_fp32.setCheckable(True)
        else:
            self.radiobutton_fp16.setCheckable(False)
            self.radiobutton_fp32.setCheckable(False)

        size_constraint: SizeConstraint = model.arch.size_constraint
        self.spinbox_w.setMinimum(size_constraint.min[0])
        self.spinbox_w.setSingleStep(size_constraint.modulo)
        self.spinbox_h.setMinimum(size_constraint.min[1])
        self.spinbox_h.setSingleStep(size_constraint.modulo)

        self.setEnabled(True)


    def resolution_selected(self, index: int) -> None:
        current_text: str = self.combobox_resolution.currentText()
        w, h = predefined_shapes[current_text]
        self.spinbox_w.blockSignals(True)
        self.spinbox_w.setValue(w)
        self.spinbox_w.blockSignals(False)
        self.spinbox_h.blockSignals(True)
        self.spinbox_h.setValue(h)
        self.spinbox_h.blockSignals(True)


    def resolution_changed(self, value: int) -> None:
        w, h = self.spinbox_w.value(), self.spinbox_h.value()
        k = "x".join(map(str, (w, h)))
        t = predefined_shapes_inv.get(k, "")

        self.combobox_resolution.blockSignals(True)
        self.combobox_resolution.setCurrentIndex(
            self.combobox_resolution.findText(t)
        )
        self.combobox_resolution.blockSignals(False)


    def datatype_changed(self, state: bool) -> None:
        print("changed to")