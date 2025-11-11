from __future__ import annotations
from pprint import pprint
from hytils import (
    red
)
from .logger import alog
from hwidgets import HStyle
from .pynnlib_api import (
    NnModel,
    NnFrameworkType,
)
from .common import (
    DEFAULT_SIZE,
    predefined_shapes_inv,
    ShapeStrategyName,
)
from .ui_types import (
    ui_dtypes,
    ui_shapes
)

from PySide6.QtCore import (
    Qt,
    QTimer,
)
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QWidget,
    QLayout,
)
from .designer.ui_onnx_widget import Ui_OnnxWidget


class OnnxWidget(QWidget, Ui_OnnxWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)

        self.shape_strategy: ShapeStrategyName = 'dynamic'

        self.h_button_group_dtypes.set_buttons(ui_dtypes)

        _ui_shapes = ui_shapes.copy()
        del _ui_shapes['fixed']
        self.h_button_group_shapes.set_buttons(_ui_shapes)

        self.clear()
        self.adjustSize()


    def clear(self) -> None:
        for b in (
            *self.h_button_group_dtypes.buttons(),
            *self.h_button_group_shapes.buttons()
        ):
            b.setChecked(False)
            b.setCheckable(False)

        for l in self.findChildren(QLineEdit):
            l.clear()
            l.setReadOnly(True)
        self.label_resolution.clear()


    def _set_widgets_visible(self, layout: QLayout, enable: bool):
        """Recursively hide all widgets in a layout"""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if widget := item.widget():
                widget.setVisible(enable)
            elif child_layout := item.layout():
                self._set_widgets_visible(child_layout, enable=enable)


    def set_shape_visible(self, enable: bool, row: int = -1) -> None:
        if row == -1:
            row = self.main_layout.rowCount() - 1
        self.main_layout.setRowStretch(row, 0)
        for col in range(self.main_layout.columnCount()):
            item = self.main_layout.itemAtPosition(row, col)
            if item:
                # If the item is a widget, hide it
                if widget := item.widget():
                    widget.setVisible(enable)

                elif child_layout := item.layout():
                    self._set_widgets_visible(child_layout, enable=enable)
                    child_layout.invalidate()

        self.main_layout.invalidate()
        self.adjustSize()


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        if model is None or model.framework.type != NnFrameworkType.ONNX:
            self.setEnabled(False)
            self.setVisible(False)
            return

        self.setVisible(True)
        self.setEnabled(True)
        self.lineedit_opset.setText(f"{model.opset}")

        for b in (
            *self.h_button_group_dtypes.buttons(),
            *self.h_button_group_shapes.buttons()
        ):
            b.setEnabled(True)
            b.setCheckable(True)

        # datatypes
        if 'fp32' in model.dtypes and 'fp16' in model.dtypes:
            alog.error("ERRROR, onnx has both fp16 and fp32")

        dtype = model.io_dtypes['input']
        for b in self.h_button_group_dtypes.buttons():
            if b.key == dtype:
                b.setEnabled(True)
                b.setChecked(True)
            else:
                b.setEnabled(False)

        # Shape strategy
        if model.shape_strategy.type == 'static':
            self.set_shape_visible(True)

            self.h_button_group_shapes.get_button('static').setChecked(True)
            self.h_button_group_shapes.get_button('dynamic').setEnabled(False)
            size = " x ".join(map(str, model.shape_strategy.opt_size))
            self.lineedit_shape.setText(size)
            self.label_resolution.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), ""))

        else:
            self.h_button_group_shapes.get_button('dynamic').setEnabled(True)
            self.h_button_group_shapes.get_button('static').setEnabled(False)
            self.set_shape_visible(False)

        # Do not allow clicking on a Qadiobutton or selectin a text
        for b in (
            *self.h_button_group_dtypes.buttons(),
            *self.h_button_group_shapes.buttons()
        ):
            b.setCheckable(False)
            b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
