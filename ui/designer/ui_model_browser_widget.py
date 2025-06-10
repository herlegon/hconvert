# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_model_browser_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QWidget)

class Ui_ModelBrowserWidget(object):
    def setupUi(self, ModelBrowserWidget):
        if not ModelBrowserWidget.objectName():
            ModelBrowserWidget.setObjectName(u"ModelBrowserWidget")
        ModelBrowserWidget.resize(392, 30)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ModelBrowserWidget.sizePolicy().hasHeightForWidth())
        ModelBrowserWidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(ModelBrowserWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.combobox_model_fp = QComboBox(ModelBrowserWidget)
        self.combobox_model_fp.setObjectName(u"combobox_model_fp")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.combobox_model_fp.sizePolicy().hasHeightForWidth())
        self.combobox_model_fp.setSizePolicy(sizePolicy1)
        self.combobox_model_fp.setMinimumSize(QSize(300, 0))
        self.combobox_model_fp.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.combobox_model_fp.setAcceptDrops(True)
        self.combobox_model_fp.setEditable(True)
        self.combobox_model_fp.setMaxCount(10)
        self.combobox_model_fp.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)

        self.horizontalLayout.addWidget(self.combobox_model_fp)

        self.button_browse = QPushButton(ModelBrowserWidget)
        self.button_browse.setObjectName(u"button_browse")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.button_browse.sizePolicy().hasHeightForWidth())
        self.button_browse.setSizePolicy(sizePolicy2)
        self.button_browse.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout.addWidget(self.button_browse)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)

        self.label = QLabel(ModelBrowserWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)


        self.retranslateUi(ModelBrowserWidget)

        QMetaObject.connectSlotsByName(ModelBrowserWidget)
    # setupUi

    def retranslateUi(self, ModelBrowserWidget):
        ModelBrowserWidget.setWindowTitle(QCoreApplication.translate("ModelBrowserWidget", u"Form", None))
        self.button_browse.setText(QCoreApplication.translate("ModelBrowserWidget", u"...", None))
        self.label.setText(QCoreApplication.translate("ModelBrowserWidget", u"Filepath", None))
    # retranslateUi

