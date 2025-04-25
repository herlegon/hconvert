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
from .common import (
    predefined_shapes,
    predefined_shapes_inv,
)




class OnnxWidget(QWidget, Ui_OnnxWidget):
    def __init__(self, parent, editable: bool | None = None):
        super().__init__(parent)
        self.setupUi(self)
        self.editable: bool | None = editable
        self._saved_shape: tuple[int]= (0, 0)
        self._is_static: bool = False

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
        self.combobox_resolution.setCurrentIndex(-1)

        self.clear()
        self.setEnabled(False)
        self.adjustSize()

        self.radiobutton_fp16.toggled.connect(self.datatype_changed)
        self.radiobutton_static.toggled.connect(self.shape_strategy_changed)

        self.spinbox_w.valueChanged.connect(self.size_modified)
        self.spinbox_h.valueChanged.connect(self.size_modified)
        self.combobox_resolution.currentIndexChanged.connect(self.resolution_selected)



    def block_signals(self, b: bool) -> None:
        if self.editable:
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
        focus_policy: Qt.FocusPolicy = Qt.FocusPolicy.NoFocus
        if editable:
            focus_policy = Qt.FocusPolicy.WheelFocus
            self.main_layout.removeRow(4)
            self.spinbox_w.lineEdit().setFocusPolicy(focus_policy)
            self.spinbox_h.lineEdit().setFocusPolicy(focus_policy)
        else:
            self.main_layout.removeRow(3)
            self.main_layout.removeRow(1)

        self.spinbox_opset.lineEdit().setFocusPolicy(focus_policy)
        self.editable = editable
        self.clear()



    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
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
            self.radiobutton_fp32.setChecked(False)
            self.radiobutton_fp16.setChecked(False)
            self.radiobutton_dynamic.setChecked(False)
            self.radiobutton_static.setChecked(False)
            self.setEnabled(False)
            return

        # Enable conversion
        self.block_signals(True)
        self.spinbox_opset.lineEdit().setText(str(self.spinbox_opset.value()))
        self.spinbox_opset.lineEdit().setReadOnly(False)
        self.spinbox_opset.setReadOnly(False)
        self.spinbox_opset.setEnabled(True)

        self.radiobutton_fp32.setChecked(True)
        self.radiobutton_dynamic.setChecked(True)

        self.radiobutton_static.setChecked(True)
        self._is_static = self.radiobutton_static.isChecked()
        if self._is_static:
            self.spinbox_h.lineEdit().setText(str(self.spinbox_h.value()))
            self.spinbox_w.lineEdit().setText(str(self.spinbox_w.value()))
            self.update_resolution_text()

        for w in (self.spinbox_w, self.spinbox_h):
            w.lineEdit().setReadOnly(not self._is_static)
            w.setReadOnly(not self._is_static)
            w.setEnabled(self._is_static)

        if "fp16" in model.arch.dtypes:
            self.radiobutton_fp16.setCheckable(True)
            self.radiobutton_fp32.setCheckable(True)
        else:
            self.radiobutton_fp16.setCheckable(False)
            self.radiobutton_fp32.setCheckable(False)

        size_constraint: SizeConstraint = model.arch.size_constraint
        if size_constraint is not None:
            self.spinbox_w.setMinimum(size_constraint.min[0])
            self.spinbox_w.setSingleStep(size_constraint.modulo)
            self.spinbox_h.setMinimum(size_constraint.min[1])
            self.spinbox_h.setSingleStep(size_constraint.modulo)
        else:
            self.spinbox_w.setMinimum(8)
            self.spinbox_w.setSingleStep(1)
            self.spinbox_h.setMinimum(8)
            self.spinbox_h.setSingleStep(1)

        self.setEnabled(True)
        self.block_signals(False)




    def datatype_changed(self, state: bool) -> None:
        print("datatype_changed to")



    def shape_strategy_changed(self, state: bool) -> None:
        if not self.editable:
            return
        self.block_signals(True)
        is_static = self.radiobutton_static.isChecked()
        if self._is_static and not is_static:
            # static -> dynamic
            self._saved_shape = (
                self.spinbox_w.value(), self.spinbox_h.value()
            )
            self.spinbox_w.lineEdit().clear()
            self.spinbox_h.lineEdit().clear()
            self.combobox_resolution.setCurrentIndex(-1)

        if not self._is_static and is_static:
            # dynamic -> static
            self.spinbox_w.setValue(self._saved_shape[0])
            self.spinbox_h.setValue(self._saved_shape[1])
            # focus_policy = Qt.FocusPolicy.WheelFocus
            # self.spinbox_w.lineEdit().setFocusPolicy(focus_policy)
            # self.spinbox_h.lineEdit().setFocusPolicy(focus_policy)
            self.update_resolution_text()

        self.spinbox_w.setEnabled(is_static)
        self.spinbox_h.setEnabled(is_static)
        self.combobox_resolution.setEnabled(is_static)

        self._is_static = is_static
        self.block_signals(False)



    def update_resolution_text(self) -> None:
        w, h = self.spinbox_w.value(), self.spinbox_h.value()
        t = predefined_shapes_inv.get("x".join(map(str, (w, h))), "")
        self.combobox_resolution.setCurrentIndex(
            self.combobox_resolution.findText(t)
        )



    def size_modified(self, value: int) -> None:
        self.combobox_resolution.blockSignals(True)
        self.update_resolution_text()
        self.spinbox_w.lineEdit().deselect()
        self.spinbox_h.lineEdit().deselect()
        self.combobox_resolution.blockSignals(False)



    def resolution_selected(self, index: int) -> None:
        current_text: str = self.combobox_resolution.currentText()
        w, h = predefined_shapes[current_text]
        self.spinbox_w.blockSignals(True)
        self.spinbox_h.blockSignals(True)
        self.spinbox_w.setValue(w)
        self.spinbox_h.setValue(h)
        self.spinbox_w.lineEdit().deselect()
        self.spinbox_h.lineEdit().deselect()
        self.spinbox_w.blockSignals(False)
        self.spinbox_h.blockSignals(False)
