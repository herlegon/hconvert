# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_model_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from ui.model_browser_widget import ModelBrowserWidget
from ui.onnx_widget import OnnxWidget
from ui.pytorch_widget import PyTorchWidget
from ui.tensorrt_widget import TensorRTWidget

class Ui_ModelWidget(object):
    def setupUi(self, ModelWidget):
        if not ModelWidget.objectName():
            ModelWidget.setObjectName(u"ModelWidget")
        ModelWidget.resize(531, 85)
        self.verticalLayout = QVBoxLayout(ModelWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(ModelWidget)
        self.label_4.setObjectName(u"label_4")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label_4.setFont(font)

        self.verticalLayout.addWidget(self.label_4)

        self.layout_model_selection = QHBoxLayout()
        self.layout_model_selection.setObjectName(u"layout_model_selection")
        self.layout_model_selection.setContentsMargins(12, -1, -1, -1)
        self.widget_model_browser = ModelBrowserWidget(ModelWidget)
        self.widget_model_browser.setObjectName(u"widget_model_browser")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_model_browser.sizePolicy().hasHeightForWidth())
        self.widget_model_browser.setSizePolicy(sizePolicy)
        self.widget_model_browser.setMinimumSize(QSize(500, 0))

        self.layout_model_selection.addWidget(self.widget_model_browser)


        self.verticalLayout.addLayout(self.layout_model_selection)

        self.layout_model = QHBoxLayout()
        self.layout_model.setObjectName(u"layout_model")
        self.layout_model.setContentsMargins(12, -1, -1, 12)
        self.widget_pytorch_model = PyTorchWidget(ModelWidget)
        self.widget_pytorch_model.setObjectName(u"widget_pytorch_model")

        self.layout_model.addWidget(self.widget_pytorch_model, 0, Qt.AlignmentFlag.AlignTop)

        self.widget_onnx_model = OnnxWidget(ModelWidget)
        self.widget_onnx_model.setObjectName(u"widget_onnx_model")

        self.layout_model.addWidget(self.widget_onnx_model, 0, Qt.AlignmentFlag.AlignTop)

        self.widget_tensorrt_model = TensorRTWidget(ModelWidget)
        self.widget_tensorrt_model.setObjectName(u"widget_tensorrt_model")

        self.layout_model.addWidget(self.widget_tensorrt_model, 0, Qt.AlignmentFlag.AlignTop)

        self.horizontalSpacer_10 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_model.addItem(self.horizontalSpacer_10)


        self.verticalLayout.addLayout(self.layout_model)


        self.retranslateUi(ModelWidget)

        QMetaObject.connectSlotsByName(ModelWidget)
    # setupUi

    def retranslateUi(self, ModelWidget):
        ModelWidget.setWindowTitle(QCoreApplication.translate("ModelWidget", u"Form", None))
        self.label_4.setText(QCoreApplication.translate("ModelWidget", u"Model", None))
    # retranslateUi

