# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_tensorrt_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_TensorRTWidget(object):
    def setupUi(self, TensorRTWidget):
        if not TensorRTWidget.objectName():
            TensorRTWidget.setObjectName(u"TensorRTWidget")
        TensorRTWidget.resize(390, 107)
        self.verticalLayout = QVBoxLayout(TensorRTWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupbox_tensorrt_model = QGroupBox(TensorRTWidget)
        self.groupbox_tensorrt_model.setObjectName(u"groupbox_tensorrt_model")
        self.verticalLayout_6 = QVBoxLayout(self.groupbox_tensorrt_model)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(6, 6, 6, 6)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_30 = QLabel(self.groupbox_tensorrt_model)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMinimumSize(QSize(120, 0))

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_30)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.checkbox_dynamic = QCheckBox(self.groupbox_tensorrt_model)
        self.checkbox_dynamic.setObjectName(u"checkbox_dynamic")
        self.checkbox_dynamic.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkbox_dynamic.sizePolicy().hasHeightForWidth())
        self.checkbox_dynamic.setSizePolicy(sizePolicy)
        self.checkbox_dynamic.setChecked(True)

        self.horizontalLayout_21.addWidget(self.checkbox_dynamic)

        self.checkbox_static_2 = QCheckBox(self.groupbox_tensorrt_model)
        self.checkbox_static_2.setObjectName(u"checkbox_static_2")
        self.checkbox_static_2.setEnabled(True)
        sizePolicy.setHeightForWidth(self.checkbox_static_2.sizePolicy().hasHeightForWidth())
        self.checkbox_static_2.setSizePolicy(sizePolicy)

        self.horizontalLayout_21.addWidget(self.checkbox_static_2)

        self.checkbox_static = QCheckBox(self.groupbox_tensorrt_model)
        self.checkbox_static.setObjectName(u"checkbox_static")
        self.checkbox_static.setEnabled(True)
        sizePolicy.setHeightForWidth(self.checkbox_static.sizePolicy().hasHeightForWidth())
        self.checkbox_static.setSizePolicy(sizePolicy)

        self.horizontalLayout_21.addWidget(self.checkbox_static, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalSpacer_7 = QSpacerItem(10, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_7)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_21)

        self.label_12 = QLabel(self.groupbox_tensorrt_model)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.layout_resolution_r = QHBoxLayout()
        self.layout_resolution_r.setObjectName(u"layout_resolution_r")
        self.lineedit_shape = QLineEdit(self.groupbox_tensorrt_model)
        self.lineedit_shape.setObjectName(u"lineedit_shape")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineedit_shape.sizePolicy().hasHeightForWidth())
        self.lineedit_shape.setSizePolicy(sizePolicy1)
        self.lineedit_shape.setMaximumSize(QSize(100, 16777215))
        self.lineedit_shape.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_resolution_r.addWidget(self.lineedit_shape)

        self.label_resolution = QLabel(self.groupbox_tensorrt_model)
        self.label_resolution.setObjectName(u"label_resolution")
        self.label_resolution.setMinimumSize(QSize(130, 0))
        self.label_resolution.setMaximumSize(QSize(150, 16777215))
        self.label_resolution.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_resolution_r.addWidget(self.label_resolution)

        self.horizontalSpacer_9 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_resolution_r.addItem(self.horizontalSpacer_9)


        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_resolution_r)


        self.verticalLayout_6.addLayout(self.formLayout)


        self.verticalLayout.addWidget(self.groupbox_tensorrt_model)


        self.retranslateUi(TensorRTWidget)

        QMetaObject.connectSlotsByName(TensorRTWidget)
    # setupUi

    def retranslateUi(self, TensorRTWidget):
        TensorRTWidget.setWindowTitle(QCoreApplication.translate("TensorRTWidget", u"Form", None))
        self.groupbox_tensorrt_model.setTitle(QCoreApplication.translate("TensorRTWidget", u"TensorRT", None))
        self.label_30.setText(QCoreApplication.translate("TensorRTWidget", u"Shape strategy", None))
        self.checkbox_dynamic.setText(QCoreApplication.translate("TensorRTWidget", u"dynamic", None))
        self.checkbox_static_2.setText(QCoreApplication.translate("TensorRTWidget", u"fixed", None))
        self.checkbox_static.setText(QCoreApplication.translate("TensorRTWidget", u"static", None))
        self.label_12.setText(QCoreApplication.translate("TensorRTWidget", u"Shape", None))
        self.lineedit_shape.setText(QCoreApplication.translate("TensorRTWidget", u"4096 x 2160", None))
        self.label_resolution.setText(QCoreApplication.translate("TensorRTWidget", u"2160p (4K UHDTV)", None))
    # retranslateUi

