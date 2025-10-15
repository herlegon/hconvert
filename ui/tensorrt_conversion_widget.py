from __future__ import annotations
from functools import partial
from pprint import pprint
from typing import Literal, Type
from hutils import (
    red,
    lightcyan,
    lightgreen,
    purple,
    yellow,
)
from pynnlib import (
    NnModel,
    NnFrameworkType,
    NnPytorchArchitecture,
)
from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QCheckBox,
    QComboBox,
    QRadioButton,
    QSpinBox,
)

from .designer.ui_tensorrt_conversion_widget import Ui_TensorRTConversionWidget
from .common import (
    DEFAULT_SIZE,
    PREDEFINED_SIZE,
    predefined_shapes_inv,
    ShapeStrategyName,
)



class TensorRTConversionWidget(QWidget, Ui_TensorRTConversionWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._gpus: dict[str, int] = {}
        self.current_shape_strategy: ShapeStrategyName = ''
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": (64, 64),
            "opt": DEFAULT_SIZE,
            "max": (1920, 1080),
        }

        self._editable_widgets: tuple[type[QWidget]] = (
            *self.findChildren(QComboBox),
            *self.findChildren(QRadioButton),
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
        self.radio_fixed.toggled.connect(partial(self.shape_strategy_changed, 'fixed'))
        self.radio_static.toggled.connect(partial(self.shape_strategy_changed, 'static'))
        self.radio_dynamic.toggled.connect(partial(self.shape_strategy_changed, 'dynamic'))
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
        for w in self._editable_widgets:
            w.blockSignals(b)


    def editable_widgets(self) -> list[Type[QWidget]]:
        return list(self._editable_widgets)


    def clear(self) -> None:
        self.block_signals(True)

        self.radio_fp32.setChecked(True)

        self.radio_dynamic.setChecked(False)
        self.radio_fixed.setChecked(False)

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


    def set_size_widget_enabled(self, strategy: ShapeStrategyName) -> None:
        print(f"  update_size_widgets: strategy=", f"{strategy}")
        if strategy == 'dynamic':
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                sb_w.setEnabled(True)
                sb_h.setEnabled(True)
                cb_r.setEnabled(True)
        else:
            # Disable min/max shapes
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                if i == 1:
                    sb_w.setEnabled(True)
                    sb_h.setEnabled(True)
                    cb_r.setEnabled(True)
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


    def update_capabilities(self, model: NnModel) -> bool:
        """Called when a new model is parsed
        """
        self.clear()

        # PyTorch/ONNX only
        # Conversion must be possible for the arch
        # Has a Nvidia GPU
        if model is None:
            self.clear()
            return False

        if model.framework.type == NnFrameworkType.TENSORRT:
            return False

        is_torch_to_tensorrt_possible = bool(
            model.framework.type == NnFrameworkType.PYTORCH
            and model.arch.to_onnx is not None
            and model.arch.to_tensorrt is not None
        )
        is_onnx_to_tensorrt_possible = bool(
            model.framework.type == NnFrameworkType.ONNX
            and model.arch.to_tensorrt is not None
        )

        if model.framework.type == NnFrameworkType.PYTORCH:
            to_tensorrt = model.arch.to_tensorrt
            if not (
                to_tensorrt is not None
                and to_tensorrt.dtypes
                and to_tensorrt.shape_strategy_types
            ):
                return False

        print(red("TODO: sysinfo"))
        print(lightcyan(f"tensorrt_conversion_widget: update_capabilities"))
        # print(f"  torch-> tensorrt: {is_torch_to_tensorrt_possible}")
        # print(f"  onnx-> tensorrt: {is_onnx_to_tensorrt_possible}")
        # if not is_torch_to_tensorrt_possible and not is_onnx_to_tensorrt_possible:
        #     print("  not supported")
        #     self.setEnabled(False)
        #     return

        # Enable conversion
        self.block_signals(True)

        # Use the default shape strategy

        previous_shape_strategy = self.current_shape_strategy

        if model.framework.type == NnFrameworkType.ONNX:
            print(red("TODO: Let's enable/disable widgets"))

            self.spinbox_opset.setValue(model.opset)
            self.spinbox_opset.setEnabled(False)

            in_dtype = model.io_dtypes['input']
            for d, r in (
                ('fp32', self.radio_fp32),
                ('fp16', self.radio_fp16),
                ('bf16', self.radio_bf16),
            ):
                if d == in_dtype:
                    r.setCheckable(True)
                    r.setChecked(True)
                else:
                    r.setCheckable(False)
                r.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                r.setEnabled(False)

            # Shape strategy
            self.current_shape_strategy = model.shape_strategy.type
            if model.shape_strategy.type == 'static':
                self.radio_static.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                self.radio_static.setEnabled(True)
                self.radio_static.setChecked(True)

                self.radio_dynamic.setEnabled(False)
                self.radio_fixed.setEnabled(False)

            else:
                self.radio_static.setEnabled(False)
                for r in (self.radio_dynamic, self.radio_fixed):
                    r.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                    r.setEnabled(True)
                self.radio_dynamic.setChecked(True)

            pprint(self.previous_shapes)
            self.set_size_widget_enabled(self.current_shape_strategy)
            if model.shape_strategy.type == 'static':
                print("disable")
                w, h = model.shape_strategy.opt_size
                self.spinbox_w_opt.setValue(w)
                self.spinbox_h_opt.setValue(h)
                self.update_opt_resolution_text()
                self.set_opt_modifications_enabled(False)

            else:
                self.set_opt_modifications_enabled(True)
                self.restore_sizes(ignore_opt=False)
                self.update_resolution_text()


        elif model.framework.type == NnFrameworkType.PYTORCH:
            model_arch: NnPytorchArchitecture = model.arch

            # Datatypes
            for d, r in (
                ('fp32', self.radio_fp32),
                ('bf16', self.radio_bf16),
                ('fp16', self.radio_fp16),
            ):
                if d in model_arch.to_tensorrt.dtypes:
                    r.setEnabled(True)
                    r.setChecked(True)
                else:
                    r.setEnabled(False)

            # Shape strategy
            for s, r in (
                ('dynamic', self.radio_dynamic),
                ('static', self.radio_static),
                ('fixed', self.radio_fixed),
            ):
                if s in model_arch.to_tensorrt.shape_strategy_types:
                    r.setEnabled(True)
                    r.setChecked(True)
                    self.current_shape_strategy = s
                else:
                    r.setEnabled(False)

            # Typing: read only, force to
            if model_arch.to_tensorrt.weak_typing:
                self.radio_weak.setChecked(True)
            else:
                self.radio_strong.setChecked(True)
            for r in (self.radio_weak, self.radio_strong):
                r.setEnabled(False)

            self.set_size_widget_enabled(self.current_shape_strategy)
            if previous_shape_strategy != self.current_shape_strategy:
                print(yellow("  updating capabilities, shape strategy changed"))
                # Fill the size values
                if self.current_shape_strategy in ('fixed', 'static'):
                    print(f"  fixed, static use default size: {DEFAULT_SIZE}")
                    w, h = DEFAULT_SIZE
                    self.spinbox_w_opt.setValue(w)
                    self.spinbox_h_opt.setValue(h)
                    self.update_opt_resolution_text()

                elif self.current_shape_strategy == 'dynamic':
                    print(f"  dynamic: {DEFAULT_SIZE}")
                    self.restore_sizes(ignore_opt=False)
                    self.update_resolution_text()

        self.setEnabled(True)
        self.block_signals(False)

        return True


    def shape_strategy_changed(self, button: Literal['fixed', 'static', 'dynamic'], state) -> None:
        """User action to set from/to dynamic, fixed/static
        """
        if not state:
            return
        print(f"\nBUtton state changed: {button}, state={state}")
        self.block_signals(True)
        previous_strategy: str = self.current_shape_strategy
        to_dynamic: bool = self.radio_dynamic.isChecked()
        to_fixed: bool = self.radio_fixed.isChecked()
        to_static: bool = self.radio_static.isChecked()

        print(purple(f"shape_strategy_changed:"))
        print(f"{previous_strategy} -> {'fixed' if to_fixed else ''}{'static' if to_static else ''}{'dynamic' if to_dynamic else ''}")

        if previous_strategy == 'dynamic' and (to_fixed or to_static):
            # dynamic -> fixed
            # Save to restore min/max values when changing from fixed to dynamic
            self.save_current_sizes()
            self.current_shape_strategy = 'static' if to_static else 'fixed'
            self.set_size_widget_enabled(strategy=self.current_shape_strategy)
            # self.restore_sizes(ignore_opt=False)

        elif previous_strategy != 'dynamic' and to_dynamic:
            # fixed/static -> dynamic
            self.current_shape_strategy = 'dynamic'
            self.set_size_widget_enabled(strategy=self.current_shape_strategy)
            self.restore_sizes(ignore_opt=False)

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
        cb_r.blockSignals(False)


    def resolution_selected(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value) -> None:
        """User modified resolution
        Update the size widgets
        """
        sb_w, sp_h, cb_r = sw
        current_text: str = cb_r.currentText()
        w, h = PREDEFINED_SIZE[current_text]

        for sb, v in ((sb_w, w), (sp_h, h)):
            sb.blockSignals(True)
            sb.setValue(v)
            sb.lineEdit().deselect()
            sb.blockSignals(False)


    def set_opt_modifications_enabled(self, enable: bool) -> None:
        self.spinbox_w_opt.setEnabled(enable)
        self.spinbox_h_opt.setEnabled(enable)
        self.combobox_resolution_opt.setEnabled(enable)


    def validate_shapes(self) -> None:
        """Verify that shapes are consistent.
            Emit a signal if not the case.
        """
        wrong_values: list[QSpinBox] = []
        if self.current_shape_strategy == 'dynamic':
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
        if is_valid:
            print(lightgreen("valid"))
        else:
            print(red("ERROR"))


    def values(self) -> dict[str, str | tuple[int, int] | list[str]]:
        gpu: str = ""
        if self._gpus:
            gpu = self._gpus.get(self.combobox_gpu.currentText(), "")

        dtypes: list[str] = ["fp32"]
        if self.radio_fp16.isChecked():
            dtypes.append("fp16")
        if self.radio_bf16.isChecked():
            dtypes.append("bf16")

        shape_strategy: str = 'dynamic'
        if self.radio_fixed.isChecked():
            shape_strategy = 'fixed'
        elif self.radio_static.isChecked():
            shape_strategy = 'static'

        values: dict[str, str | int | tuple[int, int]] = {
            'gpu': gpu,
            'opset': self.spinbox_opset.value(),
            'dtypes': dtypes,
            'shape_strategy': shape_strategy,
            'shape_min': (self.spinbox_w_min.value(), self.spinbox_h_min.value()),
            'shape_opt': (self.spinbox_w_opt.value(), self.spinbox_h_opt.value()),
            'shape_max': (self.spinbox_w_max.value(), self.spinbox_h_max.value()),
            'typing': 'weak' if self.radio_weak.isChecked() else 'strong',
        }
        return values
