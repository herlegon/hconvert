# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_metadata_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_MetadataWidget(object):
    def setupUi(self, MetadataWidget):
        if not MetadataWidget.objectName():
            MetadataWidget.setObjectName(u"MetadataWidget")
        MetadataWidget.resize(375, 326)
        self.verticalLayout = QVBoxLayout(MetadataWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(MetadataWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(6)
        self.formLayout.setContentsMargins(-1, 0, 0, 0)
        self.label_name = QLabel(self.groupBox)
        self.label_name.setObjectName(u"label_name")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_name)

        self.lineedit_name = QLineEdit(self.groupBox)
        self.lineedit_name.setObjectName(u"lineedit_name")
        self.lineedit_name.setMaxLength(64)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineedit_name)

        self.label_date = QLabel(self.groupBox)
        self.label_date.setObjectName(u"label_date")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_date)

        self.lineedit_date = QLineEdit(self.groupBox)
        self.lineedit_date.setObjectName(u"lineedit_date")
        self.lineedit_date.setMaxLength(10)
        self.lineedit_date.setFrame(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineedit_date)

        self.label_version = QLabel(self.groupBox)
        self.label_version.setObjectName(u"label_version")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_version)

        self.lineedit_version = QLineEdit(self.groupBox)
        self.lineedit_version.setObjectName(u"lineedit_version")
        self.lineedit_version.setMaxLength(64)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineedit_version)

        self.label_author = QLabel(self.groupBox)
        self.label_author.setObjectName(u"label_author")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_author)

        self.lineedit_author = QLineEdit(self.groupBox)
        self.lineedit_author.setObjectName(u"lineedit_author")
        self.lineedit_author.setMaxLength(64)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineedit_author)

        self.label_license = QLabel(self.groupBox)
        self.label_license.setObjectName(u"label_license")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_license)

        self.lineedit_license = QLineEdit(self.groupBox)
        self.lineedit_license.setObjectName(u"lineedit_license")
        self.lineedit_license.setMaxLength(64)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lineedit_license)

        self.label_comment = QLabel(self.groupBox)
        self.label_comment.setObjectName(u"label_comment")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_comment)

        self.plainTextEdit = QPlainTextEdit(self.groupBox)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setMinimumSize(QSize(0, 75))
        self.plainTextEdit.setMaximumSize(QSize(16777215, 75))
        self.plainTextEdit.setPlainText(u"")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.plainTextEdit)

        self.pushbutton_inject = QPushButton(self.groupBox)
        self.pushbutton_inject.setObjectName(u"pushbutton_inject")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.pushbutton_inject)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(MetadataWidget)

        QMetaObject.connectSlotsByName(MetadataWidget)
    # setupUi

    def retranslateUi(self, MetadataWidget):
        MetadataWidget.setWindowTitle(QCoreApplication.translate("MetadataWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("MetadataWidget", u"Metadata", None))
        self.label_name.setText(QCoreApplication.translate("MetadataWidget", u"Name", None))
        self.label_date.setText(QCoreApplication.translate("MetadataWidget", u"Date", None))
        self.label_version.setText(QCoreApplication.translate("MetadataWidget", u"Version", None))
        self.label_author.setText(QCoreApplication.translate("MetadataWidget", u"Author", None))
        self.label_license.setText(QCoreApplication.translate("MetadataWidget", u"License", None))
        self.label_comment.setText(QCoreApplication.translate("MetadataWidget", u"Comment", None))
        self.pushbutton_inject.setText(QCoreApplication.translate("MetadataWidget", u"Inject", None))
    # retranslateUi

