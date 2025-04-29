from __future__ import annotations
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

from .common import ShapeStrategyName
from .model_widget import ModelWidget

from .designer.ui_main_window import Ui_MainWindow
if TYPE_CHECKING:
    from backend.controller import Controller


from pynnlib import (
    NnModel,
    NnFrameworkType,
)



class MainWindow(QMainWindow, Ui_MainWindow):
    signal_preview_modified = Signal(dict)
    signal_get_out_fp = Signal(str)
    signal_convert_action = Signal(dict)

    def __init__(self, controller: Controller):
        super().__init__()
        self.setupUi(self)
        self.controller: Controller = controller
        self.is_closing: bool = False

        self.init_gui()


        self.widget_onnx_conversion.set_editable(True)

        self.model_widget = self.findChild(ModelWidget, "widget_model")
        # set_stylesheet(self)
        self.installEventFilter(self)


        self.widget_onnx_conversion.event_shape_strategy_changed.connect(
            self.widget_tensorrt_conversion.constraint_shape_strategy
        )
        self.widget_tensorrt_conversion.event_static_shape_modified.connect(
            self.widget_onnx_conversion.tensorrt_static_shape_modified
        )

        self.controller.signal_model_parsed.connect(self.event_model_parsed)



    def apply_user_preferences(self, user_preferences: dict):
        try:
            w: list[int] = user_preferences['window']
            self.setGeometry(*w[self.app_type])
        except:
            self.setGeometry(0, 0, 640, 800)
        self.show()


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
        sys.exit()


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
        self.signal_convert_action.emit()
        self.button_convert.setEnabled(False)



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



    def event_model_parsed(self) -> None:
        model: NnModel = self.controller.get_in_model_details()
        self.widget_model.model_parsed(model)
        print(model)
        print(model.arch)
        print("- event_model_parsed: TensorRT")
        self.widget_tensorrt_conversion.enable_conversion(model)

        # Hide conversion to ONNX if already an ONNX model
        print("- event_model_parsed: ONNX")
        if model.framework.type == NnFrameworkType.ONNX:
            self.widget_onnx_conversion.setVisible(False)
        else:
            self.widget_onnx_conversion.setVisible(True)
            self.widget_onnx_conversion.enable_conversion(model)

        # Enable conversion to TensorRT and update shape strategy/size
        # self.widget_tensorrt_conversion.constraint_shape_strategy(
        #     strategy=model.shape_strategy.type,
        #     size=model.shape_strategy.opt_size
        # )

        self.textedit_log.clear()
        self.textedit_log.appendPlainText(
            str(model)
        )
        self.textedit_log.appendPlainText(
            str(model.arch)
        )

