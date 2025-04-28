from __future__ import annotations
from functools import partial
from pynnlib import (
    NnModel,
    NnFrameworkType,
    PyTorchModel,
)

from PySide6.QtCore import (
    QCoreApplication,
    Signal,
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
    QSpinBox,
)

from .designer.ui_tensorrt_conversion_widget import Ui_TensorRTConversionWidget
from .common import (
    DEFAULT_SIZE,
    ShapeStrategyName,
    PREDEFINED_SIZE,
    predefined_shapes_inv,
)


class TensorRTConversionWidget(QWidget, Ui_TensorRTConversionWidget):
    event_static_shape_modified: Signal = Signal(object)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._gpus = dict[str, int]
        self.shape_strategy: ShapeStrategyName = 'dynamic'
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": DEFAULT_SIZE,
            "opt": DEFAULT_SIZE,
            "max": DEFAULT_SIZE,
        }

        self.editable_widgets: tuple[type[QWidget]] = (
            self.combobox_gpu,
            self.checkbox_fp16,
            self.checkbox_bf16,
            self.checkbox_dynamic,
            self.checkbox_fixed,
            self.spinbox_w_min,
            self.spinbox_h_min,
            self.combobox_resolution_min,
            self.spinbox_w_opt,
            self.spinbox_h_opt,
            self.combobox_resolution_opt,
            self.spinbox_w_max,
            self.spinbox_h_max,
            self.combobox_resolution_max,
        )

        self.size_widgets: tuple[tuple[QSpinBox, QSpinBox, QComboBox]] = (
            (self.spinbox_w_min, self.spinbox_h_min, self.combobox_resolution_min),
            (self.spinbox_w_opt, self.spinbox_h_opt, self.combobox_resolution_opt),
            (self.spinbox_w_max, self.spinbox_h_max, self.combobox_resolution_max),
        )

        for sb_w, sb_h, cb_r in self.size_widgets:
            sb_w.setValue(DEFAULT_SIZE[0])
            sb_h.setValue(DEFAULT_SIZE[1])
            cb_r.clear()
            cb_r.addItems(list(PREDEFINED_SIZE.keys()))
            cb_r.setCurrentIndex(-1)

        self.clear()
        self.setEnabled(False)
        self.adjustSize()

        # Signals
        self.checkbox_fixed.toggled.connect(self.shape_strategy_changed)
        for sw in self.size_widgets:
            # w, h, resolution
            sb_w, sb_h, cb_r = sw
            sb_w.valueChanged.connect(partial(self.size_modified, sw))
            sb_h.valueChanged.connect(partial(self.size_modified, sw))
            cb_r.currentIndexChanged.connect(partial(self.resolution_selected, sw))



    def set_available_gpus(self, gpus: dict[str, int]) -> None:
        self.combobox_gpu.clear()
        self.combobox_gpu.addItems(list(gpus.keys()))
        self._gpus = gpus



    def block_signals(self, b: bool) -> None:
        for w in self.editable_widgets:
            w.blockSignals(b)



    def clear(self) -> None:
        self.block_signals(True)

        self.checkbox_fp16.setChecked(False)
        self.checkbox_bf16.setChecked(False)

        self.checkbox_dynamic.setChecked(False)
        self.checkbox_fixed.setChecked(False)

        for sb_w, sb_h, cb_r in self.size_widgets:
            sb_w.lineEdit().clear()
            sb_w.clear()
            sb_h.lineEdit().clear()
            sb_h.clear()
            cb_r.setCurrentIndex(-1)

        self.block_signals(False)



    def enable_conversion(self, model: NnModel) -> None:
        self.clear()

        # PyTorch/ONNX only
        # Conversion must be possible for the arch
        # Has a Nvidia GPU
        print(model.framework.type)
        print(model.framework.type)
        is_torch_to_tensorrt_possible = bool(
            model.framework.type == NnFrameworkType.PYTORCH
            and model.arch.to_onnx is not None
        )
        is_onnx_to_tensorrt_possible = bool(
            model.framework.type == NnFrameworkType.ONNX
            and model.arch.to_tensorrt is not None
        )
        print(f"enable_conversion")
        print(f"  torch-> tensorrt: {is_torch_to_tensorrt_possible}")
        print(f"  onnx-> tensorrt: {is_onnx_to_tensorrt_possible}")


        if not is_torch_to_tensorrt_possible and not is_onnx_to_tensorrt_possible:
            print("not supported")
            self.setEnabled(False)
            return

        # Enable conversion
        print(f"enable tenbsorrt, default to onnx or dynamic: {model.shape_strategy}")
        self.block_signals(True)
        # Use the default shape strategy
        self.save_current_sizes()
        if model.framework.type == NnFrameworkType.ONNX:
            self.shape_strategy = model.shape_strategy.type
            self.constraint_shape_strategy(
                strategy=self.shape_strategy,
                size=model.shape_strategy.opt_size
            )
            if self.shape_strategy == 'static':
                self.checkbox_fixed.setChecked(True)
                self.checkbox_dynamic.setCheckable(False)
                self.checkbox_dynamic.setEnabled(False)

        else:
            self.shape_strategy = 'dynamic'
            self.checkbox_dynamic.setEnabled(False)
            self.spinbox_w_opt.setValue(self.previous_shapes['opt'][0])
            self.spinbox_h_opt.setValue(self.previous_shapes['opt'][1])
            self.update_resolution_text(index=1)

        self.update_widgets(shape_strategy=self.shape_strategy)
        is_dynamic: bool = bool(self.shape_strategy == 'dynamic')
        self.checkbox_dynamic.setChecked(is_dynamic)
        self.checkbox_fixed.setChecked(not is_dynamic)

        self.setEnabled(True)
        self.block_signals(False)


    def save_current_sizes(self) -> None:
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": (self.spinbox_w_min.value(), self.spinbox_h_min.value()),
            "opt": (self.spinbox_w_opt.value(), self.spinbox_h_opt.value()),
            "max": (self.spinbox_w_max.value(), self.spinbox_h_max.value()),
        }

    def set_opt_modifications_enabled(self, enable: bool) -> None:
        self.spinbox_w_opt.setEnabled(enable)
        self.spinbox_h_opt.setEnabled(enable)
        self.combobox_resolution_opt.setEnabled(enable)



    def update_widgets(self, shape_strategy: ShapeStrategyName) -> None:
        print(f"update widgets with strategy: {shape_strategy}")
        if shape_strategy == 'dynamic':
            self.spinbox_w_min.setValue(self.previous_shapes['min'][0])
            self.spinbox_h_min.setValue(self.previous_shapes['min'][1])
            self.spinbox_w_max.setValue(self.previous_shapes['max'][0])
            self.spinbox_h_max.setValue(self.previous_shapes['max'][1])

            # Enable all size modifications
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                sb_w.setEnabled(True)
                sb_h.setEnabled(True)
                cb_r.setEnabled(True)
            self.update_resolution_text()

        else:
            sb_w, sb_h, cb_r = self.size_widgets[1]
            self.update_resolution_text()
            if shape_strategy == 'static':
                self.checkbox_fixed.setText('static')
                self.set_opt_modifications_enabled(False)
            else:
                sb_w.setValue(self.previous_shapes['opt'][0])
                sb_h.setValue(self.previous_shapes['opt'][1])
                self.checkbox_fixed.setText('fixed')
                self.set_opt_modifications_enabled(True)
                self.checkbox_dynamic.setCheckable(True)
                self.checkbox_dynamic.setEnabled(True)

            # Disable min/max shapes
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                if i == 1:
                    continue
                sb_w.lineEdit().clear()
                sb_h.lineEdit().clear()
                cb_r.setCurrentIndex(-1)
                sb_w.setEnabled(False)
                sb_h.setEnabled(False)
                cb_r.setEnabled(False)



    def shape_strategy_changed(self, state: bool) -> None:
        self.block_signals(True)
        to_fixed = self.checkbox_fixed.isChecked()
        print(f"current strategy: {self.shape_strategy}, to fixed: {to_fixed}")

        if self.shape_strategy != 'dynamic' and not to_fixed:
            # fixed/static -> dynamic
            self.shape_strategy = 'dynamic'
            self.update_widgets(shape_strategy='dynamic')


        elif self.shape_strategy == 'dynamic' and to_fixed:
            # dynamic -> fixed
            # Save to restor min/max values when changing from fixed to dynamic
            self.save_current_sizes()
            self.update_widgets('fixed')
            self.shape_strategy = 'fixed'

        print(f"  new strategy: {self.shape_strategy}")
        self.block_signals(False)



    def update_resolution_text(self, index: int = -1) -> None:
        print("update_resolution_text")
        widgets = (
            self.size_widgets if index == -1 else (self.size_widgets[index],)
        )
        for sb_w, sb_h, cb_r in widgets:
            t = predefined_shapes_inv.get(
                "x".join(map(str, (sb_w.value(), sb_h.value()))), ""
            )
            cb_r.setCurrentIndex(cb_r.findText(t))



    def size_modified(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value: int = -1) -> None:
        print("update_resolution_text")
        sb_w, sp_h, cb_r = sw
        cb_r.blockSignals(True)
        size = (sb_w.value(), sp_h.value())
        t = predefined_shapes_inv.get("x".join(map(str, size)), "")
        cb_r.setCurrentIndex(cb_r.findText(t))
        sb_w.lineEdit().deselect()
        sp_h.lineEdit().deselect()

        # modify Onnx conversion widget if is static
        if self.shape_strategy in ('fixed', 'static'):
            self.event_static_shape_modified.emit(size)

        cb_r.blockSignals(False)



    def resolution_selected(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value) -> None:
        print(f"resolution_selected: {self.shape_strategy}")
        sb_w, sp_h, cb_r = sw
        current_text: str = cb_r.currentText()
        w, h = PREDEFINED_SIZE[current_text]

        sb_w.blockSignals(True)
        sp_h.blockSignals(True)
        sb_w.setValue(w)
        sp_h.setValue(h)
        sb_w.lineEdit().deselect()
        sp_h.lineEdit().deselect()
        print(f"  resolution_selected: {self.shape_strategy}")
        # if self.shape_strategy in ('fixed', 'static'):

        #     self.event_static_shape_modified.emit(
        #         predefined_shapes[self.combobox_resolution_opt.currentText()]
        #     )

        sb_w.blockSignals(False)
        sp_h.blockSignals(False)



    def constraint_shape_strategy(
        self,
        strategy: ShapeStrategyName,
        size: tuple[int, int],
    ) -> None:
        print(f" tensorrt constraint_shape_strategy: {strategy}")
        if self.shape_strategy == 'dynamic':
            # Change from dynamic to fixed/static
            if strategy == 'static':
                self.checkbox_fixed.setChecked(True)
                self.checkbox_dynamic.setCheckable(False)
                self.checkbox_dynamic.setEnabled(False)
                self.shape_strategy = strategy

            elif strategy == 'fixed':
                self.checkbox_fixed.setText('fixed')
                self.checkbox_fixed.setChecked(True)
                self.checkbox_dynamic.setCheckable(True)
                self.checkbox_dynamic.setEnabled(True)
                self.shape_strategy = strategy

        if strategy == 'dynamic':
            self.shape_strategy = strategy
            self.checkbox_fixed.setText('fixed')
            self.checkbox_dynamic.setEnabled(True)
            self.checkbox_dynamic.setCheckable(True)
        else:
            self.checkbox_fixed.setText('static')

        # When in static, the size is constrainted by the ONNX model
        if strategy != 'dynamic':
            self.spinbox_w_opt.setValue(size[0])
            self.spinbox_h_opt.setValue(size[1])
            self.set_opt_modifications_enabled(False)
            self.update_resolution_text(index=1)

        else:
            self.set_opt_modifications_enabled(True)



