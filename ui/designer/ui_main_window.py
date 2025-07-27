# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QMainWindow, QPlainTextEdit, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

from ui.model_widget import ModelWidget
from ui.onnx_widget import OnnxWidget
from ui.tensorrt_conversion_widget import TensorRTConversionWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(500, 408)
        MainWindow.setMaximumSize(QSize(16777215, 960))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_model = ModelWidget(self.centralwidget)
        self.widget_model.setObjectName(u"widget_model")

        self.verticalLayout.addWidget(self.widget_model)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label_3.setFont(font)

        self.verticalLayout.addWidget(self.label_3)

        self.layout_conversion = QHBoxLayout()
        self.layout_conversion.setObjectName(u"layout_conversion")
        self.layout_conversion.setContentsMargins(12, -1, -1, -1)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkbox_safetensor = QCheckBox(self.centralwidget)
        self.checkbox_safetensor.setObjectName(u"checkbox_safetensor")

        self.verticalLayout_2.addWidget(self.checkbox_safetensor, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.widget_onnx_conversion = OnnxWidget(self.centralwidget)
        self.widget_onnx_conversion.setObjectName(u"widget_onnx_conversion")
        self.widget_onnx_conversion.setMinimumSize(QSize(20, 20))

        self.verticalLayout_2.addWidget(self.widget_onnx_conversion)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.layout_conversion.addLayout(self.verticalLayout_2)

        self.widget_tensorrt_conversion = TensorRTConversionWidget(self.centralwidget)
        self.widget_tensorrt_conversion.setObjectName(u"widget_tensorrt_conversion")

        self.layout_conversion.addWidget(self.widget_tensorrt_conversion)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.layout_conversion.addItem(self.horizontalSpacer_11)


        self.verticalLayout.addLayout(self.layout_conversion)

        self.layout_output_filepath = QHBoxLayout()
        self.layout_output_filepath.setObjectName(u"layout_output_filepath")
        self.layout_output_filepath.setContentsMargins(12, 3, 3, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_out_type = QLabel(self.centralwidget)
        self.label_out_type.setObjectName(u"label_out_type")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_out_type.sizePolicy().hasHeightForWidth())
        self.label_out_type.setSizePolicy(sizePolicy)
        self.label_out_type.setMinimumSize(QSize(65, 0))

        self.horizontalLayout_2.addWidget(self.label_out_type)

        self.combobox_out_name = QComboBox(self.centralwidget)
        self.combobox_out_name.setObjectName(u"combobox_out_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.combobox_out_name.sizePolicy().hasHeightForWidth())
        self.combobox_out_name.setSizePolicy(sizePolicy1)
        self.combobox_out_name.setMinimumSize(QSize(300, 0))
        self.combobox_out_name.setAcceptDrops(True)
        self.combobox_out_name.setEditable(True)

        self.horizontalLayout_2.addWidget(self.combobox_out_name)

        self.button_out_browse = QPushButton(self.centralwidget)
        self.button_out_browse.setObjectName(u"button_out_browse")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.button_out_browse.sizePolicy().hasHeightForWidth())
        self.button_out_browse.setSizePolicy(sizePolicy2)
        self.button_out_browse.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout_2.addWidget(self.button_out_browse)


        self.layout_output_filepath.addLayout(self.horizontalLayout_2)

        self.checkbox_out_autonaming = QCheckBox(self.centralwidget)
        self.checkbox_out_autonaming.setObjectName(u"checkbox_out_autonaming")
        self.checkbox_out_autonaming.setChecked(True)

        self.layout_output_filepath.addWidget(self.checkbox_out_autonaming)


        self.verticalLayout.addLayout(self.layout_output_filepath)

        self.layout_control = QHBoxLayout()
        self.layout_control.setObjectName(u"layout_control")
        self.layout_control.setContentsMargins(12, -1, -1, -1)
        self.button_convert = QPushButton(self.centralwidget)
        self.button_convert.setObjectName(u"button_convert")

        self.layout_control.addWidget(self.button_convert)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)
        self.progressBar.setTextVisible(False)

        self.layout_control.addWidget(self.progressBar)


        self.verticalLayout.addLayout(self.layout_control)

        self.textedit_log = QPlainTextEdit(self.centralwidget)
        self.textedit_log.setObjectName(u"textedit_log")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.textedit_log.sizePolicy().hasHeightForWidth())
        self.textedit_log.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setFamilies([u"Droid Sans Fallback"])
        self.textedit_log.setFont(font1)
        self.textedit_log.setReadOnly(True)

        self.verticalLayout.addWidget(self.textedit_log)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Model conversion", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Conversion", None))
        self.checkbox_safetensor.setText(QCoreApplication.translate("MainWindow", u"SafeTensor", None))
        self.label_out_type.setText(QCoreApplication.translate("MainWindow", u"Save as", None))
        self.button_out_browse.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.checkbox_out_autonaming.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.button_convert.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.progressBar.setFormat("")
    # retranslateUi

