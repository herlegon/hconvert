# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_model_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QVBoxLayout, QWidget)

class Ui_ModelWidget(object):
    def setupUi(self, ModelWidget):
        if not ModelWidget.objectName():
            ModelWidget.setObjectName(u"ModelWidget")
        ModelWidget.resize(531, 274)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ModelWidget.sizePolicy().hasHeightForWidth())
        ModelWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(ModelWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.retranslateUi(ModelWidget)

        QMetaObject.connectSlotsByName(ModelWidget)
    # setupUi

    def retranslateUi(self, ModelWidget):
        ModelWidget.setWindowTitle(QCoreApplication.translate("ModelWidget", u"Form", None))
    # retranslateUi

