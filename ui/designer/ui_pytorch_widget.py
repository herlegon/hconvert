# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_pytorch_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_PyTorchWidget(object):
    def setupUi(self, PyTorchWidget):
        if not PyTorchWidget.objectName():
            PyTorchWidget.setObjectName(u"PyTorchWidget")
        PyTorchWidget.resize(381, 183)
        PyTorchWidget.setMaximumSize(QSize(16777210, 16777215))
        self.verticalLayout = QVBoxLayout(PyTorchWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupbox_pytorch_model = QGroupBox(PyTorchWidget)
        self.groupbox_pytorch_model.setObjectName(u"groupbox_pytorch_model")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupbox_pytorch_model.sizePolicy().hasHeightForWidth())
        self.groupbox_pytorch_model.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.groupbox_pytorch_model)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_5 = QLabel(self.groupbox_pytorch_model)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineedit_arch_name = QLineEdit(self.groupbox_pytorch_model)
        self.lineedit_arch_name.setObjectName(u"lineedit_arch_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineedit_arch_name.sizePolicy().hasHeightForWidth())
        self.lineedit_arch_name.setSizePolicy(sizePolicy1)
        self.lineedit_arch_name.setMinimumSize(QSize(200, 0))
        self.lineedit_arch_name.setMaximumSize(QSize(200, 16777215))
        self.lineedit_arch_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineedit_arch_name.setReadOnly(True)

        self.horizontalLayout.addWidget(self.lineedit_arch_name)

        self.pushbutton_link = QPushButton(self.groupbox_pytorch_model)
        self.pushbutton_link.setObjectName(u"pushbutton_link")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushbutton_link.sizePolicy().hasHeightForWidth())
        self.pushbutton_link.setSizePolicy(sizePolicy2)
        self.pushbutton_link.setMaximumSize(QSize(24, 24))
        self.pushbutton_link.setFlat(True)

        self.horizontalLayout.addWidget(self.pushbutton_link)

        self.horizontalSpacer_5 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.label_11 = QLabel(self.groupbox_pytorch_model)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.lineedit_scale = QLineEdit(self.groupbox_pytorch_model)
        self.lineedit_scale.setObjectName(u"lineedit_scale")
        sizePolicy1.setHeightForWidth(self.lineedit_scale.sizePolicy().hasHeightForWidth())
        self.lineedit_scale.setSizePolicy(sizePolicy1)
        self.lineedit_scale.setMaximumSize(QSize(45, 16777215))
        self.lineedit_scale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineedit_scale.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineedit_scale)

        self.label_6 = QLabel(self.groupbox_pytorch_model)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.lineedit_type = QLineEdit(self.groupbox_pytorch_model)
        self.lineedit_type.setObjectName(u"lineedit_type")
        sizePolicy1.setHeightForWidth(self.lineedit_type.sizePolicy().hasHeightForWidth())
        self.lineedit_type.setSizePolicy(sizePolicy1)
        self.lineedit_type.setMaximumSize(QSize(60, 16777215))
        self.lineedit_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineedit_type.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineedit_type)

        self.label_20 = QLabel(self.groupbox_pytorch_model)
        self.label_20.setObjectName(u"label_20")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_20)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(-1, -1, 0, -1)
        self.label_25 = QLabel(self.groupbox_pytorch_model)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_22.addWidget(self.label_25)

        self.lineedit_size_constraints_min = QLineEdit(self.groupbox_pytorch_model)
        self.lineedit_size_constraints_min.setObjectName(u"lineedit_size_constraints_min")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineedit_size_constraints_min.sizePolicy().hasHeightForWidth())
        self.lineedit_size_constraints_min.setSizePolicy(sizePolicy3)
        self.lineedit_size_constraints_min.setMaximumSize(QSize(60, 16777215))
        self.lineedit_size_constraints_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineedit_size_constraints_min.setReadOnly(True)

        self.horizontalLayout_22.addWidget(self.lineedit_size_constraints_min)

        self.label_24 = QLabel(self.groupbox_pytorch_model)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_22.addWidget(self.label_24)

        self.lineedit_size_constraints_modulo = QLineEdit(self.groupbox_pytorch_model)
        self.lineedit_size_constraints_modulo.setObjectName(u"lineedit_size_constraints_modulo")
        sizePolicy3.setHeightForWidth(self.lineedit_size_constraints_modulo.sizePolicy().hasHeightForWidth())
        self.lineedit_size_constraints_modulo.setSizePolicy(sizePolicy3)
        self.lineedit_size_constraints_modulo.setMaximumSize(QSize(40, 16777215))
        self.lineedit_size_constraints_modulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineedit_size_constraints_modulo.setReadOnly(True)

        self.horizontalLayout_22.addWidget(self.lineedit_size_constraints_modulo)

        self.horizontalSpacer_6 = QSpacerItem(0, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_6)


        self.formLayout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_22)


        self.verticalLayout_2.addLayout(self.formLayout)


        self.verticalLayout.addWidget(self.groupbox_pytorch_model)


        self.retranslateUi(PyTorchWidget)

        QMetaObject.connectSlotsByName(PyTorchWidget)
    # setupUi

    def retranslateUi(self, PyTorchWidget):
        PyTorchWidget.setWindowTitle(QCoreApplication.translate("PyTorchWidget", u"Form", None))
        self.groupbox_pytorch_model.setTitle(QCoreApplication.translate("PyTorchWidget", u"PyTorch / Model", None))
        self.label_5.setText(QCoreApplication.translate("PyTorchWidget", u"Arch. name", None))
        self.lineedit_arch_name.setText(QCoreApplication.translate("PyTorchWidget", u"DAT-2", None))
        self.pushbutton_link.setText(QCoreApplication.translate("PyTorchWidget", u"link", None))
        self.label_11.setText(QCoreApplication.translate("PyTorchWidget", u"Scale", None))
        self.lineedit_scale.setText(QCoreApplication.translate("PyTorchWidget", u"4", None))
        self.label_6.setText(QCoreApplication.translate("PyTorchWidget", u"Type", None))
        self.lineedit_type.setText(QCoreApplication.translate("PyTorchWidget", u"SISR", None))
        self.label_20.setText(QCoreApplication.translate("PyTorchWidget", u"Size constraints:", None))
        self.label_25.setText(QCoreApplication.translate("PyTorchWidget", u"min:", None))
        self.lineedit_size_constraints_min.setText(QCoreApplication.translate("PyTorchWidget", u"64x64", None))
        self.label_24.setText(QCoreApplication.translate("PyTorchWidget", u"multiple:", None))
        self.lineedit_size_constraints_modulo.setText(QCoreApplication.translate("PyTorchWidget", u"64", None))
    # retranslateUi

