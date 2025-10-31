from __future__ import annotations
from pprint import pprint
from typing import TYPE_CHECKING
from warnings import warn
from hwidgets import HStyle
from pynnlib import (
    NnModel,
    NnFrameworkType,
)

from .common import (
    predefined_shapes_inv,
)
from .logger import alog
from .ui_types import (
    ui_dtypes,
    ui_typing,
    ui_shapes,
)

from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QCheckBox,
    QLineEdit,
    QRadioButton,
    QLayout,
    QMainWindow,
)
from .designer.ui_tensorrt_widget import Ui_TensorRTWidget
if TYPE_CHECKING:
    from .main_window import MainWindow



class TensorRTWidget(QWidget, Ui_TensorRTWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._main_window: MainWindow = None

        self.h_button_group_dtypes.set_buttons(ui_dtypes)
        self.h_button_group_typing.set_buttons(ui_typing)
        self.h_button_group_shapes.set_buttons(ui_shapes)

        self.size_widgets: tuple[tuple[QLineEdit, QLineEdit, QLineEdit]] = (
            (self.label_size_min, self.lineedit_shape_min, self.label_resolution_min),
            (self.label_size_opt, self.lineedit_shape_opt, self.label_resolution_opt),
            (self.label_size_max, self.lineedit_shape_max, self.label_resolution_max),
        )

        self.editable_widgets: list[type[QWidget]] = [
            *self.findChildren(QRadioButton),
            *self.findChildren(QCheckBox),
            *self.findChildren(QLineEdit),
            *[w for group in self.size_widgets for w in group],
        ]

        for w in self.editable_widgets:
            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            w.setEnabled(True)

        self.clear()
        # self.setEnabled(False)
        self.adjustSize()
        self.default_row_min_height: int = self.main_layout.rowMinimumHeight(
            self.main_layout.rowCount() - 1
        )


    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window


    def clear(self) -> None:
        for w in (
            *self.findChildren(QCheckBox),
            *self.findChildren(QRadioButton)
        ):
            w.setChecked(False)
            w.setCheckable(False)
        for w in self.findChildren(QLineEdit):
            w.setEnabled(True)
            w.setReadOnly(True)
            w.clear()
        self.label_resolution_min.clear()
        self.label_resolution_opt.clear()
        self.label_resolution_max.clear()
        self.label_resolution_opt.clear()
        self.label_resolution_max.clear()


    def set_row_visible(self, rows: tuple[int], visible: bool) -> None:
        for row in rows:
            label: QWidget = self.main_layout.itemAtPosition(row, 0).widget()
            label.setVisible(visible)
            label.setMaximumHeight(0 if not visible else 50)

            field: QWidget = self.main_layout.itemAtPosition(row, 1)
            layout: QLayout = field.layout()
            for i in range(layout.count()):
                item = layout.itemAt(i).widget()
                if item:
                    item.setVisible(visible)
                    item.setMaximumHeight(0 if not visible else 50)

            if visible:
                self.main_layout.setRowMinimumHeight(row, 0 if not visible else self.default_row_min_height)
                self.main_layout.setRowStretch(row, 0)

        self.main_layout.activate()


    def refresh_model_info(self, model: NnModel | None) -> None:
        if model.framework.type != NnFrameworkType.TENSORRT:
            self.clear()
            return

        self.setEnabled(True)

        # If compatible, it displays the installed tensorrt version
        if model.engine_version:
            self.lineedit_engine_version.setText(f"{model.engine_version}")

        if model.opset:
            self.lineedit_opset.setText(f"{model.opset}")

        for b in (
            *self.h_button_group_dtypes.buttons(),
            *self.h_button_group_typing.buttons(),
            *self.h_button_group_shapes.buttons()
        ):
            b.setEnabled(True)
            b.setCheckable(True)

        # dtype: corresponds to input dtype
        dtype = model.io_dtypes['input']
        for b in self.h_button_group_dtypes.buttons():
            if b.key == dtype:
                b.setEnabled(True)
                b.setChecked(True)
            else:
                b.setEnabled(False)

        # typing
        typing: str = model.metadata.get("typing", "weak")
        if typing == "":
            for b in self.h_button_group_typing.buttons():
                b.setChecked(False)
                b.setEnabled(False)
        else:
            for b in self.h_button_group_typing.buttons():
                if b.key == typing:
                    b.setEnabled(True)
                    b.setChecked(True)
                else:
                    b.setChecked(False)
                    b.setEnabled(False)

        # shape strategy and sizes
        size = " x ".join(map(str, model.shape_strategy.opt_size))
        self.lineedit_shape_opt.setText(size)
        self.label_resolution_opt.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), ""))

        shape_strategy: str = model.shape_strategy.type
        for b in self.h_button_group_shapes.buttons():
            if b.key == shape_strategy:
                b.setEnabled(True)
                b.setChecked(True)
            else:
                b.setChecked(False)
                b.setEnabled(False)

        if shape_strategy in ('static', 'fixed'):
            self.set_row_visible((5, 7), visible=False)

        elif shape_strategy == 'dynamic':
            self.set_row_visible((5, 7), visible=True)

            size = " x ".join(map(str, model.shape_strategy.min_size))
            self.lineedit_shape_min.setText(size)
            self.label_resolution_min.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), "failed"))

            size = " x ".join(map(str, model.shape_strategy.max_size))
            self.lineedit_shape_max.setText(size)
            self.label_resolution_max.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), "failed"))

        else:
            alog.error(f"unknown shape strategy: {shape_strategy}")

        # Disable editable widgets but set color in black
        for w in self.findChildren(QLineEdit):
            w.setEnabled(True)
        # self.setStyleSheet("""
        #     QRadioButton:disabled { color: black; }
        #     QCheckBox:disabled { color: black; }
        #     QLineEdit:disabled { color: black; }
        # """)

        for b in (
            *self.h_button_group_dtypes.buttons(),
            *self.h_button_group_typing.buttons(),
            *self.h_button_group_shapes.buttons()
        ):
            b.setCheckable(False)
            b.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
