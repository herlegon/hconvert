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
    event_shape_strategy_changed = Signal(str, object)

    def __init__(self, parent, editable: bool | None = None):
        super().__init__(parent)
        self.setupUi(self)
        self.editable: bool | None = editable
        self._saved_shape: tuple[int] = DEFAULT_SIZE
        self.shape_strategy: ShapeStrategyName = 'dynamic'
        self._tensorrt_static_shape: tuple[int, int] = (0, 0)

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
        self.combobox_resolution.addItems(list(PREDEFINED_SIZE.keys()))
        self.combobox_resolution.setCurrentIndex(-1)

        self.clear()
        self.setEnabled(False)
        self.adjustSize()

        self.radiobutton_fp16.toggled.connect(self.datatype_changed)
        self.checkbox_static.toggled.connect(self.shape_strategy_changed)
        # self.checkbox_dynamic.toggled.connect(self.shape_strategy_changed)

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
        self.checkbox_dynamic.setChecked(False)
        self.checkbox_static.setChecked(False)

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
            self.checkbox_static.setChecked(True)
            self.lineedit_w.setText(str(model.shape_strategy.opt_size[0]))
            self.lineedit_h.setText(str(model.shape_strategy.opt_size[1]))

        else:
            self.checkbox_dynamic.setChecked(True)

        if 'fp32' in model.dtypes and 'fp16' in model.dtypes:
            print(red("ERRROR, onnx has both fp16 and fp32"))

        self.setEnabled(False)



    def datatype_changed(self, state: bool) -> None:
        print("datatype_changed to")



    def update_resolution_text(self) -> None:
        w, h = self.spinbox_w.value(), self.spinbox_h.value()
        t = predefined_shapes_inv.get("x".join(map(str, (w, h))), "")
        self.combobox_resolution.setCurrentIndex(
            self.combobox_resolution.findText(t)
        )



    def save_current_size(self) -> None:
        self._saved_shape = (
            self.spinbox_w.value(), self.spinbox_h.value()
        )



    def restore_size(self, ignore_opt: bool = False) -> None:
        self.spinbox_w.setValue(self._saved_shape[0])
        self.spinbox_h.setValue(self._saved_shape[1])
        self.update_resolution_text()



    def update_size_widgets(self, strategy: ShapeStrategyName) -> None:
        if strategy == 'static':
            self.spinbox_w.setEnabled(True)
            self.spinbox_h.setEnabled(True)
            self.combobox_resolution.setEnabled(True)

        else:
            self.spinbox_w.lineEdit().clear()
            self.spinbox_h.lineEdit().clear()
            self.combobox_resolution.setCurrentIndex(-1)
            self.spinbox_w.setEnabled(False)
            self.spinbox_h.setEnabled(False)
            self.combobox_resolution.setEnabled(False)


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
        self.block_signals(True)
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

        self.update_size_widgets(self.shape_strategy)
        if self.shape_strategy == 'static':
            # self.spinbox_h.lineEdit().setText(str(self.spinbox_h.value()))
            # self.spinbox_w.lineEdit().setText(str(self.spinbox_w.value()))
            self.spinbox_w.setValue(model.shape_strategy.opt_size[0])
            self.spinbox_h.setValue(model.shape_strategy.opt_size[1])
            self.update_resolution_text()

        # for w in (self.spinbox_w, self.spinbox_h):
        #     w.lineEdit().setReadOnly(is_dynamic)
        #     w.setReadOnly(is_dynamic)
        #     w.setEnabled(not is_dynamic)


        # Use the size constraints to set min/max values
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
        # Inform other widgets that the size has been modified
        self.size_modified(-1)
        self.block_signals(False)



    def shape_strategy_changed(self, state: bool) -> None:
        """User action to set from/to dynamic, fixed/static
        """
        if not self.editable:
            return
        self.block_signals(True)
        to_static = self.checkbox_static.isChecked()
        print(f"current strategy: {self.shape_strategy}, to static: {to_static}")


        if  self.shape_strategy == 'static' and not to_static:
            # static -> dynamic
            print("onnx: static -> dynamic")
            self.save_current_size()

        elif self.shape_strategy != 'static' and to_static:
            # dynamic -> static
            print("onnx: dynamic -> static")
            self.restore_size()
            # Use the shape set by tensorRT
            if all(self._tensorrt_static_shape):
                self.spinbox_w.setValue(self._tensorrt_static_shape[0])
                self.spinbox_h.setValue(self._tensorrt_static_shape[1])
                self.update_resolution_text()

        else:
            self.block_signals(False)
            return

        self._current_size = (self.spinbox_w.value(), self.spinbox_h.value())
        self.shape_strategy = 'static' if to_static else 'dynamic'
        self.update_size_widgets(strategy=self.shape_strategy)
        self.event_shape_strategy_changed.emit(self.shape_strategy, self._current_size)

        self.block_signals(False)



    def size_modified(self, value: int) -> None:
        """User modified width/height
        """
        self.combobox_resolution.blockSignals(True)
        self.update_resolution_text()
        self.spinbox_w.lineEdit().deselect()
        self.spinbox_h.lineEdit().deselect()
        if self.shape_strategy == 'static':
            # send a signal to other widgets, size doesn't matter
            # but let's send something  coherent
            self.event_shape_strategy_changed.emit(
                'static', (self.spinbox_w.value(), self.spinbox_h.value())
            )
        self.combobox_resolution.blockSignals(False)



    def resolution_selected(self, index: int) -> None:
        """User modified resolution
        Update the size widgets
        """
        current_text: str = self.combobox_resolution.currentText()
        w, h = PREDEFINED_SIZE[current_text]
        self.spinbox_w.blockSignals(True)
        self.spinbox_h.blockSignals(True)
        self.spinbox_w.setValue(w)
        self.spinbox_h.setValue(h)
        self.spinbox_w.lineEdit().deselect()
        self.spinbox_h.lineEdit().deselect()

        if self.shape_strategy == 'static':
            # send a signal to other widgets, size doesn't matter
            # but let's send something  coherent
            self.event_shape_strategy_changed.emit('static', (w, h))

        self.spinbox_w.blockSignals(False)
        self.spinbox_h.blockSignals(False)


    def tensorrt_static_shape_modified(self, size: tuple[int, int]) -> None:
        print(f"save tensorrt shape: {size}")
        self._tensorrt_static_shape = size


    def values(self) -> dict[str, str | tuple[int, int]]:
        values: dict[str, str | int | tuple[int, int]] = {
            'opset': self.spinbox_opset.value(),
            'datatype': 'fp32' if self.radiobutton_fp32.isChecked() else 'fp16',
            'shape_strategy': 'static' if self.checkbox_static.isChecked() else 'dynamic',
            'shape': (self.spinbox_w.value(), self.spinbox_h.value()),
        }
        return values