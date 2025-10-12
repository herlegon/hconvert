from __future__ import annotations
from pprint import pprint
from warnings import warn

from pynnlib import (
    NnModel,
    NnFrameworkType,
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

from pynnlib.utils.p_print import *

from .designer.ui_tensorrt_widget import Ui_TensorRTWidget
from .common import (
    predefined_shapes_inv,
)


class TensorRTWidget(QWidget, Ui_TensorRTWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setupUi(self)
        self._parent: QMainWindow = parent

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

        self.clear()
        self.setEnabled(False)
        self.adjustSize()
        self.default_row_min_height: int = self.main_layout.rowMinimumHeight(
            self.main_layout.rowCount() - 1
        )


    def clear(self) -> None:
        for w in (
            *self.findChildren(QCheckBox),
            *self.findChildren(QRadioButton)
        ):
            w.setChecked(False)
            w.setCheckable(False)
        for w in self.findChildren(QLineEdit):
            w.clear()
        self.label_resolution_min.clear()
        self.label_resolution_opt.clear()
        self.label_resolution_max.clear()


    def set_parent(self, parent: QMainWindow) -> None:
        self._parent = parent


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
            self.checkbox_fp32.setCheckable(True)
            self.checkbox_fp32.setChecked(True)
        elif model.io_dtypes['input'] == 'fp16':
            self.checkbox_fp16.setCheckable(True)
            self.checkbox_fp16.setChecked(True)
        elif model.io_dtypes['input'] == 'fp16':
            self.checkbox_bf16.setCheckable(True)
            self.checkbox_bf16.setChecked(True)
        else:
            print("Error: dtype is not found")

        # typing
        typing: str = model.metadata.get("typing", "")
        if typing == 'strong':
            self.radiobutton_strong.setCheckable(True)
            self.radiobutton_strong.setChecked(True)
        elif typing == 'weak':
            self.radiobutton_weak.setCheckable(True)
            self.radiobutton_weak.setChecked(True)

        # shape strategy and sizes
        size = " x ".join(map(str, model.shape_strategy.opt_size))
        self.lineedit_shape_opt.setText(size)
        self.label_resolution_opt.setText(predefined_shapes_inv.get(size.replace(" x ", "x"), ""))

        if model.shape_strategy.type in ('static', 'fixed'):
            if 'static' in model.shape_strategy.type:
                self.radiobutton_static.setCheckable(True)
                self.radiobutton_static.setChecked(True)
            else:
                self.radiobutton_fixed.setCheckable(True)
                self.radiobutton_fixed.setChecked(True)

            self.set_row_visible((5, 7), visible=False)

        elif model.shape_strategy.type == 'dynamic':
            self.radiobutton_dynamic.setCheckable(True)
            self.radiobutton_dynamic.setChecked(True)

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
            w.setEnabled(False)
        self.setStyleSheet("""
            QRadioButton:disabled { color: black; }
            QCheckBox:disabled { color: black; }
            QLineEdit:disabled { color: black; }
        """)
