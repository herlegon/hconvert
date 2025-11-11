from __future__ import annotations
from functools import partial
from typing import Literal, Type
from hytils import (
    red,
    lightcyan,
    lightgreen,
    purple,
    yellow,
)
from hwidgets import HStyle
from .pynnlib_api import (
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
    QSpinBox,
)

from .designer.ui_tensorrt_conversion_widget import Ui_TensorRTConversionWidget
from .common import (
    DEFAULT_SIZE,
    PREDEFINED_SIZE,
    TENSORRT_DEFAULT_SETTINGS,
    predefined_shapes_inv,
    ShapeStrategyName,
)
from .ui_types import (
    ui_dtypes,
    ui_typing,
    ui_shapes,
)
from .logger import alog


class TensorRTConversionWidget(QWidget, Ui_TensorRTConversionWidget):

    def __init__(self, parent):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._gpus: dict[str, int] = {}
        self.current_shape_strategy: ShapeStrategyName = ''
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": (64, 64),
            "opt": DEFAULT_SIZE,
            "max": (1920, 1080),
        }

        self.h_button_group_dtypes.set_buttons(ui_dtypes)
        self.h_button_group_typing.set_buttons(ui_typing)
        self.h_button_group_shapes.set_buttons(ui_shapes)

        self._editable_widgets: tuple[type[QWidget]] = (
            *self.findChildren(QComboBox),
            *self.findChildren(QCheckBox),
            *self.findChildren(QSpinBox),
            self.h_button_group_shapes,
            self.h_button_group_dtypes,
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
        self.set_default_shapes()
        self.adjustSize()

        # Signals
        self.h_button_group_shapes.signal_selection_changed.connect(self.shape_strategy_changed)
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


    def signals_blocked(self) -> bool:
        return self._editable_widgets[0].signalsBlocked()


    def editable_widgets(self) -> list[Type[QWidget]]:
        return list(self._editable_widgets)


    def clear(self) -> None:
        self.block_signals(True)

        self.h_button_group_dtypes.set_current_button('fp32')
        self.h_button_group_shapes.set_current_button('dynamic')

        for sb_w, sb_h, cb_r in self.size_widgets:
            sb_w.lineEdit().clear()
            sb_w.clear()
            sb_h.lineEdit().clear()
            sb_h.clear()
            cb_r.setCurrentIndex(-1)
        self.set_size_widget_enabled('dynamic')
        self.block_signals(False)


    def set_default_shapes(self) -> None:
        alog.debug(lightgreen("set_default_shapes"))
        self.spinbox_opset.setValue(TENSORRT_DEFAULT_SETTINGS['version'])
        self.h_button_group_shapes.set_current_button(
            TENSORRT_DEFAULT_SETTINGS['shape_strategy']
        )
        self.h_button_group_dtypes.set_current_button(
            TENSORRT_DEFAULT_SETTINGS['dtype']
        )
        self.shape_strategy_changed(True)
        self.spinbox_w_min.setValue(TENSORRT_DEFAULT_SETTINGS['shape_min'][0])
        self.spinbox_h_min.setValue(TENSORRT_DEFAULT_SETTINGS['shape_min'][1])
        self.spinbox_w_opt.setValue(TENSORRT_DEFAULT_SETTINGS['shape_opt'][0])
        self.spinbox_h_opt.setValue(TENSORRT_DEFAULT_SETTINGS['shape_opt'][1])
        self.spinbox_w_max.setValue(TENSORRT_DEFAULT_SETTINGS['shape_max'][0])
        self.spinbox_h_max.setValue(TENSORRT_DEFAULT_SETTINGS['shape_max'][1])
        self.update_resolution_text()

        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": TENSORRT_DEFAULT_SETTINGS['shape_min'],
            "opt": TENSORRT_DEFAULT_SETTINGS['shape_opt'],
            "max": TENSORRT_DEFAULT_SETTINGS['shape_max'],
        }


    def update_resolution_text(self, index: int = -1) -> None:
        # Update all if index == -1 else only the selected one
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
        alog.debug(f"  update_size_widgets: strategy= {strategy}")
        if strategy == 'dynamic':
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                sb_w.setEnabled(True)
                sb_h.setEnabled(True)
                cb_r.setEnabled(True)
        else:
            # Disable min/max shapes
            alog.debug(yellow(f"   {strategy}"))
            for i, (sb_w, sb_h, cb_r) in enumerate(self.size_widgets):
                if i == 1:
                    self.set_opt_modifications_enabled(True)
                    continue

                sb_w.setEnabled(True)
                sb_w.clear()
                sb_w.lineEdit().clear()
                sb_w.setEnabled(False)

                sb_h.setEnabled(True)
                sb_h.clear()
                sb_h.lineEdit().clear()
                sb_h.setEnabled(False)

                cb_r.setEnabled(True)
                cb_r.setCurrentIndex(-1)
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


    def _update_dtype_capabilities(self, model: NnModel) -> None:
        if model.framework.type == NnFrameworkType.PYTORCH:
            model_arch: NnPytorchArchitecture = model.arch
            in_dtypes = model_arch.to_tensorrt.dtypes

            for d in ('fp32', 'bf16', 'fp16'):
                b = self.h_button_group_dtypes.get_button(d)
                if d in in_dtypes:
                    b.setEnabled(True)
                    b.setCheckable(True)
                    b.setChecked(True)
                    b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                else:
                    b.setCheckable(False)
                    b.setEnabled(False)
                    b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        elif model.framework.type == NnFrameworkType.ONNX:
            in_dtypes = [model.io_dtypes['input'], ]
            for d in ('fp32', 'bf16', 'fp16'):
                b = self.h_button_group_dtypes.get_button(d)
                if d in in_dtypes:
                    b.setEnabled(True)
                    b.setCheckable(True)
                    b.setChecked(True)
                    b.setCheckable(False)
                else:
                    b.setCheckable(False)
                    b.setEnabled(False)
                b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)


    def _update_typing_capabilities(self, model: NnModel) -> None:
        weak_forced: bool = False
        try:
            weak_forced = model.torch_arch.to_tensorrt.weak_typing
        except:
            pass
        try:
            weak_forced = model.arch.to_tensorrt.weak_typing
        except:
            pass

        for b in self.h_button_group_typing.buttons():
            b.setCheckable(False)
        print(red(f"_update_typing_capabilities: weak:{weak_forced}"))

        # Disable all buttons
        for b in self.h_button_group_typing.buttons():
            b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            b.setCheckable(False)

        if weak_forced:
            # Check only weak
            b = self.h_button_group_typing.get_button('weak')
            b.setCheckable(True)
            b.setChecked(True)
            b.setCheckable(False)
            b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        else:
            # Check strong first but let the user choose
            b = self.h_button_group_typing.get_button('strong')
            b.setCheckable(True)
            b.setChecked(True)

            for b in self.h_button_group_typing.buttons():
                b.setCheckable(True)
                b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)


    def _update_shape_strategy_capabilities(self, model: NnModel) -> None:
        were_blocked = self.signals_blocked()
        if not were_blocked:
            self.block_signals(True)
        alog.debug(f"update shape strategy to: {model.shape_strategy.type}")

        # Shape strategy switch
        if model.framework.type == NnFrameworkType.ONNX:
            # Get ONNX strategy
            # TODO: look at the supported dtype torch_arch
            static_b = self.h_button_group_shapes.get_button('static')
            static_b.setEnabled(True)
            static_b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            static_b.setChecked(False)

            if model.shape_strategy.type == 'static':
                static_b.setChecked(True)
                static_b.setCheckable(False)
                for s in ('dynamic', 'fixed'):
                    self.h_button_group_shapes.get_button(s).setEnabled(False)
                self.h_button_group_shapes.set_current_button('static')

            else:
                static_b.setEnabled(False)
                if model.arch.to_tensorrt is not None:
                    supported_shape_strategy = model.arch.to_tensorrt.shape_strategy_types
                else:
                    supported_shape_strategy = ('dynamic', 'fixed')

                for s in ('dynamic', 'fixed'):
                    b = self.h_button_group_shapes.get_button(s)
                    b.setEnabled(True)
                    if s in supported_shape_strategy:
                        b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                        b.setChecked(False)
                        b.setCheckable(True)
                    else:
                        b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                        b.setCheckable(False)
                        b.setEnabled(False)

        elif model.framework.type == NnFrameworkType.PYTORCH:
            # TODO: look at the supported dtype
            # This function will enable/disable the shape strategy values
            supported_shapes = model.arch.to_tensorrt.shape_strategy_types
            for s in ('dynamic', 'static', 'fixed'):
                b = self.h_button_group_shapes.get_button(s)
                b.setEnabled(True)
                if s in supported_shapes:
                    b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                    b.setCheckable(True)
                    b.setChecked(True)
                else:
                    b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                    b.setChecked(False)
                    b.setCheckable(False)
                    b.setEnabled(False)

        # The prefered strategy button is checked, force update
        self.current_shape_strategy = ''
        self.shape_strategy_changed(key=self.h_button_group_shapes.current_button().key)

        # Shape strategy values
        if model.shape_strategy.type == 'static':
            alog.debug(f"update shape strategy to: {model.shape_strategy.type}")
            w, h = model.shape_strategy.opt_size
            self.spinbox_w_opt.setValue(w)
            self.spinbox_h_opt.setValue(h)
            self.update_opt_resolution_text()
            self.spinbox_w_opt.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.spinbox_h_opt.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.combobox_resolution_opt.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        else:
            self.set_opt_modifications_enabled(True)
            self.restore_sizes(ignore_opt=False)
            self.update_resolution_text()

        if not were_blocked:
            self.block_signals(False)


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
            self.spinbox_opset.setEnabled(True)
            if model.shape_strategy.type == 'static':
                self.spinbox_opset.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            else:
                self.spinbox_opset.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

            self._update_dtype_capabilities(model=model)
            self._update_typing_capabilities(model=model)
            self._update_shape_strategy_capabilities(model=model)


        elif model.framework.type == NnFrameworkType.PYTORCH:
            self.spinbox_opset.setEnabled(True)
            self.spinbox_opset.setReadOnly(False)
            self.spinbox_opset.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self._update_dtype_capabilities(model=model)
            self._update_typing_capabilities(model=model)
            self._update_shape_strategy_capabilities(model=model)

            if previous_shape_strategy != self.current_shape_strategy:
                # Fill the size values
                if self.current_shape_strategy in ('fixed', 'static'):
                    w, h = DEFAULT_SIZE
                    self.spinbox_w_opt.setValue(w)
                    self.spinbox_h_opt.setValue(h)
                    self.update_opt_resolution_text()

                elif self.current_shape_strategy == 'dynamic':
                    self.restore_sizes(ignore_opt=False)
                    self.update_resolution_text()

        self.block_signals(False)

        return True


    def shape_strategy_changed(self, key: Literal['fixed', 'static', 'dynamic']) -> None:
        """User action to set from/to dynamic, fixed/static
        """
        were_blocked = self.signals_blocked()
        if not were_blocked:
            self.block_signals(True)
        previous_strategy: str = self.current_shape_strategy
        to_dynamic: bool = bool(key == 'dynamic')
        to_fixed: bool = bool(key == 'fixed')
        to_static: bool = bool(key == 'static')

        alog.debug(purple(f"shape_strategy_changed:"))
        alog.debug(f"{previous_strategy} -> {'fixed' if to_fixed else ''}{'static' if to_static else ''}{'dynamic' if to_dynamic else ''}")

        if previous_strategy in ('', 'dynamic') and (to_fixed or to_static):
            # dynamic -> fixed
            # Save to restore min/max values when changing from fixed to dynamic
            self.save_current_sizes()
            self.current_shape_strategy = 'static' if to_static else 'fixed'
            self.set_size_widget_enabled(strategy=self.current_shape_strategy)
            # self.restore_sizes(ignore_opt=False)
            if self.current_shape_strategy == 'fixed':
                self.copy_from_opt_to_min_max()

        elif previous_strategy != 'dynamic' and to_dynamic:
            # fixed/static -> dynamic
            self.current_shape_strategy = 'dynamic'
            self.set_size_widget_enabled(strategy=self.current_shape_strategy)
            self.restore_sizes(ignore_opt=False)

        if not were_blocked:
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

        self.copy_from_opt_to_min_max()


    def copy_from_opt_to_min_max(self) -> None:
        # When the modified field is the optimized valueand the strategy is fixed,
        # then modify the min and max
        if self.current_shape_strategy == 'fixed':
            self.block_signals(True)
            sb_w, sb_h, cb_r = (self.spinbox_w_opt, self.spinbox_h_opt, self.combobox_resolution_opt)
            size_widgets: tuple[tuple[QSpinBox, QSpinBox, QComboBox]] = (
                (self.spinbox_w_min, self.spinbox_h_min, self.combobox_resolution_min),
                (self.spinbox_w_max, self.spinbox_h_max, self.combobox_resolution_max),
            )
            for _sb_w, _sb_h, _cb_r in size_widgets:
                _sb_w.setValue(sb_w.value())
                _sb_h.setValue(sb_h.value())
                _cb_r.setCurrentIndex(cb_r.currentIndex())
            self.block_signals(False)


    def resolution_selected(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value) -> None:
        """User modified resolution
        Update the size widgets
        """
        sb_w, sb_h, cb_r = sw
        current_text: str = cb_r.currentText()
        if not current_text:
            current_text = "540p NTSC 4:3 sq"
        w, h = PREDEFINED_SIZE[current_text]

        for sb, v in ((sb_w, w), (sb_h, h)):
            sb.blockSignals(True)
            sb.setValue(v)
            sb.lineEdit().deselect()
            sb.blockSignals(False)

        self.copy_from_opt_to_min_max()


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
        if self.h_button_group_dtypes.get_button('fp16').isChecked():
            dtypes.append("fp16")
        if self.h_button_group_dtypes.get_button('bf16').isChecked():
            dtypes.append("bf16")

        values: dict[str, str | int | tuple[int, int]] = {
            'gpu': gpu,
            'opset': self.spinbox_opset.value(),
            'dtypes': dtypes,
            'shape_strategy': self.h_button_group_shapes.current_button().key,
            'shape_min': (self.spinbox_w_min.value(), self.spinbox_h_min.value()),
            'shape_opt': (self.spinbox_w_opt.value(), self.spinbox_h_opt.value()),
            'shape_max': (self.spinbox_w_max.value(), self.spinbox_h_max.value()),
            'typing': self.h_button_group_typing.current_button().key,
        }
        return values
