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

        # dtype: corresponds to input dtype
        if model.io_dtypes['input'] == 'fp32':
            self.radio_fp32.setCheckable(True)
            self.radio_fp32.setChecked(True)
        elif model.io_dtypes['input'] == 'fp16':
            self.radio_fp16.setCheckable(True)
            self.radio_fp16.setChecked(True)
        elif model.io_dtypes['input'] == 'bf16':
            self.radio_bf16.setCheckable(True)
            self.radio_bf16.setChecked(True)
        else:
            print("Error: dtype is not found")

        # typing
        typing: str = model.metadata.get("typing", "")
        if typing == 'strong':
            self.radio_strong.setCheckable(True)
            self.radio_strong.setChecked(True)
        elif typing == 'weak':
            self.radio_weak.setCheckable(True)
            self.radio_weak.setChecked(True)

        # shape strategy and sizes
        size = " x ".join(map(str, model.shape_strategy.opt_size))
        self.lineedit_shape_opt.setText(size)
        self.label_resolution_opt.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), ""))

        if model.shape_strategy.type in ('static', 'fixed'):
            if 'static' in model.shape_strategy.type:
                self.radio_static.setCheckable(True)
                self.radio_static.setChecked(True)
            else:
                self.radio_fixed.setCheckable(True)
                self.radio_fixed.setChecked(True)

            self.set_row_visible((5, 7), visible=False)

        elif model.shape_strategy.type == 'dynamic':
            self.radio_dynamic.setCheckable(True)
            self.radio_dynamic.setChecked(True)

            self.set_row_visible((5, 7), visible=True)

            size = " x ".join(map(str, model.shape_strategy.min_size))
            self.lineedit_shape_min.setText(size)
            self.label_resolution_min.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), "failed"))

            size = " x ".join(map(str, model.shape_strategy.max_size))
            self.lineedit_shape_max.setText(size)
            self.label_resolution_max.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), "failed"))

        else:
            warn("shape strategy is unknow")

        # Disable editable widgets but set color in black
        for w in (
            *self.findChildren(QLineEdit),
            *self.findChildren(QRadioButton),
            *self.findChildren(QCheckBox)
        ):
            w.setEnabled(True)
        # self.setStyleSheet("""
        #     QRadioButton:disabled { color: black; }
        #     QCheckBox:disabled { color: black; }
        #     QLineEdit:disabled { color: black; }
        # """)
