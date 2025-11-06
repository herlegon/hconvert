from __future__ import annotations
from functools import partial
from pprint import pprint
from typing import Any, Literal, TYPE_CHECKING, Type
from hutils import (
    get_extension,
    lightcyan,
)
from hwidgets import HStyle
from .pynnlib_api import (
    NnModel,
    NnFrameworkType,
)
from PySide6.QtCore import (
    QTimer,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QSizePolicy,
    QRadioButton,
    QToolButton,
)
from .designer.ui_conversion_widget import Ui_ConversionWidget
from .logger import alog
if TYPE_CHECKING:
    from .main_window import MainWindow


ConversionChoices = Literal['safetensors', 'onnx', 'tensorrt']


class ConversionWidget(QWidget, Ui_ConversionWidget):
    signal_settings_modified = Signal()

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._main_window: MainWindow = None
        self._previous_selection: ConversionChoices = 'safetensors'

        # self.widget_layout.addStretch()
        # self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.selections: dict[ConversionChoices, tuple[str, str]] = {
            'safetensors': ("Safetensors", "To a Safetensors file (s)"),
            'onnx': ("ONNX", "To an ONNX model (o)"),
            'tensorrt': ("TensorRT", "To a TensorRT engine (t)"),
        }
        # self.selection_list = list(self.selections.keys())
        self.selection.set_buttons(self.selections)
        self.selection.set_current_button(0)

        self.frame_onnx.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.frame_tensorrt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.widget_select_out_dir.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.adjustSize()
        self.selection.signal_selection_changed.connect(self.selection_changed)
        self.widget_onnx_conversion.signal_settings_modified.connect(self.settings_modified)


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def apply_user_settings(self, settings: dict) -> None:
        self.frame_onnx.setVisible(False)
        self.frame_tensorrt.setVisible(False)
        self._previous_selection = settings.get('selection', '')
        self.adjust_height()


    def get_user_settings(self) -> dict:
        return {
            'selected_conversion': self.selected()
        }


    def editable_widgets(self) -> list[Type[QWidget]]:
        editable_widgets: list[Type[QWidget]] = [
            *self.selection.buttons(),
            *self.widget_onnx_conversion.editable_widgets(),
            *self.widget_tensorrt_conversion.editable_widgets(),
            *self.widget_select_out_dir.editable_widgets(),
        ]
        return editable_widgets


    def block_signals(self, b: bool) -> None:
        self.selection.blockSignals(b)


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
        self.blockSignals(True)
        self.widget_layout.invalidate()
        self.updateGeometry()
        self.adjustSize()
        self.blockSignals(False)
        QTimer.singleShot(0, self._main_window.adjust_height)


    def refresh_conversion_selection(self, model: NnModel) -> None:
        """Called when a new model is parsed
        """
        if model is None:
            self.widget_select_out_dir.setEnabled(False)
            self.block_signals(True)
            for b in self.selection.buttons():
                b.setEnabled(False)
                b.setChecked(False)
            self.frame_onnx.setVisible(False)
            self.frame_tensorrt.setVisible(False)
            self.block_signals(False)
            self.adjust_height()
            self.setVisible(False)
            return
        self.setVisible(True)

        print(lightcyan("refresh_conversion_selection"))
        print(f"  get arch details to enable/disable widgets for conversion")
        # print(model)
        # print("------------------")
        # print(model.arch)
        # print("------------------")



        self.widget_select_out_dir.refresh_model_info(model)
        self.widget_select_out_dir.setEnabled(
            bool(model.framework.type in (NnFrameworkType.PYTORCH, NnFrameworkType.ONNX))
        )

        # TODO: disable this if not available
        tensorrt_cap: bool = self.widget_tensorrt_conversion.update_capabilities(model)
        onnx_cap: bool = self.widget_onnx_conversion.update_capabilities(model)

        print(f"tensorrt supported: {tensorrt_cap}")

        # Conversion selection
        # todo: get previous checked
        self.block_signals(True)
        for b in self.selection.buttons():
            b.setEnabled(False)
        # self.conversion_selection.setEnabled(False)

        self.block_signals(False)
        if model is not None:
            if model.framework.type == NnFrameworkType.PYTORCH:
                self.selection_button('safetensors').setEnabled(
                    bool(get_extension(model.filepath) != '.safetensors')
                )

                onnx_button = self.selection.get_button('onnx')
                onnx_button.setEnabled(True)
                if tensorrt_cap:
                    self.selection.get_button('tensorrt').setEnabled(True)
                # default: select onnx
                onnx_button.setChecked(True)
                self.conversion_selection_changed('onnx', initial=True)

            elif model.framework.type == NnFrameworkType.ONNX:
                self.selection.get_button('safetensors').setEnabled(False)
                self.selection.get_button('onnx').setEnabled(False)
                tensorrt_button = self.selection.get_button('tensorrt')
                if tensorrt_cap:
                    tensorrt_button.setEnabled(True)
                    tensorrt_button.setChecked(True)
                    self.conversion_selection_changed('tensorrt', initial=True)
                else:
                    tensorrt_button.setEnabled(False)

            elif model.framework.type == NnFrameworkType.TENSORRT:
                self.conversion_selection_changed('tensorrt', initial=True)
                self.frame_onnx.setVisible(False)
                self.frame_tensorrt.setVisible(False)
                # self.adjust_height()

            if self._previous_selection:
                for k in ('safetensors', 'onnx', 'tensorrt'):
                    if (
                        self._previous_selection == k
                        and self.selection.get_button(k).isEnabled()
                    ):
                        self.selection.set_current_button(k)
                        break
                self._previous_selection = ""
                # self.adjust_height()


    def selection_button(self, k: ConversionChoices) -> QToolButton:
        return self.selection.get_button(k)


    def select(self, k: ConversionChoices) -> None:
        self.selection.get_button(k).click()


    def selection_changed(self, index: int) -> None:
        key: ConversionChoices = self.selection.get_button(index).key
        alog.debug(f"selection changed: {self._previous_selection} -> {key}")
        if key != self._previous_selection:
            self.conversion_selection_changed(key)


    def conversion_selection_changed(self, k: ConversionChoices, initial: bool = False) -> None:
        self.block_signals(True)

        is_checkable = self.selection.get_button(k).isCheckable()
        if k == 'safetensors' and is_checkable:
            self.frame_onnx.setVisible(False)
            self.frame_tensorrt.setVisible(False)

        elif k == 'onnx' and is_checkable:
            self.frame_tensorrt.setVisible(False)
            self.frame_onnx.setVisible(True)

        elif k == 'tensorrt' and is_checkable:
            self.frame_onnx.setVisible(False)
            self.frame_tensorrt.setVisible(True)

        else:
            self.setEnabled(False)
            self.block_signals(False)
            return

        self.selection.set_current_button(k)
        self._previous_selection = k
        self.adjust_height()
        self.block_signals(False)

        # Do not send a signal if it's the triggered by the parsing
        if not initial:
            self.settings_modified()


    def settings_modified(self) -> None:
        self.signal_settings_modified.emit()


    def selected(self) -> ConversionChoices | None:
        index = self.selection.current_button_index()
        if index == -1:
            return None
        return self.selection.current_button().key


    def settings(self) -> dict[str, str | dict[str, Any]] | None:
        selected = self.selected()
        if selected is None:
            return None

        settings: dict[str, str | dict[str, Any]] = {
            'to': self.selected(),
            'out_dir': self.widget_select_out_dir.out_dir(),
        }

        if selected == 'onnx':
            settings['values'] = self.widget_onnx_conversion.values()

        elif selected == 'tensorrt':
            settings['values'] = self.widget_tensorrt_conversion.values()

        return settings
