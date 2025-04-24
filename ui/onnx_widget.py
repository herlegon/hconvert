from __future__ import annotations
from pynnlib import (
    NnModel,
    NnFrameworkType,
    OnnxModel,
)

from PySide6.QtCore import (
        QSize,
        Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QAbstractSpinBox,
    QLineEdit,
    QComboBox,
    QSizePolicy,
)

from pynnlib.utils.p_print import red
from .designer.ui_onnx_widget import Ui_OnnxWidget


predefined_shapes: dict[str, tuple[int, int]] = {
    "480p 16:9 (DVD)": (854, 480),
    "480p 4:3": (640, 480),
    "480p NTSC": (720, 480),
    "576p 4:3 sq": (768, 576),
    "720p 4:3": (960, 720),
    "720p (HD ready)": (1280, 720),
    "1080p (Full HD)": (1920, 1080),
    "2160p (4K UHDTV)": (3840, 2160)
}

predefined_shapes_inv: dict[str, str] = {
    "x".join(map(str, v)): k for k, v in predefined_shapes.items()
}


class OnnxWidget(QWidget, Ui_OnnxWidget):
    def __init__(self, parent, editable: bool = False):
        super().__init__(parent)
        self.setupUi(self)
        self.editable: bool = editable
        self.saved_shape: dict[str, str] = {
            'preset': "",
            'custom': "",
        }

        self.clear()

        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.lineedit_resolution = QLineEdit()
        self.lineedit_resolution.setReadOnly(True)
        self.lineedit_resolution.setSizePolicy(size_policy)
        self.lineedit_resolution.setMaximumSize(QSize(80, 16777215))


        self.lineedit_resolution_custom = QLineEdit()
        self.lineedit_resolution_custom.setReadOnly(True)
        self.lineedit_resolution_custom.setSizePolicy(size_policy)
        self.lineedit_resolution_custom.setMaximumSize(QSize(80, 16777215))

        self.widget_resolution_custom: QLineEdit | QComboBox = self.combobox_resolution_custom
        self.widget_resolution: QLineEdit | QComboBox = self.combobox_resolution

        self.set_shape_resolution_enabled(False)
        self.set_editable(editable=editable)
        self.setEnabled(False)
        self.adjustSize()


    def clear(self) -> None:
        self.spinbox_opset.clear()
        self.radiobutton_fp32.setChecked(False)
        self.radiobutton_fp16.setChecked(False)
        self.radiobutton_static.setChecked(False)
        self.radiobutton_dynamic.setChecked(False)
        try:
            self.combobox_resolution.clear()
            self.combobox_resolution_custom.clear()
        except:
            pass
        try:
            self.lineedit_resolution.clear()
            self.lineedit_resolution_custom.clear()
        except:
            pass



    def set_editable(self, editable: bool) -> None:
        self.spinbox_opset.setReadOnly(not editable)
        self.spinbox_opset.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.spinbox_opset.lineEdit().setReadOnly(not editable)
        self.spinbox_opset.lineEdit().setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.radiobutton_fp32.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.radiobutton_fp16.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.radiobutton_static.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.radiobutton_dynamic.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if editable:
            self.widget_resolution_custom: QLineEdit | QComboBox = self.combobox_resolution_custom
            self.widget_resolution: QLineEdit | QComboBox = self.combobox_resolution

            self.combobox_resolution.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.combobox_resolution.setEnabled(not editable)
            self.combobox_resolution_custom.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.combobox_resolution_custom.setEnabled(not editable)


        else:
            self.spinbox_opset.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            self.combobox_resolution.setEditable(False)
            self.main_layout.replaceWidget(self.combobox_resolution, self.lineedit_resolution)
            self.combobox_resolution.deleteLater()
            self.widget_resolution = self.lineedit_resolution
            self.combobox_resolution_custom.setEditable(False)
            self.main_layout.replaceWidget(self.combobox_resolution_custom, self.lineedit_resolution_custom)
            self.combobox_resolution_custom.deleteLater()
            self.widget_resolution_custom = self.lineedit_resolution_custom

            self.lineedit_resolution.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.lineedit_resolution.setReadOnly(not editable)
            self.lineedit_resolution_custom.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.lineedit_resolution_custom.setReadOnly(not editable)

        self.editable = editable


    def set_shape_resolution_enabled(self, enable: bool) -> None:
        self.label_shape.setEnabled(enable)
        self.widget_resolution.setEnabled(enable)
        self.widget_resolution_custom.setEnabled(enable)

        if self.editable:
            if enable:
                self.widget_resolution.setCurrentText(self.saved_shape['preset'])
                self.widget_resolution_custom.setCurrentText(self.saved_shape['custom'])
            else:
                self.saved_shape = {
                    'preset': self.widget_resolution.currentText(),
                    'custom': self.widget_resolution_custom.currentText(),
                }
                self.widget_resolution.clear()
                self.widget_resolution_custom.clear()


    def refresh_model_info(self, model: NnModel | None) -> None:
        self.clear()
        print(model)
        if model is None or model.framework.type != NnFrameworkType.ONNX:
            return

        self.setEnabled(True)
        self.spinbox_opset.setValue(model.opset)

        self.widget_resolution.clear()
        self.widget_resolution_custom.clear()
        if 'static' in model.shape_strategy.type:
            self.radiobutton_static.setChecked(True)
            self.label_shape.setEnabled(True)
            k = 'x'.join(map(str, model.shape_strategy.opt_size))
            l = predefined_shapes_inv.get(k, "")
            if self.editable:
                self.widget_resolution.setCurrentText(l)
                self.widget_resolution_custom.setCurrentText(k)
            else:
                self.widget_resolution.setText(l)
                self.widget_resolution_custom.setText(k)

        else:
            self.radiobutton_dynamic.setChecked(True)
            self.label_shape.setEnabled(True)

        self.radiobutton_static.setEnabled(False)
        self.radiobutton_dynamic.setEnabled(False)

        if 'fp32' in model.dtypes:
            self.radiobutton_fp32.setChecked(True)
        if 'fp16' in model.dtypes:
            self.radiobutton_fp16.setChecked(True)
        self.radiobutton_fp32.setCheckable(False)
        self.radiobutton_fp16.setCheckable(False)

        if 'fp32' in model.dtypes and 'fp16' in model.dtypes:
            print(red("ERRROR, onnx has both fp16 and fp32"))


