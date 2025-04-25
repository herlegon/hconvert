from __future__ import annotations
from functools import partial
from pynnlib import (
    NnModel,
    NnFrameworkType,
    PyTorchModel,
)

from PySide6.QtCore import (
    QCoreApplication,
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
    predefined_shapes,
    predefined_shapes_inv,
)


class TensorRTConversionWidget(QWidget, Ui_TensorRTConversionWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._gpus = dict[str, int]
        self._is_fixed: bool = False
        self.previous_shapes: dict[str, tuple[int, int]] = {
            "min": (0, 0),
            "opt": (0, 0),
            "max": (0, 0),
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

        for cb in (
            self.combobox_resolution_min,
            self.combobox_resolution_opt,
            self.combobox_resolution_max,
        ):
            cb.clear()
            cb.addItems(list(predefined_shapes.keys()))
            cb.setCurrentIndex(-1)

        self.clear()
        self.setEnabled(False)
        self.adjustSize()

        self.checkbox_dynamic.toggled.connect(self.shape_strategy_changed)
        self.checkbox_fixed.toggled.connect(self.shape_strategy_changed)

        for sw in self.size_widgets:
            # w, h, resolution
            ww, hw, rw = sw
            ww.valueChanged.connect(partial(self.size_modified, sw))
            hw.valueChanged.connect(partial(self.size_modified, sw))
            rw.currentIndexChanged.connect(partial(self.resolution_selected, sw))



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

        for sw, sh, sc in self.size_widgets:
            sw.lineEdit().clear()
            sh.lineEdit().clear()
            sc.setCurrentIndex(-1)



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
        print(f"torch-> tensorrt: {is_torch_to_tensorrt_possible}")
        print(f"onnx-> tensorrt: {is_onnx_to_tensorrt_possible}")

        if not is_torch_to_tensorrt_possible and not is_onnx_to_tensorrt_possible:
            print("not supported")
            self.setEnabled(False)
            return

        print("enable tenbsorrt")
        # Enable conversion
        self.block_signals(True)
        self.checkbox_dynamic.setChecked(True)
        self.checkbox_fixed.setChecked(False)
        self.block_signals(False)

        self._is_fixed = not self.checkbox_fixed.isChecked()
        self.shape_strategy_changed(True)



        self.setEnabled(True)
        self.block_signals(False)



    def shape_strategy_changed(self, state: bool) -> None:
        self.block_signals(True)
        is_fixed = self.checkbox_fixed.isChecked()
        if self._is_fixed and not is_fixed:
            # fixed -> dynamic
            self.previous_shapes: dict[str, tuple[int, int]] = {
                "min": (self.spinbox_w_min.value(), self.spinbox_h_min.value()),
                "opt": (self.spinbox_w_opt.value(), self.spinbox_h_opt.value()),
                "max": (self.spinbox_w_max.value(), self.spinbox_h_max.value()),
            }
            for sw, sh, sc in self.size_widgets:
                sw.lineEdit().clear()
                sh.lineEdit().clear()
                sc.setCurrentIndex(-1)

        if not self._is_fixed and is_fixed:
            # dynamic -> fixed
            # self.spinbox_w_min.setValue(self.previous_shapes['min'][0])
            # self.spinbox_h_min.setValue(self.previous_shapes['min'][1])
            # self.spinbox_w_opt.setValue(self.previous_shapes['opt'][0])
            # self.spinbox_h_opt.setValue(self.previous_shapes['opt'][1])
            # self.spinbox_w_max.setValue(self.previous_shapes['max'][0])
            # self.spinbox_h_max.setValue(self.previous_shapes['max'][1])
            self.spinbox_w_min.setEnabled(False)
            self.update_resolution_text()

        self._is_fixed = is_fixed
        self.block_signals(False)



    def update_resolution_text(self) -> None:
        for sw, sh, sc in self.size_widgets:
            t = predefined_shapes_inv.get(
                "x".join(map(str, (sw.value(), sh.value()))), ""
            )
            sc.setCurrentIndex(sc.findText(t))



    def size_modified(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value) -> None:
        ww, hw, rw = sw
        rw.blockSignals(True)
        t = predefined_shapes_inv.get(
            "x".join(map(str, (ww.value(), hw.value()))), ""
        )
        rw.setCurrentIndex(rw.findText(t))
        ww.lineEdit().deselect()
        hw.lineEdit().deselect()
        rw.blockSignals(False)



    def resolution_selected(self, sw: tuple[QSpinBox, QSpinBox, QComboBox], value) -> None:
        ww, hw, rw = sw

        current_text: str = rw.currentText()
        w, h = predefined_shapes[current_text]
        ww.blockSignals(True)
        hw.blockSignals(True)
        ww.setValue(w)
        hw.setValue(h)
        ww.lineEdit().deselect()
        hw.lineEdit().deselect()
        ww.blockSignals(False)
        hw.blockSignals(False)
