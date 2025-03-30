# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QPlainTextEdit, QProgressBar, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(761, 731)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.combobox_filepath = QComboBox(self.centralwidget)
        self.combobox_filepath.setObjectName(u"combobox_filepath")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.combobox_filepath.sizePolicy().hasHeightForWidth())
        self.combobox_filepath.setSizePolicy(sizePolicy)
        self.combobox_filepath.setMinimumSize(QSize(300, 0))
        self.combobox_filepath.setAcceptDrops(True)
        self.combobox_filepath.setEditable(True)

        self.horizontalLayout.addWidget(self.combobox_filepath)

        self.button_browse = QPushButton(self.centralwidget)
        self.button_browse.setObjectName(u"button_browse")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.button_browse.sizePolicy().hasHeightForWidth())
        self.button_browse.setSizePolicy(sizePolicy1)
        self.button_browse.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout.addWidget(self.button_browse)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, -1, -1, 20)
        self.verticalFrame_2 = QFrame(self.centralwidget)
        self.verticalFrame_2.setObjectName(u"verticalFrame_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalFrame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.verticalFrame_2)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.pushButton_2 = QPushButton(self.verticalFrame_2)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_7.addWidget(self.pushButton_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_20 = QLabel(self.verticalFrame_2)
        self.label_20.setObjectName(u"label_20")

        self.horizontalLayout_6.addWidget(self.label_20)

        self.label_25 = QLabel(self.verticalFrame_2)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_6.addWidget(self.label_25)

        self.label_26 = QLabel(self.verticalFrame_2)
        self.label_26.setObjectName(u"label_26")

        self.horizontalLayout_6.addWidget(self.label_26)

        self.label_24 = QLabel(self.verticalFrame_2)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_6.addWidget(self.label_24)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.layout_model_type = QHBoxLayout()
        self.layout_model_type.setObjectName(u"layout_model_type")
        self.label_6 = QLabel(self.verticalFrame_2)
        self.label_6.setObjectName(u"label_6")

        self.layout_model_type.addWidget(self.label_6)

        self.label_27 = QLabel(self.verticalFrame_2)
        self.label_27.setObjectName(u"label_27")

        self.layout_model_type.addWidget(self.label_27)


        self.verticalLayout_2.addLayout(self.layout_model_type)


        self.horizontalLayout_8.addWidget(self.verticalFrame_2)

        self.verticalFrame_3 = QFrame(self.centralwidget)
        self.verticalFrame_3.setObjectName(u"verticalFrame_3")
        self.verticalLayout_3 = QVBoxLayout(self.verticalFrame_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_7 = QLabel(self.verticalFrame_3)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_3.addWidget(self.label_7)

        self.label_28 = QLabel(self.verticalFrame_3)
        self.label_28.setObjectName(u"label_28")

        self.verticalLayout_3.addWidget(self.label_28)

        self.label_11 = QLabel(self.verticalFrame_3)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_3.addWidget(self.label_11)

        self.label_12 = QLabel(self.verticalFrame_3)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_3.addWidget(self.label_12)


        self.horizontalLayout_8.addWidget(self.verticalFrame_3, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalFrame_4 = QFrame(self.centralwidget)
        self.verticalFrame_4.setObjectName(u"verticalFrame_4")
        self.verticalLayout_6 = QVBoxLayout(self.verticalFrame_4)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_19 = QLabel(self.verticalFrame_4)
        self.label_19.setObjectName(u"label_19")

        self.verticalLayout_6.addWidget(self.label_19)

        self.label_23 = QLabel(self.verticalFrame_4)
        self.label_23.setObjectName(u"label_23")

        self.verticalLayout_6.addWidget(self.label_23)

        self.label_21 = QLabel(self.verticalFrame_4)
        self.label_21.setObjectName(u"label_21")

        self.verticalLayout_6.addWidget(self.label_21)


        self.horizontalLayout_8.addWidget(self.verticalFrame_4, 0, Qt.AlignmentFlag.AlignTop)


        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupbox_onnx = QGroupBox(self.centralwidget)
        self.groupbox_onnx.setObjectName(u"groupbox_onnx")
        self.groupbox_onnx.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.groupbox_onnx)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_14 = QLabel(self.groupbox_onnx)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_13.addWidget(self.label_14)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_3)

        self.spinBox_3 = QSpinBox(self.groupbox_onnx)
        self.spinBox_3.setObjectName(u"spinBox_3")
        self.spinBox_3.setMinimum(15)
        self.spinBox_3.setMaximum(21)
        self.spinBox_3.setValue(20)

        self.horizontalLayout_13.addWidget(self.spinBox_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_15 = QLabel(self.groupbox_onnx)
        self.label_15.setObjectName(u"label_15")

        self.horizontalLayout_14.addWidget(self.label_15)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer)

        self.radioButton_5 = QRadioButton(self.groupbox_onnx)
        self.radioButton_5.setObjectName(u"radioButton_5")

        self.horizontalLayout_14.addWidget(self.radioButton_5)

        self.radioButton_6 = QRadioButton(self.groupbox_onnx)
        self.radioButton_6.setObjectName(u"radioButton_6")

        self.horizontalLayout_14.addWidget(self.radioButton_6)


        self.verticalLayout_4.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_22 = QLabel(self.groupbox_onnx)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_17.addWidget(self.label_22)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_2)

        self.checkBox_13 = QCheckBox(self.groupbox_onnx)
        self.checkBox_13.setObjectName(u"checkBox_13")
        self.checkBox_13.setEnabled(True)
        self.checkBox_13.setChecked(True)

        self.horizontalLayout_17.addWidget(self.checkBox_13)

        self.checkBox_14 = QCheckBox(self.groupbox_onnx)
        self.checkBox_14.setObjectName(u"checkBox_14")
        self.checkBox_14.setEnabled(True)

        self.horizontalLayout_17.addWidget(self.checkBox_14)


        self.verticalLayout_4.addLayout(self.horizontalLayout_17)


        self.horizontalLayout_4.addWidget(self.groupbox_onnx, 0, Qt.AlignmentFlag.AlignTop)

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


        self.horizontalLayout_4.addWidget(self.groupbox_tensorrt, 0, Qt.AlignmentFlag.AlignTop)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.combobox_filepath_2 = QComboBox(self.centralwidget)
        self.combobox_filepath_2.setObjectName(u"combobox_filepath_2")
        sizePolicy.setHeightForWidth(self.combobox_filepath_2.sizePolicy().hasHeightForWidth())
        self.combobox_filepath_2.setSizePolicy(sizePolicy)
        self.combobox_filepath_2.setMinimumSize(QSize(300, 0))
        self.combobox_filepath_2.setAcceptDrops(True)
        self.combobox_filepath_2.setEditable(True)

        self.horizontalLayout_2.addWidget(self.combobox_filepath_2)

        self.button_browse_2 = QPushButton(self.centralwidget)
        self.button_browse_2.setObjectName(u"button_browse_2")
        sizePolicy1.setHeightForWidth(self.button_browse_2.sizePolicy().hasHeightForWidth())
        self.button_browse_2.setSizePolicy(sizePolicy1)
        self.button_browse_2.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout_2.addWidget(self.button_browse_2)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        self.checkBox = QCheckBox(self.centralwidget)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_5.addWidget(self.pushButton)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)
        self.progressBar.setTextVisible(False)

        self.horizontalLayout_5.addWidget(self.progressBar)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.plainTextEdit = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayout.addWidget(self.plainTextEdit)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.button_browse.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Arch. name", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"link", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Size constraints", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"min", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"max", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"modulo", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Type", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"VSR/SISR/", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"ONNX", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"version", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"shape strategy:", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Precision", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"TensorRT", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Shape strategy:", None))
        self.groupbox_onnx.setTitle(QCoreApplication.translate("MainWindow", u"ONNX", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Version", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Precision", None))
        self.radioButton_5.setText(QCoreApplication.translate("MainWindow", u"fp32", None))
        self.radioButton_6.setText(QCoreApplication.translate("MainWindow", u"fp16", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Shape strategy", None))
        self.checkBox_13.setText(QCoreApplication.translate("MainWindow", u"dynamic", None))
        self.checkBox_14.setText(QCoreApplication.translate("MainWindow", u"static", None))
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

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Save as", None))
        self.button_browse_2.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.progressBar.setFormat("")
    # retranslateUi

