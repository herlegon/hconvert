from __future__ import annotations
from pprint import pprint
from typing import Tuple
from pynnlib import (
    NnModel,
    NnFrameworkType,
    OnnxModel,
    SizeConstraint,
)

from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
    Slot,
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
    DEFAULT_SIZE,
    PREDEFINED_SIZE,
    predefined_shapes_inv,
    ShapeStrategyName,
)




class OnnxWidget(QWidget, Ui_OnnxWidget):
    # ShapeStrategyName, size as tuple (w, h)
    signal_shape_strategy_changed = Signal(str, object)
    signal_selection_changed: Signal = Signal(bool)
    signal_is_enabled: Signal = Signal(bool)

    def __init__(self, parent, editable: bool | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self._saved_shape: tuple[int] = DEFAULT_SIZE
        self.shape_strategy: ShapeStrategyName = 'dynamic'
        self._tensorrt_static_shape: tuple[int, int] = (0, 0)
        self.lineedit_shape.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.clear()
        self.setEnabled(False)
        # self.adjustSize()

        self.groupbox_onnx_conversion.clicked.connect(self.event_conversion_selected)


    def clear(self) -> None:
        self.spinbox_opset.clear()
        self.checkbox_dynamic.setChecked(False)
        self.checkbox_static.setChecked(False)

        self.spinbox_opset.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spinbox_width = 35
        self.lineedit_shape.clear()
        self.label_resolution.clear()
        self.spinbox_opset.setMinimumWidth(spinbox_width)
        self.spinbox_opset.setMaximumWidth(spinbox_width)



    # def set_editable(self, editable: bool) -> None:
    #     focus_policy: Qt.FocusPolicy = Qt.FocusPolicy.NoFocus

    #     self.spinbox_opset.lineEdit().setFocusPolicy(focus_policy)
    #     self.editable = editable
    #     self.clear()


    def event_conversion_selected(self, checked: bool) -> bool:
        print(f"onnx widget:enabled changed: {checked} vs {self.groupbox_onnx_conversion.isChecked()}")
        # if self.groupbox_onnx_conversion.isChecked():
        self.signal_selection_changed.emit(self.groupbox_onnx_conversion.isChecked())


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        if model is None or model.framework.type != NnFrameworkType.ONNX:
            return

        self.setEnabled(True)
        self.spinbox_opset.setValue(model.opset)

        if 'static' in model.shape_strategy.type:
            self.checkbox_static.setChecked(True)
            self.lineedit_w.setText(str(model.shape_strategy.opt_size[0]))
            self.lineedit_h.setText(str(model.shape_strategy.opt_size[1]))

        else:
            self.checkbox_dynamic.setChecked(True)

        if 'fp32' in model.dtypes and 'fp16' in model.dtypes:
            print(red("ERRROR, onnx has both fp16 and fp32"))

        self.setEnabled(False)


    # def update_resolution_text(self) -> None:
    #     w, h = self.spinbox_w.value(), self.spinbox_h.value()
    #     t = predefined_shapes_inv.get("x".join(map(str, (w, h))), "")
    #     self.combobox_resolution.setCurrentIndex(
    #         self.combobox_resolution.findText(t)
    #     )



    # def save_current_size(self) -> None:
    #     self._saved_shape = (
    #         self.spinbox_w.value(), self.spinbox_h.value()
    #     )



    # def restore_size(self, ignore_opt: bool = False) -> None:
    #     self.spinbox_w.setValue(self._saved_shape[0])
    #     self.spinbox_h.setValue(self._saved_shape[1])
    #     self.update_resolution_text()



    # def update_size_widgets(self, strategy: ShapeStrategyName) -> None:
    #     if strategy == 'static':
    #         self.spinbox_w.setEnabled(True)
    #         self.spinbox_h.setEnabled(True)
    #         self.combobox_resolution.setEnabled(True)

    #     else:
    #         self.spinbox_w.lineEdit().clear()
    #         self.spinbox_h.lineEdit().clear()
    #         self.combobox_resolution.setCurrentIndex(-1)
    #         self.spinbox_w.setEnabled(False)
    #         self.spinbox_h.setEnabled(False)
    #         self.combobox_resolution.setEnabled(False)


    def enable_conversion(self, model: NnModel) -> None:
        """Called when a new model is parsed
        """
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
            self.checkbox_dynamic.setChecked(False)
            self.checkbox_static.setChecked(False)
            self.setEnabled(False)
            return

        # Enable conversion
        self.spinbox_opset.lineEdit().setText(str(self.spinbox_opset.value()))
        self.spinbox_opset.lineEdit().setReadOnly(False)
        self.spinbox_opset.setReadOnly(False)
        self.spinbox_opset.setEnabled(True)

        # Datatype
        self.radiobutton_fp32.setChecked(True)
        if "fp16" in model.arch.dtypes:
            self.radiobutton_fp16.setCheckable(True)
            self.radiobutton_fp32.setCheckable(True)
        else:
            self.radiobutton_fp16.setCheckable(False)
            self.radiobutton_fp32.setCheckable(False)

        # Shape strategy
        self.shape_strategy == 'static' if 'static' in model.shape_strategy.type else 'dynamic'

        is_dynamic: bool = bool(self.shape_strategy == 'dynamic')
        self.checkbox_dynamic.setChecked(is_dynamic)
        self.checkbox_static.setChecked(not is_dynamic)

        # self.update_size_widgets(self.shape_strategy)
        # if self.shape_strategy == 'static':
            # self.spinbox_h.lineEdit().setText(str(self.spinbox_h.value()))
            # self.spinbox_w.lineEdit().setText(str(self.spinbox_w.value()))
            # self.spinbox_w.setValue(model.shape_strategy.opt_size[0])
            # self.spinbox_h.setValue(model.shape_strategy.opt_size[1])
            # self.update_resolution_text()

        # for w in (self.spinbox_w, self.spinbox_h):
        #     w.lineEdit().setReadOnly(is_dynamic)
        #     w.setReadOnly(is_dynamic)
        #     w.setEnabled(not is_dynamic)


        # # Use the size constraints to set min/max values
        # size_constraint: SizeConstraint = model.arch.size_constraint
        # if size_constraint is not None:
        #     self.spinbox_w.setMinimum(size_constraint.min[0])
        #     self.spinbox_w.setSingleStep(size_constraint.modulo)
        #     self.spinbox_h.setMinimum(size_constraint.min[1])
        #     self.spinbox_h.setSingleStep(size_constraint.modulo)
        # else:
        #     self.spinbox_w.setMinimum(8)
        #     self.spinbox_w.setSingleStep(1)
        #     self.spinbox_h.setMinimum(8)
        #     self.spinbox_h.setSingleStep(1)



        # self.setEnabled(True)
        # Inform other widgets that the size has been modified
        # self.size_modified(-1)

