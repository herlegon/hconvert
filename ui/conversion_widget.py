from __future__ import annotations
from functools import partial
from pprint import pprint
from typing import Any, Literal, TYPE_CHECKING
from backend.user_preferences import UserPreferences
from pynnlib import (
    NnModel,
    NnFrameworkType,
    SizeConstraint,
)
from pynnlib.utils.p_print import *

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
)
from .designer.ui_conversion_widget import Ui_ConversionWidget
if TYPE_CHECKING:
    from .main_window import MainWindow


class ConversionWidget(QWidget, Ui_ConversionWidget):
    signal_conversion_selection_changed = Signal()

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setupUi(self)
        self._main_window: MainWindow = None

        self.setEnabled(False)
        self.adjustSize()

        # Conversion selection changed
        self.radioButton_safetensor.setChecked(True)
        self.radioButton_safetensor.clicked.connect(
            partial(self.conversion_selection_changed, 'safetensor'))
        self.radioButton_onnx.clicked.connect(
            partial(self.conversion_selection_changed, 'onnx'))
        self.radioButton_tensorrt.clicked.connect(
            partial(self.conversion_selection_changed, 'tensorrt'))


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def apply_user_preferences(self, user_preferences: UserPreferences):
        try:
            w: list[int] = user_preferences.settings['window']['geometry']
            self.setGeometry(*w)
        except:
            pass
        self.groupBox_onnx.setVisible(False)
        self.groupBox_tensorrt.setVisible(False)
        self.conversion_selection_changed('safetensor')


    def block_signals(self, b: bool) -> None:
        for r in (
            self.radioButton_safetensor,
            self.radioButton_onnx,
            self.radioButton_tensorrt,
        ):
            r.blockSignals(b)


    def clear(self) -> None:
        self.block_signals(True)
        for w in (
            self.widget_onnx_conversion,
            self.widget_tensorrt_conversion,
            self.widget_select_out_dir,
        ):
            w.clear()
        self.block_signals(False)


    def adjust_height(self) -> None:
        self.setMaximumHeight(4096)
        w = self.geometry().width()
        self.adjustSize()
        x, y, _, h = list(self.geometry().getRect())
        self.setGeometry(x, y, w, h)
        self.setMaximumHeight(h)


    def refresh_conversion_selection(self, model: NnModel) -> None:
        """Called when a new model is parsed
        """
        if model is None:
            self.widget_select_out_dir.setEnabled(False)

        elif model.framework.type == NnFrameworkType.PYTORCH:
            self.widget_select_out_dir.setEnabled(True)

        elif model.framework.type == NnFrameworkType.ONNX:
            self.widget_select_out_dir.setEnabled(True)

        if model.framework.type == NnFrameworkType.TENSORRT:
            self.widget_select_out_dir.setEnabled(False)

        self.widget_select_out_dir.refresh_model_info(model)


        # TODO: disable this if not available
        self.widget_tensorrt_conversion.enable_conversion(model)

        # Conversion selection
        # todo: get previous checked
        self.block_signals(True)
        self.radioButton_safetensor.setEnabled(False)
        self.radioButton_safetensor.setChecked(False)
        self.radioButton_onnx.setEnabled(False)
        self.radioButton_onnx.setChecked(False)
        self.radioButton_tensorrt.setEnabled(False)
        self.radioButton_tensorrt.setChecked(False)
        self.block_signals(False)
        if model is not None:
            if model.framework.type == NnFrameworkType.PYTORCH:
                self.radioButton_safetensor.setEnabled(True)
                self.radioButton_onnx.setEnabled(True)
                self.radioButton_tensorrt.setEnabled(True)
                # self.radioButton_safetensor.setChecked(True)

            elif model.framework.type == NnFrameworkType.ONNX:
                self.radioButton_safetensor.setEnabled(False)
                self.radioButton_onnx.setEnabled(False)
                self.radioButton_tensorrt.setEnabled(True)
                self.radioButton_tensorrt.setChecked(True)


    def conversion_selection_changed(self, k: Literal['safetensor', 'onnx', 'tensorrt']) -> None:
        self.block_signals(True)

        if k == 'safetensor':
            # self.widget_onnx_conversion.set_selected(False)
            # self.widget_tensorrt_conversion.set_selected(False)
            self.groupBox_onnx.setVisible(False)
            self.groupBox_tensorrt.setVisible(False)

        elif k == 'onnx':
            # self.widget_tensorrt_conversion.set_selected(False)
            # self.widget_onnx_conversion.set_selected(True)
            self.groupBox_tensorrt.setVisible(False)
            self.groupBox_onnx.setVisible(True)

        elif k == 'tensorrt':
            # self.widget_onnx_conversion.set_selected(False)
            # self.widget_tensorrt_conversion.set_selected(True)
            self.groupBox_onnx.setVisible(False)
            self.groupBox_tensorrt.setVisible(True)

        else:
            self.setEnabled(False)
            self.block_signals(False)
            return

        self.setEnabled(True)
        self.block_signals(False)


    def started(self, started: bool) -> None:
        if started:
            self.widget_onnx_conversion.setEnabled(False)
            self.widget_tensorrt_conversion.setEnabled(False)

        else:
            self.widget_onnx_conversion.setEnabled(True)
            self.widget_tensorrt_conversion.setEnabled(True)


    def settings(self) -> dict[str, str | dict[str, Any]] | None:
        settings: dict[str, str | dict[str, Any]] | None =  None
        if self.radioButton_safetensor:
            settings = {
                'to': 'safetensors',
                'out_dir': self.widget_select_out_dir.values()
            }

        elif self.radioButton_onnx:
            settings = {
                'to': 'onnx',
                'values': self.widget_onnx_conversion.values(),
                'out_dir': self.widget_select_out_dir.values()
            }

        elif self.radioButton_tensorrt:
            settings = {
                'to': 'tensorrt',
                'values': self.widget_tensorrt_conversion.values(),
                'out_dir': self.widget_select_out_dir.values()
            }

        return settings
