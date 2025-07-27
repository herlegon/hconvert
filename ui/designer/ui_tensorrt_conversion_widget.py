# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_tensorrt_conversion_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_TensorRTConversionWidget(object):
    def setupUi(self, TensorRTConversionWidget):
        if not TensorRTConversionWidget.objectName():
            TensorRTConversionWidget.setObjectName(u"TensorRTConversionWidget")
        TensorRTConversionWidget.resize(398, 250)
        self.verticalLayout = QVBoxLayout(TensorRTConversionWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupbox_tensorrt_conversion = QGroupBox(TensorRTConversionWidget)
        self.groupbox_tensorrt_conversion.setObjectName(u"groupbox_tensorrt_conversion")
        self.groupbox_tensorrt_conversion.setCheckable(True)
        self.verticalLayout_4 = QVBoxLayout(self.groupbox_tensorrt_conversion)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.main_layout = QFormLayout()
        self.main_layout.setObjectName(u"main_layout")
        self.layout_datatype = QHBoxLayout()
        self.layout_datatype.setObjectName(u"layout_datatype")
        self.checkbox_fp32 = QCheckBox(self.groupbox_tensorrt_conversion)
        self.checkbox_fp32.setObjectName(u"checkbox_fp32")
        self.checkbox_fp32.setEnabled(False)
        self.checkbox_fp32.setChecked(True)

        self.layout_datatype.addWidget(self.checkbox_fp32)

        self.checkbox_fp16 = QCheckBox(self.groupbox_tensorrt_conversion)
        self.buttonGroup = QButtonGroup(TensorRTConversionWidget)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.checkbox_fp16)
        self.checkbox_fp16.setObjectName(u"checkbox_fp16")
        self.checkbox_fp16.setEnabled(True)

        self.layout_datatype.addWidget(self.checkbox_fp16)

        self.checkbox_bf16 = QCheckBox(self.groupbox_tensorrt_conversion)
        self.buttonGroup.addButton(self.checkbox_bf16)
        self.checkbox_bf16.setObjectName(u"checkbox_bf16")
        self.checkbox_bf16.setEnabled(True)

        self.layout_datatype.addWidget(self.checkbox_bf16)

        self.horizontalSpacer_6 = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_datatype.addItem(self.horizontalSpacer_6)


        self.main_layout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_datatype)

        self.label_shape_strategy = QLabel(self.groupbox_tensorrt_conversion)
        self.label_shape_strategy.setObjectName(u"label_shape_strategy")

        self.main_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_shape_strategy)

        self.layout_shape_strategy = QHBoxLayout()
        self.layout_shape_strategy.setObjectName(u"layout_shape_strategy")
        self.checkbox_dynamic = QCheckBox(self.groupbox_tensorrt_conversion)
        self.buttongroup_shape_strategy = QButtonGroup(TensorRTConversionWidget)
        self.buttongroup_shape_strategy.setObjectName(u"buttongroup_shape_strategy")
        self.buttongroup_shape_strategy.addButton(self.checkbox_dynamic)
        self.checkbox_dynamic.setObjectName(u"checkbox_dynamic")
        self.checkbox_dynamic.setCheckable(True)
        self.checkbox_dynamic.setChecked(False)
        self.checkbox_dynamic.setAutoExclusive(True)

        self.layout_shape_strategy.addWidget(self.checkbox_dynamic)

        self.checkbox_fixed = QCheckBox(self.groupbox_tensorrt_conversion)
        self.buttongroup_shape_strategy.addButton(self.checkbox_fixed)
        self.checkbox_fixed.setObjectName(u"checkbox_fixed")
        self.checkbox_fixed.setCheckable(True)
        self.checkbox_fixed.setChecked(False)
        self.checkbox_fixed.setAutoExclusive(True)

        self.layout_shape_strategy.addWidget(self.checkbox_fixed)

        self.horizontalSpacer_7 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_shape_strategy.addItem(self.horizontalSpacer_7)


        self.main_layout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layout_shape_strategy)

        self.label_shape_w = QLabel(self.groupbox_tensorrt_conversion)
        self.label_shape_w.setObjectName(u"label_shape_w")
        self.label_shape_w.setEnabled(True)

        self.main_layout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_shape_w)

        self.layout_shape_min = QHBoxLayout()
        self.layout_shape_min.setObjectName(u"layout_shape_min")
        self.spinbox_w_min = QSpinBox(self.groupbox_tensorrt_conversion)
        self.spinbox_w_min.setObjectName(u"spinbox_w_min")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinbox_w_min.sizePolicy().hasHeightForWidth())
        self.spinbox_w_min.setSizePolicy(sizePolicy)
        self.spinbox_w_min.setMinimum(16)
        self.spinbox_w_min.setMaximum(4096)
        self.spinbox_w_min.setSingleStep(1)
        self.spinbox_w_min.setValue(4096)

        self.layout_shape_min.addWidget(self.spinbox_w_min)

        self.label_x_w = QLabel(self.groupbox_tensorrt_conversion)
        self.label_x_w.setObjectName(u"label_x_w")

        self.layout_shape_min.addWidget(self.label_x_w)

        self.spinbox_h_min = QSpinBox(self.groupbox_tensorrt_conversion)
        self.spinbox_h_min.setObjectName(u"spinbox_h_min")
        sizePolicy.setHeightForWidth(self.spinbox_h_min.sizePolicy().hasHeightForWidth())
        self.spinbox_h_min.setSizePolicy(sizePolicy)
        self.spinbox_h_min.setMinimum(16)
        self.spinbox_h_min.setMaximum(2160)
        self.spinbox_h_min.setValue(2160)

        self.layout_shape_min.addWidget(self.spinbox_h_min)

        self.combobox_resolution_min = QComboBox(self.groupbox_tensorrt_conversion)
        self.combobox_resolution_min.addItem("")
        self.combobox_resolution_min.addItem("")
        self.combobox_resolution_min.setObjectName(u"combobox_resolution_min")
        self.combobox_resolution_min.setMinimumSize(QSize(120, 0))
        self.combobox_resolution_min.setMaximumSize(QSize(200, 16777215))
        self.combobox_resolution_min.setEditable(False)
        self.combobox_resolution_min.setMaxCount(20)
        self.combobox_resolution_min.setFrame(True)
        self.combobox_resolution_min.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.layout_shape_min.addWidget(self.combobox_resolution_min)

        self.horizontalSpacer_8 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_shape_min.addItem(self.horizontalSpacer_8)


        self.main_layout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.layout_shape_min)

        self.label_shape_r = QLabel(self.groupbox_tensorrt_conversion)
        self.label_shape_r.setObjectName(u"label_shape_r")
        self.label_shape_r.setEnabled(True)

        self.main_layout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_shape_r)

        self.label_18 = QLabel(self.groupbox_tensorrt_conversion)
        self.label_18.setObjectName(u"label_18")

        self.main_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_18)

        self.combobox_gpu = QComboBox(self.groupbox_tensorrt_conversion)
        self.combobox_gpu.setObjectName(u"combobox_gpu")

        self.main_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.combobox_gpu)

        self.label_16 = QLabel(self.groupbox_tensorrt_conversion)
        self.label_16.setObjectName(u"label_16")

        self.main_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_16)

        self.label_10 = QLabel(self.groupbox_tensorrt_conversion)
        self.label_10.setObjectName(u"label_10")

        self.main_layout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.layout_shape_max = QHBoxLayout()
        self.layout_shape_max.setObjectName(u"layout_shape_max")
        self.spinbox_w_max = QSpinBox(self.groupbox_tensorrt_conversion)
        self.spinbox_w_max.setObjectName(u"spinbox_w_max")
        sizePolicy.setHeightForWidth(self.spinbox_w_max.sizePolicy().hasHeightForWidth())
        self.spinbox_w_max.setSizePolicy(sizePolicy)
        self.spinbox_w_max.setMinimum(16)
        self.spinbox_w_max.setMaximum(4096)
        self.spinbox_w_max.setSingleStep(1)
        self.spinbox_w_max.setValue(4096)

        self.layout_shape_max.addWidget(self.spinbox_w_max)

        self.label_x_w_max = QLabel(self.groupbox_tensorrt_conversion)
        self.label_x_w_max.setObjectName(u"label_x_w_max")

        self.layout_shape_max.addWidget(self.label_x_w_max)

        self.spinbox_h_max = QSpinBox(self.groupbox_tensorrt_conversion)
        self.spinbox_h_max.setObjectName(u"spinbox_h_max")
        sizePolicy.setHeightForWidth(self.spinbox_h_max.sizePolicy().hasHeightForWidth())
        self.spinbox_h_max.setSizePolicy(sizePolicy)
        self.spinbox_h_max.setMinimum(16)
        self.spinbox_h_max.setMaximum(2160)
        self.spinbox_h_max.setValue(2160)

        self.layout_shape_max.addWidget(self.spinbox_h_max)

        self.combobox_resolution_max = QComboBox(self.groupbox_tensorrt_conversion)
        self.combobox_resolution_max.addItem("")
        self.combobox_resolution_max.addItem("")
        self.combobox_resolution_max.setObjectName(u"combobox_resolution_max")
        self.combobox_resolution_max.setMinimumSize(QSize(120, 0))
        self.combobox_resolution_max.setMaximumSize(QSize(200, 16777215))
        self.combobox_resolution_max.setEditable(False)
        self.combobox_resolution_max.setMaxCount(20)
        self.combobox_resolution_max.setFrame(True)
        self.combobox_resolution_max.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.layout_shape_max.addWidget(self.combobox_resolution_max)

        self.horizontalSpacer_10 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_shape_max.addItem(self.horizontalSpacer_10)


        self.main_layout.setLayout(5, QFormLayout.ItemRole.FieldRole, self.layout_shape_max)

        self.layout_shape_opt = QHBoxLayout()
        self.layout_shape_opt.setObjectName(u"layout_shape_opt")
        self.spinbox_w_opt = QSpinBox(self.groupbox_tensorrt_conversion)
        self.spinbox_w_opt.setObjectName(u"spinbox_w_opt")
        sizePolicy.setHeightForWidth(self.spinbox_w_opt.sizePolicy().hasHeightForWidth())
        self.spinbox_w_opt.setSizePolicy(sizePolicy)
        self.spinbox_w_opt.setMinimum(16)
        self.spinbox_w_opt.setMaximum(4096)
        self.spinbox_w_opt.setSingleStep(1)
        self.spinbox_w_opt.setValue(4096)

        self.layout_shape_opt.addWidget(self.spinbox_w_opt)

        self.label_x_w_opt = QLabel(self.groupbox_tensorrt_conversion)
        self.label_x_w_opt.setObjectName(u"label_x_w_opt")

        self.layout_shape_opt.addWidget(self.label_x_w_opt)

        self.spinbox_h_opt = QSpinBox(self.groupbox_tensorrt_conversion)
        self.spinbox_h_opt.setObjectName(u"spinbox_h_opt")
        sizePolicy.setHeightForWidth(self.spinbox_h_opt.sizePolicy().hasHeightForWidth())
        self.spinbox_h_opt.setSizePolicy(sizePolicy)
        self.spinbox_h_opt.setMinimum(16)
        self.spinbox_h_opt.setMaximum(2160)
        self.spinbox_h_opt.setValue(2160)

        self.layout_shape_opt.addWidget(self.spinbox_h_opt)

        self.combobox_resolution_opt = QComboBox(self.groupbox_tensorrt_conversion)
        self.combobox_resolution_opt.addItem("")
        self.combobox_resolution_opt.addItem("")
        self.combobox_resolution_opt.setObjectName(u"combobox_resolution_opt")
        self.combobox_resolution_opt.setMinimumSize(QSize(120, 0))
        self.combobox_resolution_opt.setMaximumSize(QSize(200, 16777215))
        self.combobox_resolution_opt.setEditable(False)
        self.combobox_resolution_opt.setMaxCount(20)
        self.combobox_resolution_opt.setFrame(True)
        self.combobox_resolution_opt.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.layout_shape_opt.addWidget(self.combobox_resolution_opt)

        self.horizontalSpacer_9 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_shape_opt.addItem(self.horizontalSpacer_9)


        self.main_layout.setLayout(4, QFormLayout.ItemRole.FieldRole, self.layout_shape_opt)


        self.verticalLayout_4.addLayout(self.main_layout)


        self.verticalLayout.addWidget(self.groupbox_tensorrt_conversion)


        self.retranslateUi(TensorRTConversionWidget)

        QMetaObject.connectSlotsByName(TensorRTConversionWidget)
    # setupUi

    def retranslateUi(self, TensorRTConversionWidget):
        TensorRTConversionWidget.setWindowTitle(QCoreApplication.translate("TensorRTConversionWidget", u"Form", None))
        self.groupbox_tensorrt_conversion.setTitle(QCoreApplication.translate("TensorRTConversionWidget", u"TensorRT", None))
        self.checkbox_fp32.setText(QCoreApplication.translate("TensorRTConversionWidget", u"fp32", None))
        self.checkbox_fp16.setText(QCoreApplication.translate("TensorRTConversionWidget", u"fp16", None))
        self.checkbox_bf16.setText(QCoreApplication.translate("TensorRTConversionWidget", u"bf16", None))
        self.label_shape_strategy.setText(QCoreApplication.translate("TensorRTConversionWidget", u"Shape strategy", None))
        self.checkbox_dynamic.setText(QCoreApplication.translate("TensorRTConversionWidget", u"dynamic", None))
        self.checkbox_fixed.setText(QCoreApplication.translate("TensorRTConversionWidget", u"fixed", None))
        self.label_shape_w.setText(QCoreApplication.translate("TensorRTConversionWidget", u"Minimum", None))
        self.label_x_w.setText(QCoreApplication.translate("TensorRTConversionWidget", u"x", None))
        self.combobox_resolution_min.setItemText(0, QCoreApplication.translate("TensorRTConversionWidget", u"2160p (4K UHDTV)", None))
        self.combobox_resolution_min.setItemText(1, "")

        self.label_shape_r.setText(QCoreApplication.translate("TensorRTConversionWidget", u"Optimized", None))
        self.label_18.setText(QCoreApplication.translate("TensorRTConversionWidget", u"GPU", None))
        self.label_16.setText(QCoreApplication.translate("TensorRTConversionWidget", u"Precision", None))
        self.label_10.setText(QCoreApplication.translate("TensorRTConversionWidget", u"Maximum", None))
        self.label_x_w_max.setText(QCoreApplication.translate("TensorRTConversionWidget", u"x", None))
        self.combobox_resolution_max.setItemText(0, QCoreApplication.translate("TensorRTConversionWidget", u"2160p (4K UHDTV)", None))
        self.combobox_resolution_max.setItemText(1, "")

        self.label_x_w_opt.setText(QCoreApplication.translate("TensorRTConversionWidget", u"x", None))
        self.combobox_resolution_opt.setItemText(0, QCoreApplication.translate("TensorRTConversionWidget", u"2160p (4K UHDTV)", None))
        self.combobox_resolution_opt.setItemText(1, "")

    # retranslateUi

