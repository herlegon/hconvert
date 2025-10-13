from __future__ import annotations
from functools import partial
from typing import Literal
from pynnlib import (
    NnModel,
    NnFrameworkType,
)
from PySide6.QtCore import (
    Signal,
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QCheckBox,
    QComboBox,
    QSpinBox,
)

from .designer.ui_tensorrt_conversion_widget import Ui_TensorRTConversionWidget
from .common import (
    DEFAULT_SIZE,
    PREDEFINED_SIZE,
    predefined_shapes_inv,
    ShapeStrategyName,
)

from pynnlib.utils.p_print import *

class TensorRTConversionWidget(QWidget, Ui_TensorRTConversionWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._gpus: dict[str, int] = {}
        self.shape_strategy: ShapeStrategyName = 'dynamic'
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": DEFAULT_SIZE,
            "opt": DEFAULT_SIZE,
            "max": DEFAULT_SIZE,
        }
        self._strategy_constraint: Literal['dynamic', 'static', 'fixed'] = 'fixed'

        self.editable_widgets: tuple[type[QWidget]] = (
            *self.findChildren(QComboBox),
            *self.findChildren(QCheckBox),
            *self.findChildren(QSpinBox),
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
        self.adjustSize()

        # Signals
        self.radiobutton_fixed.toggled.connect(self.shape_strategy_changed)
        self.radiobutton_static.toggled.connect(self.shape_strategy_changed)
        for sw in self.size_widgets:
            # w, h, resolution
            sb_w, sb_h, cb_r = sw
            sb_w.valueChanged.connect(partial(self.size_modified, sw))
            sb_h.valueChanged.connect(partial(self.size_modified, sw))
            cb_r.currentIndexChanged.connect(partial(self.resolution_selected, sw))


    def is_selected(self) -> bool:
        return self.isEnabled()


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

        self.radiobutton_dynamic.setChecked(False)
        self.radiobutton_fixed.setChecked(False)

        for sb_w, sb_h, cb_r in self.size_widgets:
            sb_w.lineEdit().clear()
            sb_w.clear()
            sb_h.lineEdit().clear()
            sb_h.clear()
            cb_r.setCurrentIndex(-1)

        self.block_signals(False)



    def update_resolution_text(self, index: int = -1) -> None:
        widgets = (
            self.size_widgets if index == -1 else (self.size_widgets[index],)
        )
        for sb_w, sb_h, cb_r in widgets:
            size = (sb_w.value(), sb_h.value())
            if all(size):
                t = predefined_shapes_inv.get(
                    "x".join(map(str, size)), ""
                )
                cb_r.setCurrentIndex(cb_r.findText(t))



    def update_opt_resolution_text(self) -> None:
        self.update_resolution_text(index=1)



    def update_size_widgets(self, strategy: ShapeStrategyName) -> None:
        if strategy == 'static':
            self.radiobutton_static.setChecked(True)
        elif strategy == 'fixed':
            self.radiobutton_fixed.setChecked(True)
        else:
            self.radiobutton_dynamic.setCheckable(True)

        if strategy == 'dynamic':
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                sb_w.setEnabled(True)
                sb_h.setEnabled(True)
                cb_r.setEnabled(True)
        else:
            # Disable min/max shapes
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                if i == 1 and strategy != 'static':
                    continue
                sb_w.lineEdit().clear()
                sb_h.lineEdit().clear()
                cb_r.setCurrentIndex(-1)
                sb_w.setEnabled(False)
                sb_h.setEnabled(False)
                cb_r.setEnabled(False)



    def save_current_sizes(self) -> None:
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": (self.spinbox_w_min.value(), self.spinbox_h_min.value()),
            "opt": (self.spinbox_w_opt.value(), self.spinbox_h_opt.value()),
            "max": (self.spinbox_w_max.value(), self.spinbox_h_max.value()),
        }



    def restore_sizes(self, ignore_opt: bool = False) -> None:
        self.spinbox_w_min.setValue(self.previous_shapes['min'][0])
        self.spinbox_h_min.setValue(self.previous_shapes['min'][1])
        self.spinbox_w_max.setValue(self.previous_shapes['max'][0])
        self.spinbox_h_max.setValue(self.previous_shapes['max'][1])
        if not ignore_opt:
            self.spinbox_w_opt.setValue(self.previous_shapes['opt'][0])
            self.spinbox_h_opt.setValue(self.previous_shapes['opt'][1])
        self.update_resolution_text()



    def enable_conversion(self, model: NnModel) -> None:
        """Called when a new model is parsed
        """
        self.clear()

        # PyTorch/ONNX only
        # Conversion must be possible for the arch
        # Has a Nvidia GPU
        if model is None:
            self.clear()
            return

        is_torch_to_tensorrt_possible = bool(
            model.framework.type == NnFrameworkType.PYTORCH
            and model.arch.to_onnx is not None
        )
        is_onnx_to_tensorrt_possible = bool(
            model.framework.type == NnFrameworkType.ONNX
            and model.arch.to_tensorrt is not None
        )
        print(red("TODO: sysinfo"))
        print(lightcyan(f"tensorrt_conversion_widget: enable_conversion(model)"))
        print(f"  torch-> tensorrt: {is_torch_to_tensorrt_possible}")
        print(f"  onnx-> tensorrt: {is_onnx_to_tensorrt_possible}")
        # if not is_torch_to_tensorrt_possible and not is_onnx_to_tensorrt_possible:
        #     print("  not supported")
        #     self.setEnabled(False)
        #     return

        # Enable conversion
        self.block_signals(True)

        # Use the default shape strategy
        self.save_current_sizes()
        if model.framework.type == NnFrameworkType.ONNX:
            self._strategy_constraint = 'static' if model.shape_strategy.type == 'static' else 'fixed'

            self.shape_strategy = model.shape_strategy.type
            self.update_size_widgets(self.shape_strategy)
            if self.shape_strategy == 'static':
                for r in (self.radiobutton_fixed, self.radiobutton_dynamic):
                    r.setCheckable(False)
                    r.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                    r.setEnabled(False)

                    self.radiobutton_static.setCheckable(False)
                    self.radiobutton_static.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                    self.radiobutton_static.setChecked(True)

            else:
                for r in (self.radiobutton_fixed, self.radiobutton_dynamic):
                    r.setEnabled(True)
                    r.setCheckable(True)
                    r.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

                    self.radiobutton_static.setCheckable(False)
                    self.radiobutton_static.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                    self.radiobutton_static.setEnabled(False)

        elif model.framework.type == NnFrameworkType.PYTORCH:
            # Set default strategy to dynamic
            #

            self.shape_strategy = 'dynamic'
            for r in (
                self.radiobutton_static,
                self.radiobutton_fixed,
                self.radiobutton_dynamic,
            ):
                r.setEnabled(True)
                r.setCheckable(True)
                r.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        else:
            raise NotImplementedError(f"{model.framework.type}")

        # Fill the size values
        if self.shape_strategy in ('fixed', 'static'):
            self.spinbox_w_opt.setValue(model.shape_strategy.opt_size[0])
            self.spinbox_h_opt.setValue(model.shape_strategy.opt_size[1])
            self.update_opt_resolution_text()

        elif self.shape_strategy == 'dynamic':
            self._strategy_constraint = 'fixed'
            self.save_current_sizes()
            self.update_size_widgets(self.shape_strategy)
            self.update_resolution_text()
            self.restore_sizes()

        if self.shape_strategy == 'dynamic':
            self.radiobutton_dynamic.setChecked(True)
        elif self.shape_strategy == 'fixed':
            self.radiobutton_fixed.setChecked(True)
        elif self.shape_strategy == 'static':
            self.radiobutton_fixed.setChecked(True)

        self.setEnabled(True)
        self.block_signals(False)



    def shape_strategy_changed(self) -> None:
        """User action to set from/to dynamic, fixed/static
        """
        self.block_signals(True)
        current_strategy: str = self.shape_strategy
        to_fixed: bool = self.radiobutton_fixed.isChecked()
        to_static: bool = self.radiobutton_static.isChecked()
        print(f"current strategy: {current_strategy}, to fixed: {to_fixed}, to static: {to_static}")

        if current_strategy != 'dynamic' and not to_fixed and not to_static:
            # fixed/static -> dynamic
            print("shape_strategy_changed: fixed/static -> dynamic")
            self.shape_strategy = 'dynamic'
            self.update_size_widgets(strategy=self.shape_strategy)
            self.restore_sizes(ignore_opt=True)

        elif current_strategy == 'dynamic' and (to_fixed or to_static):
            print("shape_strategy_changed: dynamic -> fixed")
            # dynamic -> fixed
            # Save to restor min/max values when changing from fixed to dynamic
            self.save_current_sizes()
            self.shape_strategy = 'static' if to_static else 'fixed'
            self.update_size_widgets(strategy=self.shape_strategy)
            # self.restore_sizes(ignore_opt=True)

        print(lightgreen(f"  new strategy: {self.shape_strategy}"))
        self.block_signals(False)



    def size_modified(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value: int = -1) -> None:
        """User modified width/height
        """
        sb_w, sp_h, cb_r = sw
        cb_r.blockSignals(True)
        size = (sb_w.value(), sp_h.value())
        t = predefined_shapes_inv.get("x".join(map(str, size)), "")
        cb_r.setCurrentIndex(cb_r.findText(t))
        sb_w.lineEdit().deselect()
        sp_h.lineEdit().deselect()

        # Emit a signal to infor Onnx conversion that the
        # current static/fixed shape has been modified
        # It will be used to set the default size value for other widgets

        cb_r.blockSignals(False)



    def resolution_selected(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value) -> None:
        """User modified resolution
        Update the size widgets
        """
        sb_w, sp_h, cb_r = sw
        current_text: str = cb_r.currentText()
        w, h = PREDEFINED_SIZE[current_text]

        sb_w.blockSignals(True)
        sp_h.blockSignals(True)
        sb_w.setValue(w)
        sp_h.setValue(h)
        sb_w.lineEdit().deselect()
        sp_h.lineEdit().deselect()

        # Emit a signal to infor Onnx conversion that the
        # current static/fixed shape has been modified
        # It will be used to set the default size value for other widgets

        sb_w.blockSignals(False)
        sp_h.blockSignals(False)



    def set_opt_modifications_enabled(self, enable: bool) -> None:
        self.spinbox_w_opt.setEnabled(enable)
        self.spinbox_h_opt.setEnabled(enable)
        self.combobox_resolution_opt.setEnabled(enable)



    # def constraint_shape_strategy(
    #     self,
    #     strategy: ShapeStrategyName,
    #     size: tuple[int, int],
    # ) -> None:
    #     print(f" tensorrt constraint_shape_strategy: {strategy}, size: {size}, current strategy: {self.shape_strategy}")
    #     if strategy != self.shape_strategy:
    #         print("  update")
    #         self.block_signals(True)
    #         # Update constraint
    #         self._strategy_constraint = (
    #             'static' if strategy == 'static' else 'fixed'
    #         )
    #         # Modify shape strategy
    #         if strategy == 'static':
    #             print("force to static")
    #             self.save_current_sizes()
    #             self.shape_strategy = 'static'

    #         elif self.shape_strategy != 'dynamic':
    #             print("force to fixed")
    #             self.shape_strategy = 'fixed'

    #         self.update_size_widgets(strategy=self.shape_strategy)
    #         if self.shape_strategy in ('static', 'fixed'):
    #             self.spinbox_w_opt.setValue(size[0])
    #             self.spinbox_h_opt.setValue(size[1])
    #             self.update_opt_resolution_text()

    #         # When in static, the size is constrainted by the ONNX model
    #         if self.shape_strategy == 'static':
    #             self.set_opt_modifications_enabled(False)
    #         else:
    #             self.set_opt_modifications_enabled(True)
    #         self.block_signals(False)

    #     if self.shape_strategy == 'static':
    #         self.block_signals(True)
    #         self.spinbox_w_opt.setValue(size[0])
    #         self.spinbox_h_opt.setValue(size[1])
    #         self.update_opt_resolution_text()
    #         self.block_signals(False)


    def validate_shapes(self) -> None:
        """Verify that shapes are consistent.
            Emit a signal if not the case.
        """
        wrong_values: list[QSpinBox] = []
        if self.shape_strategy == 'dynamic':
            w_min, w_opt, w_max = (
                self.spinbox_w_min.value(),
                self.spinbox_w_opt.value(),
                self.spinbox_w_max.value(),
            )
            if not w_min <= w_opt:
                wrong_values.append(self.spinbox_w_min, self.spinbox_w_opt)
            if not w_opt <= w_max:
                wrong_values.append(self.spinbox_w_opt, self.spinbox_w_max)

            h_min, h_opt, h_max = (
                self.spinbox_h_min.value(),
                self.spinbox_h_opt.value(),
                self.spinbox_h_max.value(),
            )
            if not h_min <= h_opt:
                wrong_values.append(self.spinbox_h_min, self.spinbox_h_opt)
            if not h_opt <= h_max:
                wrong_values.append(self.spinbox_h_opt, self.spinbox_h_max)


        is_valid: bool = bool(len(wrong_values))


    def values(self) -> dict[str, str | tuple[int, int] | list[str]]:
        gpu: str = ""
        if self._gpus:
            gpu = self._gpus.get(self.combobox_gpu.currentText(), "")

        dtypes: list[str] = ["fp32"]
        if self.checkbox_fp16.isChecked():
            dtypes.append("fp16")
        if self.checkbox_bf16.isChecked():
            dtypes.append("bf16")

        shape_strategy: str = 'dynamic'
        if self.radiobutton_fixed.isChecked():
            shape_strategy = 'fixed'
        elif self.radiobutton_static.isChecked():
            shape_strategy = 'static'

        values: dict[str, str | int | tuple[int, int]] = {
            'gpu': gpu,
            'dtypes': dtypes,
            'shape_strategy': shape_strategy,
            'shape_min': (self.spinbox_w_min.value(), self.spinbox_h_min.value()),
            'shape_opt': (self.spinbox_w_opt.value(), self.spinbox_h_opt.value()),
            'shape_max': (self.spinbox_w_max.value(), self.spinbox_h_max.value()),
        }
        return values


        self.block_signals(True)
        self.groupbox_tensorrt_conversion.setChecked(b)
        self.block_signals(False)
