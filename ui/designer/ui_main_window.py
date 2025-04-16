# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

from ui.model_widget import ModelWidget
from ui.onnx_widget import OnnxWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(500, 558)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = ModelWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")

        self.verticalLayout.addWidget(self.widget)

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
        self.widget_onnx_conversion = OnnxWidget(self.centralwidget)
        self.widget_onnx_conversion.setObjectName(u"widget_onnx_conversion")

        self.layout_conversion.addWidget(self.widget_onnx_conversion, 0, Qt.AlignmentFlag.AlignTop)

        self.groupbox_tensorrt = QGroupBox(self.centralwidget)
        self.groupbox_tensorrt.setObjectName(u"groupbox_tensorrt")
        self.groupbox_tensorrt.setCheckable(True)
        self.verticalLayout_5 = QVBoxLayout(self.groupbox_tensorrt)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_18 = QLabel(self.groupbox_tensorrt)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_11.addWidget(self.label_18)

        self.comboBox_7 = QComboBox(self.groupbox_tensorrt)
        self.comboBox_7.setObjectName(u"comboBox_7")

        self.horizontalLayout_11.addWidget(self.comboBox_7)


        self.verticalLayout_5.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_16 = QLabel(self.groupbox_tensorrt)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_15.addWidget(self.label_16)

        self.checkBox_8 = QCheckBox(self.groupbox_tensorrt)
        self.checkBox_8.setObjectName(u"checkBox_8")
        self.checkBox_8.setEnabled(False)
        self.checkBox_8.setChecked(True)

        self.horizontalLayout_15.addWidget(self.checkBox_8)

        self.checkBox_9 = QCheckBox(self.groupbox_tensorrt)
        self.checkBox_9.setObjectName(u"checkBox_9")
        self.checkBox_9.setEnabled(True)

        self.horizontalLayout_15.addWidget(self.checkBox_9)

        self.checkBox_10 = QCheckBox(self.groupbox_tensorrt)
        self.checkBox_10.setObjectName(u"checkBox_10")
        self.checkBox_10.setEnabled(True)

        self.horizontalLayout_15.addWidget(self.checkBox_10)


        self.verticalLayout_5.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_13 = QLabel(self.groupbox_tensorrt)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_10.addWidget(self.label_13)

        self.horizontalSpacer_14 = QSpacerItem(12, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_14)

        self.spinBox = QSpinBox(self.groupbox_tensorrt)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(5)
        self.spinBox.setValue(3)

        self.horizontalLayout_10.addWidget(self.spinBox)


        self.verticalLayout_5.addLayout(self.horizontalLayout_10)

        self.layout_shape_strategy = QVBoxLayout()
        self.layout_shape_strategy.setObjectName(u"layout_shape_strategy")
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_17 = QLabel(self.groupbox_tensorrt)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_16.addWidget(self.label_17)

        self.horizontalSpacer_13 = QSpacerItem(12, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_13)

        self.checkBox_11 = QCheckBox(self.groupbox_tensorrt)
        self.checkBox_11.setObjectName(u"checkBox_11")
        self.checkBox_11.setEnabled(True)
        self.checkBox_11.setChecked(True)

        self.horizontalLayout_16.addWidget(self.checkBox_11)

        self.checkBox_12 = QCheckBox(self.groupbox_tensorrt)
        self.checkBox_12.setObjectName(u"checkBox_12")
        self.checkBox_12.setEnabled(True)

        self.horizontalLayout_16.addWidget(self.checkBox_12)


        self.layout_shape_strategy.addLayout(self.horizontalLayout_16)

        self.layout_min = QHBoxLayout()
        self.layout_min.setObjectName(u"layout_min")
        self.layout_min.setContentsMargins(9, -1, -1, -1)
        self.label_8 = QLabel(self.groupbox_tensorrt)
        self.label_8.setObjectName(u"label_8")

        self.layout_min.addWidget(self.label_8)

        self.comboBox = QComboBox(self.groupbox_tensorrt)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.layout_min.addWidget(self.comboBox)

        self.comboBox_4 = QComboBox(self.groupbox_tensorrt)
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setEditable(True)

        self.layout_min.addWidget(self.comboBox_4)


        self.layout_shape_strategy.addLayout(self.layout_min)

        self.layout_opt = QHBoxLayout()
        self.layout_opt.setObjectName(u"layout_opt")
        self.layout_opt.setContentsMargins(9, -1, -1, -1)
        self.label_9 = QLabel(self.groupbox_tensorrt)
        self.label_9.setObjectName(u"label_9")

        self.layout_opt.addWidget(self.label_9)

        self.comboBox_2 = QComboBox(self.groupbox_tensorrt)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.layout_opt.addWidget(self.comboBox_2)

        self.comboBox_5 = QComboBox(self.groupbox_tensorrt)
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.setObjectName(u"comboBox_5")
        self.comboBox_5.setEditable(True)

        self.layout_opt.addWidget(self.comboBox_5)


        self.layout_shape_strategy.addLayout(self.layout_opt)

        self.layout_max = QHBoxLayout()
        self.layout_max.setObjectName(u"layout_max")
        self.layout_max.setContentsMargins(9, -1, -1, -1)
        self.label_10 = QLabel(self.groupbox_tensorrt)
        self.label_10.setObjectName(u"label_10")

        self.layout_max.addWidget(self.label_10)

        self.comboBox_3 = QComboBox(self.groupbox_tensorrt)
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.layout_max.addWidget(self.comboBox_3)

        self.comboBox_6 = QComboBox(self.groupbox_tensorrt)
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.setObjectName(u"comboBox_6")
        self.comboBox_6.setEditable(True)

        self.layout_max.addWidget(self.comboBox_6)


        self.layout_shape_strategy.addLayout(self.layout_max)


        self.verticalLayout_5.addLayout(self.layout_shape_strategy)


        self.layout_conversion.addWidget(self.groupbox_tensorrt, 0, Qt.AlignmentFlag.AlignTop)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        self.plainTextEdit = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy3)
        self.plainTextEdit.setMaximumSize(QSize(16777215, 120))
        self.plainTextEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.plainTextEdit)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Model conversion", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Conversion", None))
        self.groupbox_tensorrt.setTitle(QCoreApplication.translate("MainWindow", u"Tensor RT", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"GPU", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Precision", None))
        self.checkBox_8.setText(QCoreApplication.translate("MainWindow", u"fp32", None))
        self.checkBox_9.setText(QCoreApplication.translate("MainWindow", u"fp16", None))
        self.checkBox_10.setText(QCoreApplication.translate("MainWindow", u"bf16", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Optimization level", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Shape strategy", None))
        self.checkBox_11.setText(QCoreApplication.translate("MainWindow", u"dynamic", None))
        self.checkBox_12.setText(QCoreApplication.translate("MainWindow", u"fixed", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Minimum", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"320p", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"480p", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"720p", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"1080p (2K)", None))
        self.comboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"4K", None))

        self.comboBox_4.setItemText(0, QCoreApplication.translate("MainWindow", u"8x8", None))
        self.comboBox_4.setItemText(1, QCoreApplication.translate("MainWindow", u"640x480", None))
        self.comboBox_4.setItemText(2, QCoreApplication.translate("MainWindow", u"705x480", None))
        self.comboBox_4.setItemText(3, QCoreApplication.translate("MainWindow", u"1440x1080", None))

        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Optimum", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("MainWindow", u"320p", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("MainWindow", u"480p", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("MainWindow", u"720p", None))
        self.comboBox_2.setItemText(3, QCoreApplication.translate("MainWindow", u"1080p (2K)", None))
        self.comboBox_2.setItemText(4, QCoreApplication.translate("MainWindow", u"4K", None))

        self.comboBox_5.setItemText(0, QCoreApplication.translate("MainWindow", u"8x8", None))
        self.comboBox_5.setItemText(1, QCoreApplication.translate("MainWindow", u"640x480", None))
        self.comboBox_5.setItemText(2, QCoreApplication.translate("MainWindow", u"705x480", None))
        self.comboBox_5.setItemText(3, QCoreApplication.translate("MainWindow", u"1440x1080", None))

        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Maximum", None))
        self.comboBox_3.setItemText(0, QCoreApplication.translate("MainWindow", u"320p", None))
        self.comboBox_3.setItemText(1, QCoreApplication.translate("MainWindow", u"480p", None))
        self.comboBox_3.setItemText(2, QCoreApplication.translate("MainWindow", u"720p", None))
        self.comboBox_3.setItemText(3, QCoreApplication.translate("MainWindow", u"1080p (2K)", None))
        self.comboBox_3.setItemText(4, QCoreApplication.translate("MainWindow", u"4K", None))

        self.comboBox_6.setItemText(0, QCoreApplication.translate("MainWindow", u"8x8", None))
        self.comboBox_6.setItemText(1, QCoreApplication.translate("MainWindow", u"640x480", None))
        self.comboBox_6.setItemText(2, QCoreApplication.translate("MainWindow", u"705x480", None))
        self.comboBox_6.setItemText(3, QCoreApplication.translate("MainWindow", u"1440x1080", None))

        self.label_out_type.setText(QCoreApplication.translate("MainWindow", u"Save as", None))
        self.button_out_browse.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.checkbox_out_autonaming.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.button_convert.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.progressBar.setFormat("")
    # retranslateUi

