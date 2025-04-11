from PySide6.QtWidgets import (
    QTableWidgetItem,
    QWidget,
    QCheckBox,
    QHBoxLayout,
    QSlider,
    QAbstractSpinBox,
    QLineEdit,
    QComboBox,
)

from .designer.ui_onnx_widget import Ui_OnnxWidget

class OnnxWidget(QWidget, Ui_OnnxWidget):
    def __init__(self, parent, editable: bool = False):
        super().__init__(parent)
        self.setupUi(self)
        self.editable: bool = editable
        self.saved_shape: dict[str, str] = {
            'preset': "",
            'custom': "",
        }

        self.spinbox_version.clear()
        self.radiobutton_fp32.setChecked(False)
        self.radiobutton_fp16.setChecked(False)
        self.radiobutton_static.setChecked(False)
        self.radiobutton_dynamic.setChecked(False)
        self.combobox_resolution.clear()
        self.combobox_resolution_custom.clear()

        self.lineedit_resolution = QLineEdit()
        self.lineedit_resolution.setReadOnly(True)

        self.lineedit_resolution_custom = QLineEdit()
        self.lineedit_resolution_custom.setReadOnly(True)

        self.widget_resolution_custom: QLineEdit | QComboBox = self.combobox_resolution_custom
        self.widget_resolution: QLineEdit | QComboBox = self.combobox_resolution

        self.set_shape_resolution_enabled(False)
        self.setEnabled(False)
        self.adjustSize()


    def set_editable(self, editable: bool) -> None:
        if editable:
            self.widget_resolution_custom: QLineEdit | QComboBox = self.combobox_resolution_custom
            self.widget_resolution: QLineEdit | QComboBox = self.combobox_resolution

        else:
            self.spinbox_version.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            self.combobox_resolution.setEditable(False)
            self.main_layout.replaceWidget(self.combobox_resolution, self.lineedit_resolution)
            self.combobox_resolution.deleteLater()
            self.widget_resolution = self.lineedit_resolution
            self.combobox_resolution_custom.setEditable(False)
            self.main_layout.replaceWidget(self.combobox_resolution_custom, self.lineedit_resolution_custom)
            self.combobox_resolution_custom.deleteLater()
            self.widget_resolution_custom = self.lineedit_resolution_custom
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


