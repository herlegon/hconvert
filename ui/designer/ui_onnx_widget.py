# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_onnx_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_OnnxWidget(object):
    def setupUi(self, OnnxWidget):
        if not OnnxWidget.objectName():
            OnnxWidget.setObjectName(u"OnnxWidget")
        OnnxWidget.resize(398, 213)
        self.verticalLayout = QVBoxLayout(OnnxWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupbox_onnx_conversion = QGroupBox(OnnxWidget)
        self.groupbox_onnx_conversion.setObjectName(u"groupbox_onnx_conversion")
        self.verticalLayout_4 = QVBoxLayout(self.groupbox_onnx_conversion)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.main_layout = QFormLayout()
        self.main_layout.setObjectName(u"main_layout")
        self.label_version = QLabel(self.groupbox_onnx_conversion)
        self.label_version.setObjectName(u"label_version")

        self.main_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_version)

        self.spinbox_opset = QSpinBox(self.groupbox_onnx_conversion)
        self.spinbox_opset.setObjectName(u"spinbox_opset")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinbox_opset.sizePolicy().hasHeightForWidth())
        self.spinbox_opset.setSizePolicy(sizePolicy)
        self.spinbox_opset.setMinimumSize(QSize(50, 0))
        self.spinbox_opset.setMaximumSize(QSize(50, 16777215))
        self.spinbox_opset.setMinimum(15)
        self.spinbox_opset.setMaximum(21)
        self.spinbox_opset.setValue(20)

        self.main_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinbox_opset)

        self.label_datatype = QLabel(self.groupbox_onnx_conversion)
        self.label_datatype.setObjectName(u"label_datatype")

        self.main_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_datatype)

        self.layout_datatype = QHBoxLayout()
        self.layout_datatype.setObjectName(u"layout_datatype")
        self.radiobutton_fp32 = QRadioButton(self.groupbox_onnx_conversion)
        self.buttongroup_datatype = QButtonGroup(OnnxWidget)
        self.buttongroup_datatype.setObjectName(u"buttongroup_datatype")
        self.buttongroup_datatype.addButton(self.radiobutton_fp32)
        self.radiobutton_fp32.setObjectName(u"radiobutton_fp32")
        self.radiobutton_fp32.setEnabled(True)
        self.radiobutton_fp32.setCheckable(True)
        self.radiobutton_fp32.setChecked(False)

        self.layout_datatype.addWidget(self.radiobutton_fp32)

        self.radiobutton_fp16 = QRadioButton(self.groupbox_onnx_conversion)
        self.buttongroup_datatype.addButton(self.radiobutton_fp16)
        self.radiobutton_fp16.setObjectName(u"radiobutton_fp16")
        self.radiobutton_fp16.setCheckable(True)

        self.layout_datatype.addWidget(self.radiobutton_fp16)

        self.horizontalSpacer_6 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_datatype.addItem(self.horizontalSpacer_6)


        self.main_layout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_datatype)

        self.label_shape_strategy = QLabel(self.groupbox_onnx_conversion)
        self.label_shape_strategy.setObjectName(u"label_shape_strategy")

        self.main_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_shape_strategy)

        self.layout_shape_strategy = QHBoxLayout()
        self.layout_shape_strategy.setObjectName(u"layout_shape_strategy")
        self.radiobutton_dynamic = QCheckBox(self.groupbox_onnx_conversion)
        self.buttongroup_shape_strategy = QButtonGroup(OnnxWidget)
        self.buttongroup_shape_strategy.setObjectName(u"buttongroup_shape_strategy")
        self.buttongroup_shape_strategy.addButton(self.radiobutton_dynamic)
        self.radiobutton_dynamic.setObjectName(u"radiobutton_dynamic")
        self.radiobutton_dynamic.setCheckable(True)
        self.radiobutton_dynamic.setChecked(False)
        self.radiobutton_dynamic.setAutoExclusive(True)

        self.layout_shape_strategy.addWidget(self.radiobutton_dynamic)

        self.radiobutton_static = QCheckBox(self.groupbox_onnx_conversion)
        self.buttongroup_shape_strategy.addButton(self.radiobutton_static)
        self.radiobutton_static.setObjectName(u"radiobutton_static")
        self.radiobutton_static.setCheckable(True)
        self.radiobutton_static.setChecked(False)
        self.radiobutton_static.setAutoExclusive(True)

        self.layout_shape_strategy.addWidget(self.radiobutton_static)

        self.horizontalSpacer_7 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_shape_strategy.addItem(self.horizontalSpacer_7)


        self.main_layout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layout_shape_strategy)

        self.label_shape_w = QLabel(self.groupbox_onnx_conversion)
        self.label_shape_w.setObjectName(u"label_shape_w")
        self.label_shape_w.setEnabled(True)

        self.main_layout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_shape_w)

        self.layout_resolution_w = QHBoxLayout()
        self.layout_resolution_w.setObjectName(u"layout_resolution_w")
        self.spinbox_w = QSpinBox(self.groupbox_onnx_conversion)
        self.spinbox_w.setObjectName(u"spinbox_w")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinbox_w.sizePolicy().hasHeightForWidth())
        self.spinbox_w.setSizePolicy(sizePolicy1)
        self.spinbox_w.setMinimum(16)
        self.spinbox_w.setMaximum(4096)
        self.spinbox_w.setSingleStep(1)
        self.spinbox_w.setValue(4096)

        self.layout_resolution_w.addWidget(self.spinbox_w)

        self.label_x_w = QLabel(self.groupbox_onnx_conversion)
        self.label_x_w.setObjectName(u"label_x_w")

        self.layout_resolution_w.addWidget(self.label_x_w)

        self.spinbox_h = QSpinBox(self.groupbox_onnx_conversion)
        self.spinbox_h.setObjectName(u"spinbox_h")
        sizePolicy1.setHeightForWidth(self.spinbox_h.sizePolicy().hasHeightForWidth())
        self.spinbox_h.setSizePolicy(sizePolicy1)
        self.spinbox_h.setMinimum(16)
        self.spinbox_h.setMaximum(2160)
        self.spinbox_h.setValue(2160)

        self.layout_resolution_w.addWidget(self.spinbox_h)

        self.combobox_resolution = QComboBox(self.groupbox_onnx_conversion)
        self.combobox_resolution.addItem("")
        self.combobox_resolution.addItem("")
        self.combobox_resolution.setObjectName(u"combobox_resolution")
        self.combobox_resolution.setMinimumSize(QSize(120, 0))
        self.combobox_resolution.setMaximumSize(QSize(200, 16777215))
        self.combobox_resolution.setEditable(False)
        self.combobox_resolution.setMaxCount(20)
        self.combobox_resolution.setFrame(True)
        self.combobox_resolution.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.layout_resolution_w.addWidget(self.combobox_resolution)

        self.horizontalSpacer_8 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_resolution_w.addItem(self.horizontalSpacer_8)


        self.main_layout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.layout_resolution_w)

        self.label_shape_r = QLabel(self.groupbox_onnx_conversion)
        self.label_shape_r.setObjectName(u"label_shape_r")
        self.label_shape_r.setEnabled(True)

        self.main_layout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_shape_r)

        self.layout_resolution_r = QHBoxLayout()
        self.layout_resolution_r.setObjectName(u"layout_resolution_r")
        self.lineedit_w = QLineEdit(self.groupbox_onnx_conversion)
        self.lineedit_w.setObjectName(u"lineedit_w")
        sizePolicy.setHeightForWidth(self.lineedit_w.sizePolicy().hasHeightForWidth())
        self.lineedit_w.setSizePolicy(sizePolicy)
        self.lineedit_w.setMaximumSize(QSize(50, 16777215))
        self.lineedit_w.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_resolution_r.addWidget(self.lineedit_w)

        self.label_x_r = QLabel(self.groupbox_onnx_conversion)
        self.label_x_r.setObjectName(u"label_x_r")

        self.layout_resolution_r.addWidget(self.label_x_r)

        self.lineedit_h = QLineEdit(self.groupbox_onnx_conversion)
        self.lineedit_h.setObjectName(u"lineedit_h")
        sizePolicy.setHeightForWidth(self.lineedit_h.sizePolicy().hasHeightForWidth())
        self.lineedit_h.setSizePolicy(sizePolicy)
        self.lineedit_h.setMaximumSize(QSize(50, 16777215))
        self.lineedit_h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_resolution_r.addWidget(self.lineedit_h)

        self.label_resolution = QLabel(self.groupbox_onnx_conversion)
        self.label_resolution.setObjectName(u"label_resolution")
        self.label_resolution.setMaximumSize(QSize(150, 16777215))
        self.label_resolution.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_resolution_r.addWidget(self.label_resolution)

        self.horizontalSpacer_9 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_resolution_r.addItem(self.horizontalSpacer_9)


        self.main_layout.setLayout(4, QFormLayout.ItemRole.FieldRole, self.layout_resolution_r)


        self.verticalLayout_4.addLayout(self.main_layout)


        self.verticalLayout.addWidget(self.groupbox_onnx_conversion)


        self.retranslateUi(OnnxWidget)

        QMetaObject.connectSlotsByName(OnnxWidget)
    # setupUi

    def retranslateUi(self, OnnxWidget):
        OnnxWidget.setWindowTitle(QCoreApplication.translate("OnnxWidget", u"Form", None))
        self.groupbox_onnx_conversion.setTitle(QCoreApplication.translate("OnnxWidget", u"ONNX", None))
        self.label_version.setText(QCoreApplication.translate("OnnxWidget", u"Version", None))
        self.label_datatype.setText(QCoreApplication.translate("OnnxWidget", u"Datatype", None))
        self.radiobutton_fp32.setText(QCoreApplication.translate("OnnxWidget", u"fp32", None))
        self.radiobutton_fp16.setText(QCoreApplication.translate("OnnxWidget", u"fp16", None))
        self.label_shape_strategy.setText(QCoreApplication.translate("OnnxWidget", u"Shape strategy", None))
        self.radiobutton_dynamic.setText(QCoreApplication.translate("OnnxWidget", u"dynamic", None))
        self.radiobutton_static.setText(QCoreApplication.translate("OnnxWidget", u"static", None))
        self.label_shape_w.setText(QCoreApplication.translate("OnnxWidget", u"Input shape", None))
        self.label_x_w.setText(QCoreApplication.translate("OnnxWidget", u"x", None))
        self.combobox_resolution.setItemText(0, QCoreApplication.translate("OnnxWidget", u"2160p (4K UHDTV)", None))
        self.combobox_resolution.setItemText(1, "")

        self.label_shape_r.setText(QCoreApplication.translate("OnnxWidget", u"Input shape", None))
        self.lineedit_w.setText(QCoreApplication.translate("OnnxWidget", u"4096", None))
        self.label_x_r.setText(QCoreApplication.translate("OnnxWidget", u"x", None))
        self.lineedit_h.setText(QCoreApplication.translate("OnnxWidget", u"2160", None))
        self.label_resolution.setText(QCoreApplication.translate("OnnxWidget", u"2160p (4K UHDTV)", None))
    # retranslateUi

