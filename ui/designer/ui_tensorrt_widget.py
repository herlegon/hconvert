# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_tensorrt_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_TensorRTWidget(object):
    def setupUi(self, TensorRTWidget):
        if not TensorRTWidget.objectName():
            TensorRTWidget.setObjectName(u"TensorRTWidget")
        TensorRTWidget.resize(277, 111)
        self.verticalLayout = QVBoxLayout(TensorRTWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupbox_tensorrt_model = QGroupBox(TensorRTWidget)
        self.groupbox_tensorrt_model.setObjectName(u"groupbox_tensorrt_model")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupbox_tensorrt_model.sizePolicy().hasHeightForWidth())
        self.groupbox_tensorrt_model.setSizePolicy(sizePolicy)
        self.verticalLayout_6 = QVBoxLayout(self.groupbox_tensorrt_model)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_30 = QLabel(self.groupbox_tensorrt_model)
        self.label_30.setObjectName(u"label_30")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_30)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.checkbox_dynamic = QCheckBox(self.groupbox_tensorrt_model)
        self.checkbox_dynamic.setObjectName(u"checkbox_dynamic")
        self.checkbox_dynamic.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.checkbox_dynamic.sizePolicy().hasHeightForWidth())
        self.checkbox_dynamic.setSizePolicy(sizePolicy1)
        self.checkbox_dynamic.setChecked(True)

        self.horizontalLayout_21.addWidget(self.checkbox_dynamic)

        self.checkbox_static = QCheckBox(self.groupbox_tensorrt_model)
        self.checkbox_static.setObjectName(u"checkbox_static")
        self.checkbox_static.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.checkbox_static.sizePolicy().hasHeightForWidth())
        self.checkbox_static.setSizePolicy(sizePolicy1)

        self.horizontalLayout_21.addWidget(self.checkbox_static)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_21)

        self.label_12 = QLabel(self.groupbox_tensorrt_model)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.lineedit_shape = QLineEdit(self.groupbox_tensorrt_model)
        self.lineedit_shape.setObjectName(u"lineedit_shape")
        sizePolicy1.setHeightForWidth(self.lineedit_shape.sizePolicy().hasHeightForWidth())
        self.lineedit_shape.setSizePolicy(sizePolicy1)
        self.lineedit_shape.setMaximumSize(QSize(100, 16777215))
        self.lineedit_shape.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineedit_shape)


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
        self.checkbox_static.setText(QCoreApplication.translate("TensorRTWidget", u"fixed", None))
        self.label_12.setText(QCoreApplication.translate("TensorRTWidget", u"Shape", None))
        self.lineedit_shape.setText(QCoreApplication.translate("TensorRTWidget", u"128x450", None))
    # retranslateUi

