from __future__ import annotations
from functools import partial
from pprint import pprint
from typing import Any, Literal, TYPE_CHECKING, Type
from hutils import (
    get_extension,
    lightcyan,
)
from hwidgets import HStyle
from pynnlib import (
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
)
from .designer.ui_conversion_widget import Ui_ConversionWidget
if TYPE_CHECKING:
    from .main_window import MainWindow


ConversionChoices = Literal['safetensors', 'onnx', 'tensorrt']


class ConversionWidget(QWidget, Ui_ConversionWidget):
    signal_conversion_selection_changed = Signal()

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._main_window: MainWindow = None
        self._initial_selection: ConversionChoices = 'safetensors'

        self.layout_main.addStretch()
        # self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.groupBox_onnx.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.groupBox_tensorrt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.radioButton_safetensors.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.widget_select_out_dir.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.adjustSize()

        self.radioButton_safetensors.setToolTip("To a SafeTensors file (s)")
        self.radioButton_onnx.setToolTip("To an ONNX model (o)")
        self.radioButton_tensorrt.setToolTip("To a TensorRT engine (t)")

        self.radio_buttons: list[QRadioButton] = [
            self.radioButton_safetensors,
            self.radioButton_onnx,
            self.radioButton_tensorrt,
        ]
        # Conversion selection changed
        self.radioButton_safetensors.setChecked(True)
        self.radioButton_safetensors.clicked.connect(
            partial(self.conversion_selection_changed, 'safetensors'))
        self.radioButton_onnx.clicked.connect(
            partial(self.conversion_selection_changed, 'onnx'))
        self.radioButton_tensorrt.clicked.connect(
            partial(self.conversion_selection_changed, 'tensorrt'))


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def apply_user_settings(self, settings: dict) -> None:
        self.groupBox_onnx.setVisible(False)
        self.groupBox_tensorrt.setVisible(False)
        self._initial_selection = settings.get('selection', '')
        self.adjust_height()


    def get_user_settings(self) -> dict:
        return {
            'selected_conversion': self.selected()
        }


    def editable_widgets(self) -> list[Type[QWidget]]:
        editable_widgets: list[Type[QWidget]] = [
            *self.radio_buttons,
            *self.widget_onnx_conversion.editable_widgets(),
            *self.widget_tensorrt_conversion.editable_widgets(),
            *self.widget_select_out_dir.editable_widgets(),
        ]
        return editable_widgets


    def block_signals(self, b: bool) -> None:
        for r in self.radio_buttons:
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
        self.updateGeometry()
        self.adjustSize()
        QTimer.singleShot(0, self._main_window.adjust_height)


    def refresh_conversion_selection(self, model: NnModel) -> None:
        """Called when a new model is parsed
        """
        if model is None:
            self.widget_select_out_dir.setEnabled(False)
            self.block_signals(True)
            for r in self.radio_buttons:
                r.setEnabled(False)
                r.setChecked(False)
            self.groupBox_onnx.setVisible(False)
            self.groupBox_tensorrt.setVisible(False)
            self.adjust_height()
            self.block_signals(False)
            return


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
        for r in self.radio_buttons:
            r.setEnabled(False)
            r.setChecked(False)

        self.block_signals(False)
        if model is not None:
            if model.framework.type == NnFrameworkType.PYTORCH:
                self.radioButton_safetensors.setEnabled(
                    bool(get_extension(model.filepath) != '.safetensors')
                )
                self.radioButton_onnx.setEnabled(True)
                if tensorrt_cap:
                    self.radioButton_tensorrt.setEnabled(True)
                # default: select onnx
                self.radioButton_onnx.setChecked(True)
                self.conversion_selection_changed('onnx')

            elif model.framework.type == NnFrameworkType.ONNX:
                self.radioButton_safetensors.setEnabled(False)
                self.radioButton_onnx.setEnabled(False)
                if tensorrt_cap:
                    self.radioButton_tensorrt.setEnabled(True)
                    self.radioButton_tensorrt.setChecked(True)
                    self.conversion_selection_changed('tensorrt')
                else:
                    self.radioButton_tensorrt.setEnabled(False)

            elif model.framework.type == NnFrameworkType.TENSORRT:
                self.radioButton_tensorrt.setChecked(True)
                self.groupBox_onnx.setVisible(False)
                self.groupBox_tensorrt.setVisible(False)
                self.adjust_height()

            if self._initial_selection:
                if (
                    self._initial_selection == 'safetensors'
                    and self.radioButton_safetensors.isEnabled()
                ):
                    self.radioButton_safetensors.setChecked(True)

                elif (
                    self._initial_selection == 'onnx'
                    and self.radioButton_onnx.isEnabled()
                ):
                    self.radioButton_onnx.setChecked(True)

                elif (
                    self._initial_selection == 'tensorrt'
                    and self.radioButton_tensorrt.isEnabled()
                ):
                    self.radioButton_tensorrt.setChecked(True)
                self._initial_selection = ""
                self.adjust_height()


    def conversion_selection_changed(self, k: ConversionChoices) -> None:
        self.block_signals(True)

        if k == 'safetensors' and self.radioButton_safetensors.isCheckable():
            self.groupBox_onnx.setVisible(False)
            self.groupBox_tensorrt.setVisible(False)

        elif k == 'onnx' and self.radioButton_onnx.isCheckable():
            self.groupBox_tensorrt.setVisible(False)
            self.groupBox_onnx.setVisible(True)

        elif k == 'tensorrt' and self.radioButton_tensorrt.isCheckable():
            self.groupBox_onnx.setVisible(False)
            self.groupBox_tensorrt.setVisible(True)

        else:
            self.setEnabled(False)
            self.block_signals(False)
            return

        self.adjust_height()
        self.block_signals(False)


    def selected(self) -> ConversionChoices | None:
        if self.radioButton_safetensors.isChecked():
            return 'safetensors'
        elif self.radioButton_onnx.isChecked():
            return 'onnx'
        elif self.radioButton_tensorrt.isChecked():
            return 'tensorrt'
        return None


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
