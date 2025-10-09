from __future__ import annotations
from functools import partial
import os
from pprint import pprint
import sys
from typing import TYPE_CHECKING, Literal
from PySide6.QtCore import (
    Signal,
    Slot,
    QEvent,
    QObject,
    Slot,
    Qt,
)
from PySide6.QtGui import (
    QCloseEvent,
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMessageBox,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
)


from .designer.ui_main_window import Ui_MainWindow
if TYPE_CHECKING:
    from backend.controller import Controller
    from backend.user_preferences import UserPreferences


from pynnlib import (
    NnModel,
    NnFrameworkType,
)



class MainWindow(QMainWindow, Ui_MainWindow):
    signal_preview_modified = Signal(dict)
    signal_get_out_fp = Signal(str)
    signal_convert_action = Signal(dict)
    signal_model_loaded = Signal(str)


    def __init__(self, controller: Controller):
        super().__init__()
        self.setupUi(self)
        self.controller: Controller = controller
        self.is_closing: bool = False

        self.init_gui()


        # self.model_widget = self.findChild(ModelWidget, "widget_model")
        # set_stylesheet(self)
        self.installEventFilter(self)


        # self.widget_onnx_conversion.signal_shape_strategy_changed.connect(
        #     self.widget_tensorrt_conversion.constraint_shape_strategy
        # )
        # self.widget_tensorrt_conversion.signal_static_shape_modified.connect(
        #     self.widget_onnx_conversion.tensorrt_static_shape_modified
        # )
        self.controller.signal_model_parsed.connect(self.event_model_parsed)

        # Conversion selected changed
        self.checkbox_safetensor.setCheckable(True)
        self.checkbox_safetensor.setCheckState(Qt.CheckState.Unchecked)
        self.checkbox_safetensor.stateChanged.connect(
            partial(self.conversion_selection_changed, 'safetensor'))
        self.groupBox_onnx.toggled.connect(
            partial(self.conversion_selection_changed, 'onnx'))
        self.groupBox_tensorrt.toggled.connect(
            partial(self.conversion_selection_changed, 'tensorrt'))

        self.is_converting: bool = False



    def apply_user_preferences(self, user_preferences: UserPreferences):
        print(f"apply_user_preferences: {user_preferences.settings}")
        # try:
        #     w: list[int] = user_preferences.settings['window']['geometry']
        #     self.setGeometry(*w)
        # except:
        #     self.setGeometry(0, 0, 640, 800)

        self.show()
        self.checkbox_safetensor.setCheckState(Qt.CheckState.Checked)
        self.conversion_selection_changed('safetensor', True)
        self.adjustSize()


    def get_user_preferences(self) -> dict:
        preferences = {
            'window': {
                'screen': 0,
                'geometry': self.geometry().getRect()
            },
            'user': {},
        }
        return preferences


    def closeEvent(self, event: QCloseEvent):
        self.close_event()


    def close_event(self):
        if not self.is_closing:
            self.is_closing = True
            self.controller.exit()
            self.close_all_widgets()


    def close_all_widgets(self):
        for widget in QApplication.topLevelWidgets():
            widget.close()
        self.close()
        # Not clean but avoid ghost processes: clean this
        # sys.exit()


    def init_gui(self):

        # Put here all initialization settings fro each widget.
        # so that it will be easier for refactoring

        self.combobox_out_name.setAcceptDrops(False)
        self.combobox_out_name.setEditable(True)
        self.combobox_out_name.setInsertPolicy(QComboBox.InsertAtCurrent)
        self.combobox_out_name.clear()
        self.combobox_out_name.clearEditText()
        self.button_out_browse.clicked.connect(self.event_out_dir_picker)
        self.checkbox_out_autonaming.setChecked(True)
        self.checkbox_out_autonaming.toggled[bool].connect(self.event_out_autonaming)

        self.button_convert.clicked.connect(self.event_convert)

        self.controller.signal_out_fp.connect(self.event_out_fp_refreshed)


    def block_conversion_signal(self, b: bool) -> None:
        self.checkbox_safetensor.blockSignals(b)
        self.groupBox_onnx.blockSignals(b)
        self.groupBox_tensorrt.blockSignals(b)


    def adjust_height(self) -> None:
        w = self.geometry().width()
        self.adjustSize()
        x, y, _, h = self.geometry().getRect()
        print(f"to: {x}, {y}: {w}x{h}")
        self.setGeometry(x, y, w, h)
        print(f"new: {self.geometry().getRect()}")


    def conversion_selection_changed(self, k: Literal['safetensor', 'onnx', 'tensorrt'], state: bool) -> None:
        self.block_conversion_signal(True)

        if k == 'safetensor':
            if self.checkbox_safetensor.checkState() != Qt.CheckState.Checked:
                self.checkbox_safetensor.setCheckState(Qt.CheckState.Checked)
            else:
                self.widget_onnx_conversion.set_selected(False)
                self.widget_tensorrt_conversion.set_selected(False)
                self.groupBox_onnx.setChecked(False)
                self.groupBox_tensorrt.setChecked(False)
                self.widget_onnx_conversion.hide()
                self.widget_tensorrt_conversion.hide()
                # self.textedit_log.hide()
                self.adjust_height()

        elif k == 'onnx':
            if not self.groupBox_onnx.isChecked():
                self.groupBox_onnx.setChecked(True)
            else:
                self.widget_tensorrt_conversion.set_selected(False)
                self.groupBox_tensorrt.setChecked(False)
                self.checkbox_safetensor.setCheckState(Qt.CheckState.Unchecked)
                self.widget_tensorrt_conversion.hide()
                self.widget_onnx_conversion.set_selected(True)
                self.widget_onnx_conversion.show()
                self.widget_onnx_conversion.adjustSize()
                # self.textedit_log.show()
                self.adjust_height()

        elif k == 'tensorrt':
            if not self.groupBox_tensorrt.isChecked():
                self.groupBox_tensorrt.setChecked(True)
            else:
                self.widget_onnx_conversion.set_selected(False)
                self.groupBox_onnx.setChecked(False)
                self.checkbox_safetensor.setCheckState(Qt.CheckState.Unchecked)
                self.widget_tensorrt_conversion.set_selected(True)
                self.widget_onnx_conversion.hide()
                self.widget_tensorrt_conversion.show()
                self.widget_tensorrt_conversion.adjustSize()
                # self.textedit_log.show()
                self.adjust_height()

        self.block_conversion_signal(False)



    def get_conversion_settings(self) -> dict:
        return {}



    def event_out_dir_picker(self):
        pass



    def event_out_autonaming(self):
        auto_naming: bool = self.checkbox_out_autonaming.isChecked()
        self.signal_get_out_fp.emit(
            {
                'autonaming': auto_naming,
                'out_dir': self.combobox_out_name.currentText(),
                'settings': self.get_conversion_settings(),
            }
        )
        label_text: str = "Save as" if auto_naming else "Directory"
        self.label_out_type.setText(label_text)



    def event_out_fp_refreshed(self, name: str) -> None:
        self.combobox_out_name.setCurrentText(name)



    def event_convert(self) -> None:
        # Can be either start or cancel
        if not self.is_converting:
            self.is_converting = True
            self.widget_onnx_conversion.setEnabled(False)
            self.widget_tensorrt_conversion.setEnabled(False)
            self.button_convert.setEnabled(False)
            conversion_values: dict[str, dict[str, Any]] = {
                'onnx': self.widget_onnx_conversion.values(),
                'tensorrt': self.widget_tensorrt_conversion.values(),
            }
            self.signal_convert_action.emit(conversion_values)
            print("start converting")
            pprint(conversion_values)

            # remove this once backend send ack
            self.button_convert.setText("Cancel")
            self.button_convert.setEnabled(True)

        else:
            self.widget_onnx_conversion.setEnabled(True)
            self.widget_tensorrt_conversion.setEnabled(True)
            self.signal_convert_action.emit("stop")

            # remove this once backend send ack
            self.button_convert.setText("Convert")
            self.button_convert.setEnabled(True)
            self.is_converting = False


    def event_convert_state_changed(self, status: dict) -> None:
        # status: dict(
        #   'state': Literal['stopped', 'running'],
        #   'type': Literal['progress', 'undetermined'],
        #   'progress': int,
        # )
        if status['state'] == 'stopped':
            self.button_convert.setText("Convert")
            self.button_convert.setEnabled(True)

        elif status['state'] == 'running':
            self.button_convert.setText("Cancel")
            self.button_convert.setEnabled(True)



    def event_model_parsed(self, model_fp: str) -> None:
        self.widget_model_browser.update_model_fp(model_fp=model_fp)

        model: NnModel = self.controller.get_in_model_info()

        # self.setEnabled(True)
        self.widget_pytorch_model.refresh_model_info(model)
        self.widget_onnx_model.refresh_model_info(model)
        self.widget_metadata.refresh_model_info(model)

        print(model)
        if model is not None:
            print(model.arch)
        print("- event_model_parsed: TensorRT")
        self.widget_tensorrt_conversion.enable_conversion(model)

        # Hide conversion to ONNX if already an ONNX model
        print("- event_model_parsed: ONNX")
        if model is not None:
            if model.framework.type == NnFrameworkType.ONNX:
                self.groupBox_onnx.setVisible(False)
            else:
                self.groupBox_onnx.setVisible(True)
                # self.groupBox_onnx.enable_conversion(model)
        else:
            print("Set Editable to False")
            self.groupBox_onnx.setVisible(True)
            self.groupBox_onnx.setEnabled(False)

        # Enable conversion to TensorRT and update shape strategy/size
        if model is None:
            self.groupBox_tensorrt.setVisible(False)
        else:
            self.groupBox_tensorrt.setVisible(True)
        # self.widget_tensorrt_conversion.constraint_shape_strategy(
        #     strategy=model.shape_strategy.type,
        #     size=model.shape_strategy.opt_size
        # )

        # self.textedit_log.clear()
        # if model is not None:
        #     self.textedit_log.appendPlainText(str(model))
        #     self.textedit_log.appendPlainText(str(model.arch))
