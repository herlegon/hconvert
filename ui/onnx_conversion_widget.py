from __future__ import annotations
from pprint import pprint
from typing import Type
from hutils import red
from hwidgets import HStyle
from pynnlib import (
    NnModel,
    NnPytorchArchitecture,
    NnFrameworkType,
    SizeConstraint,
)
from .common import (
    DEFAULT_SIZE,
    PREDEFINED_SIZE,
    predefined_shapes_inv,
    ShapeStrategyName,
    ONNX_DEFAULT_CONVERSION_SETTINGS,
)
from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QAbstractSpinBox,
    QComboBox,
    QCheckBox,
    QRadioButton,
    QSpinBox,
)
from .designer.ui_onnx_conversion_widget import Ui_OnnxConversionWidget



class OnnxConversionWidget(QWidget, Ui_OnnxConversionWidget):

    def __init__(self, parent):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._saved_shape: tuple[int, int] = DEFAULT_SIZE
        self.shape_strategy: ShapeStrategyName = 'dynamic'
        self._tensorrt_static_shape: tuple[int, int] = (0, 0)

        self._editable_widgets: list[type[QWidget]] = [
            *self.findChildren(QComboBox),
            *self.findChildren(QCheckBox),
            *self.findChildren(QSpinBox),
            *self.findChildren(QRadioButton),
        ]
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
        self.spinbox_opset.setValue(ONNX_DEFAULT_CONVERSION_SETTINGS['version'])

        _dtypes: dict[str, tuple[str, str]] = {
            'fp32': ("fp32", "float32"),
            'fp16': ("fp16", "float16"),
            'bf16': ("bf16", "bfloat16"),
        }
        self.h_button_group_dtypes.set_buttons(_dtypes)

        _shapes: dict[str, tuple[str, str]] = {
            'dynamic': ("dynamic", "Input size is not a constraint"),
            'static': ("static", "Input image size must be the one specified below"),
        }
        self.h_button_group_shapes.set_buttons(_shapes)
        self.spinbox_w.setValue(ONNX_DEFAULT_CONVERSION_SETTINGS['shape'][0])
        self.spinbox_h.setValue(ONNX_DEFAULT_CONVERSION_SETTINGS['shape'][1])
        self.update_resolution_text()
        self.shape_strategy_changed(True)

        self.adjustSize()

        self.h_button_group_shapes.signal_selection_changed.connect(
            self.shape_strategy_changed
        )

        self.spinbox_w.valueChanged.connect(self.size_modified)
        self.spinbox_h.valueChanged.connect(self.size_modified)
        self.combobox_resolution.currentIndexChanged.connect(self.resolution_selected)


    def editable_widgets(self) -> list[Type[QWidget]]:
        return self._editable_widgets


    def block_signals(self, b: bool) -> None:
        for w in self._editable_widgets:
            w.blockSignals(b)


    def clear(self) -> None:
        self.block_signals(True)
        self.spinbox_opset.clear()
        spinbox_width = 50
        self.h_button_group_shapes.set_current_button('dynamic')

        self.spinbox_opset.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        for b in self.h_button_group_dtypes.buttons():
            b.setChecked(False)

        self.spinbox_w.lineEdit().clear()
        self.spinbox_h.lineEdit().clear()
        self.spinbox_w.clear()
        self.spinbox_h.clear()

        self.spinbox_opset.setMinimumWidth(spinbox_width)
        self.spinbox_opset.setMaximumWidth(spinbox_width)
        self.block_signals(False)


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


    def update_capabilities(self, model: NnModel) -> bool:
        """Called when a new model is parsed
        """
        if model.framework.type != NnFrameworkType.PYTORCH:
            return False

        to_onnx = model.arch.to_onnx
        if to_onnx is not None and isinstance(to_onnx, tuple):
            print(red("to_onnx has a tuple"))
            print(model.arch)
        if not (
            to_onnx is not None
            and to_onnx.dtypes
            and to_onnx.shape_strategy_types
        ):
            return False

        arch: NnPytorchArchitecture = model.arch

        # Datatypes
        for b in self.h_button_group_dtypes.buttons():
            b.setEnabled(bool(b.key in arch.to_onnx.dtypes))
        for d in ('fp32', 'fp16', 'bf16'):
            if d in arch.to_onnx.dtypes:
                self.h_button_group_dtypes.set_current_button(d)
                break


        # Shape strategy
        for s in ('static', 'dynamic'):
            b = self.h_button_group_shapes.get_button(s)
            if s in arch.to_onnx.shape_strategy_types:
                b.setEnabled(True)
                b.setChecked(True)
            else:
                b.setEnabled(False)

        # Use the size constraints to set min/max values
        size_constraint: SizeConstraint = arch.size_constraint
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

        # clear spinbox/combobox if dynamic
        if self.h_button_group_shapes.current_button().key == 'dynamic':
            self.spinbox_w.clear()
            self.spinbox_h.clear()
            self.combobox_resolution.setCurrentIndex(-1)
        else:
            self.size_modified(-1)

        self.block_signals(False)
        return True


    def shape_strategy_changed(self, state: bool) -> None:
        """User action to set from/to dynamic, fixed/static
        """
        self.block_signals(True)
        to_static = self.h_button_group_shapes.current_button().key == 'static'

        if  self.shape_strategy == 'static' and not to_static:
            # static -> dynamic
            self.save_current_size()

        elif self.shape_strategy != 'static' and to_static:
            # dynamic -> static
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
        self.block_signals(False)


    def size_modified(self, value: int) -> None:
        """User modified width/height
        """
        self.combobox_resolution.blockSignals(True)
        self.update_resolution_text()
        self.spinbox_w.lineEdit().deselect()
        self.spinbox_h.lineEdit().deselect()
        self.combobox_resolution.blockSignals(False)


    def resolution_selected(self, index: int) -> None:
        """User modified resolution
        Update the size widgets
        """
        current_text: str = self.combobox_resolution.currentText()
        if current_text:
            w, h = PREDEFINED_SIZE[current_text]
            self.spinbox_w.blockSignals(True)
            self.spinbox_h.blockSignals(True)
            self.spinbox_w.setValue(w)
            self.spinbox_h.setValue(h)
            self.spinbox_w.lineEdit().deselect()
            self.spinbox_h.lineEdit().deselect()
            self.spinbox_w.blockSignals(False)
            self.spinbox_h.blockSignals(False)


    def values(self) -> dict[str, str | int | tuple[int, int]]:
        settings: dict[str, str | int | tuple[int, int]] = {
            'opset': self.spinbox_opset.value(),
            'dtype': self.h_button_group_dtypes.current_button().key,
            'shape_strategy': self.h_button_group_shapes.current_button().key,
            'shape': (self.spinbox_w.value(), self.spinbox_h.value()),
        }
        return settings
