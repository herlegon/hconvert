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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QComboBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_OnnxWidget(object):
    def setupUi(self, OnnxWidget):
        if not OnnxWidget.objectName():
            OnnxWidget.setObjectName(u"OnnxWidget")
        OnnxWidget.resize(300, 176)
        self.verticalLayout = QVBoxLayout(OnnxWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupbox_onnx_conversion = QGroupBox(OnnxWidget)
        self.groupbox_onnx_conversion.setObjectName(u"groupbox_onnx_conversion")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupbox_onnx_conversion.sizePolicy().hasHeightForWidth())
        self.groupbox_onnx_conversion.setSizePolicy(sizePolicy)
        self.groupbox_onnx_conversion.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.groupbox_onnx_conversion)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.main_layout = QFormLayout()
        self.main_layout.setObjectName(u"main_layout")
        self.label_version = QLabel(self.groupbox_onnx_conversion)
        self.label_version.setObjectName(u"label_version")

        self.main_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_version)

        self.spinbox_version = QSpinBox(self.groupbox_onnx_conversion)
        self.spinbox_version.setObjectName(u"spinbox_version")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinbox_version.sizePolicy().hasHeightForWidth())
        self.spinbox_version.setSizePolicy(sizePolicy1)
        self.spinbox_version.setMinimum(15)
        self.spinbox_version.setMaximum(21)
        self.spinbox_version.setValue(20)

        self.main_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinbox_version)

        self.label_datatype = QLabel(self.groupbox_onnx_conversion)
        self.label_datatype.setObjectName(u"label_datatype")

        self.main_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_datatype)

        self.layout_datatype = QHBoxLayout()
        self.layout_datatype.setObjectName(u"layout_datatype")
        self.radiobutton_fp32 = QRadioButton(self.groupbox_onnx_conversion)
        self.buttonGroup = QButtonGroup(OnnxWidget)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radiobutton_fp32)
        self.radiobutton_fp32.setObjectName(u"radiobutton_fp32")

        self.layout_datatype.addWidget(self.radiobutton_fp32)

        self.radiobutton_fp16 = QRadioButton(self.groupbox_onnx_conversion)
        self.buttonGroup.addButton(self.radiobutton_fp16)
        self.radiobutton_fp16.setObjectName(u"radiobutton_fp16")

        self.layout_datatype.addWidget(self.radiobutton_fp16)

        self.horizontalSpacer_6 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_datatype.addItem(self.horizontalSpacer_6)


        self.main_layout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_datatype)

        self.label_shape_strategy = QLabel(self.groupbox_onnx_conversion)
        self.label_shape_strategy.setObjectName(u"label_shape_strategy")

        self.main_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_shape_strategy)

        self.layout_shape_strategy = QHBoxLayout()
        self.layout_shape_strategy.setObjectName(u"layout_shape_strategy")
        self.radiobutton_dynamic = QRadioButton(self.groupbox_onnx_conversion)
        self.buttonGroup_2 = QButtonGroup(OnnxWidget)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.radiobutton_dynamic)
        self.radiobutton_dynamic.setObjectName(u"radiobutton_dynamic")
        self.radiobutton_dynamic.setChecked(True)

        self.layout_shape_strategy.addWidget(self.radiobutton_dynamic)

        self.radiobutton_static = QRadioButton(self.groupbox_onnx_conversion)
        self.buttonGroup_2.addButton(self.radiobutton_static)
        self.radiobutton_static.setObjectName(u"radiobutton_static")

        self.layout_shape_strategy.addWidget(self.radiobutton_static)

        self.horizontalSpacer_7 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_shape_strategy.addItem(self.horizontalSpacer_7)


        self.main_layout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layout_shape_strategy)

        self.label_shape = QLabel(self.groupbox_onnx_conversion)
        self.label_shape.setObjectName(u"label_shape")
        self.label_shape.setEnabled(True)

        self.main_layout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_shape)

        self.layout_resolution = QHBoxLayout()
        self.layout_resolution.setObjectName(u"layout_resolution")
        self.combobox_resolution = QComboBox(self.groupbox_onnx_conversion)
        self.combobox_resolution.addItem("")
        self.combobox_resolution.addItem("")
        self.combobox_resolution.addItem("")
        self.combobox_resolution.addItem("")
        self.combobox_resolution.addItem("")
        self.combobox_resolution.setObjectName(u"combobox_resolution")
        self.combobox_resolution.setEditable(False)
        self.combobox_resolution.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.combobox_resolution.setFrame(True)
        self.combobox_resolution.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.layout_resolution.addWidget(self.combobox_resolution)

        self.combobox_resolution_custom = QComboBox(self.groupbox_onnx_conversion)
        self.combobox_resolution_custom.addItem("")
        self.combobox_resolution_custom.addItem("")
        self.combobox_resolution_custom.addItem("")
        self.combobox_resolution_custom.addItem("")
        self.combobox_resolution_custom.addItem("")
        self.combobox_resolution_custom.setObjectName(u"combobox_resolution_custom")
        self.combobox_resolution_custom.setEditable(True)
        self.combobox_resolution_custom.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)

        self.layout_resolution.addWidget(self.combobox_resolution_custom)


        self.main_layout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.layout_resolution)


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
        self.label_shape.setText(QCoreApplication.translate("OnnxWidget", u"Shape", None))
        self.combobox_resolution.setItemText(0, QCoreApplication.translate("OnnxWidget", u"320p", None))
        self.combobox_resolution.setItemText(1, QCoreApplication.translate("OnnxWidget", u"480p", None))
        self.combobox_resolution.setItemText(2, QCoreApplication.translate("OnnxWidget", u"720p", None))
        self.combobox_resolution.setItemText(3, QCoreApplication.translate("OnnxWidget", u"1080p (2K)", None))
        self.combobox_resolution.setItemText(4, QCoreApplication.translate("OnnxWidget", u"4K", None))

        self.combobox_resolution_custom.setItemText(0, QCoreApplication.translate("OnnxWidget", u"8x8", None))
        self.combobox_resolution_custom.setItemText(1, QCoreApplication.translate("OnnxWidget", u"640x480", None))
        self.combobox_resolution_custom.setItemText(2, QCoreApplication.translate("OnnxWidget", u"705x480", None))
        self.combobox_resolution_custom.setItemText(3, QCoreApplication.translate("OnnxWidget", u"1440x1080", None))
        self.combobox_resolution_custom.setItemText(4, QCoreApplication.translate("OnnxWidget", u"1920x1080", None))

    # retranslateUi

