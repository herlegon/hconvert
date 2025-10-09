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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QHBoxLayout, QLabel, QLayout, QMainWindow,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from ui.metadata_widget import MetadataWidget
from ui.model_browser_widget import ModelBrowserWidget
from ui.onnx_conversion_widget import OnnxConversionWidget
from ui.onnx_widget import OnnxWidget
from ui.pytorch_widget import PyTorchWidget
from ui.tensorrt_conversion_widget import TensorRTConversionWidget
from ui.tensorrt_widget import TensorRTWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(561, 314)
        MainWindow.setMaximumSize(QSize(16777213, 960))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_6 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(12, 12, 12, 12)
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label_4.setFont(font)

        self.verticalLayout_6.addWidget(self.label_4)

        self.layout_model_selection = QHBoxLayout()
        self.layout_model_selection.setObjectName(u"layout_model_selection")
        self.layout_model_selection.setContentsMargins(12, -1, -1, -1)
        self.widget_model_browser = ModelBrowserWidget(self.centralwidget)
        self.widget_model_browser.setObjectName(u"widget_model_browser")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_model_browser.sizePolicy().hasHeightForWidth())
        self.widget_model_browser.setSizePolicy(sizePolicy)
        self.widget_model_browser.setMinimumSize(QSize(500, 0))

        self.layout_model_selection.addWidget(self.widget_model_browser)


        self.verticalLayout_6.addLayout(self.layout_model_selection)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, 20, -1)
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.widget_pytorch_model = PyTorchWidget(self.centralwidget)
        self.widget_pytorch_model.setObjectName(u"widget_pytorch_model")
        sizePolicy.setHeightForWidth(self.widget_pytorch_model.sizePolicy().hasHeightForWidth())
        self.widget_pytorch_model.setSizePolicy(sizePolicy)

        self.verticalLayout_5.addWidget(self.widget_pytorch_model, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.widget_onnx_model = OnnxWidget(self.centralwidget)
        self.widget_onnx_model.setObjectName(u"widget_onnx_model")

        self.verticalLayout_5.addWidget(self.widget_onnx_model, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.widget_tensorrt_model = TensorRTWidget(self.centralwidget)
        self.widget_tensorrt_model.setObjectName(u"widget_tensorrt_model")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_tensorrt_model.sizePolicy().hasHeightForWidth())
        self.widget_tensorrt_model.setSizePolicy(sizePolicy1)

        self.verticalLayout_5.addWidget(self.widget_tensorrt_model, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, -1, -1, 0)
        self.widget_metadata = MetadataWidget(self.centralwidget)
        self.widget_metadata.setObjectName(u"widget_metadata")

        self.verticalLayout_4.addWidget(self.widget_metadata, 0, Qt.AlignmentFlag.AlignTop)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)
        self.label_3.setFont(font)

        self.verticalLayout_4.addWidget(self.label_3, 0, Qt.AlignmentFlag.AlignTop)

        self.layout_output_filepath = QHBoxLayout()
        self.layout_output_filepath.setObjectName(u"layout_output_filepath")
        self.layout_output_filepath.setContentsMargins(12, 0, 0, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_out_type = QLabel(self.centralwidget)
        self.label_out_type.setObjectName(u"label_out_type")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_out_type.sizePolicy().hasHeightForWidth())
        self.label_out_type.setSizePolicy(sizePolicy3)
        self.label_out_type.setMinimumSize(QSize(65, 0))

        self.horizontalLayout_2.addWidget(self.label_out_type)

        self.combobox_out_name = QComboBox(self.centralwidget)
        self.combobox_out_name.setObjectName(u"combobox_out_name")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.combobox_out_name.sizePolicy().hasHeightForWidth())
        self.combobox_out_name.setSizePolicy(sizePolicy4)
        self.combobox_out_name.setMinimumSize(QSize(300, 0))
        self.combobox_out_name.setAcceptDrops(True)
        self.combobox_out_name.setEditable(True)

        self.horizontalLayout_2.addWidget(self.combobox_out_name)

        self.button_out_browse = QPushButton(self.centralwidget)
        self.button_out_browse.setObjectName(u"button_out_browse")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.button_out_browse.sizePolicy().hasHeightForWidth())
        self.button_out_browse.setSizePolicy(sizePolicy5)
        self.button_out_browse.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout_2.addWidget(self.button_out_browse)


        self.layout_output_filepath.addLayout(self.horizontalLayout_2)

        self.checkbox_out_autonaming = QCheckBox(self.centralwidget)
        self.checkbox_out_autonaming.setObjectName(u"checkbox_out_autonaming")
        self.checkbox_out_autonaming.setChecked(True)

        self.layout_output_filepath.addWidget(self.checkbox_out_autonaming)


        self.verticalLayout_4.addLayout(self.layout_output_filepath)

        self.layout_conversion = QVBoxLayout()
        self.layout_conversion.setSpacing(0)
        self.layout_conversion.setObjectName(u"layout_conversion")
        self.layout_conversion.setContentsMargins(12, 0, -1, 0)
        self.checkbox_safetensor = QCheckBox(self.centralwidget)
        self.checkbox_safetensor.setObjectName(u"checkbox_safetensor")
        self.checkbox_safetensor.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.checkbox_safetensor.setAutoExclusive(False)

        self.layout_conversion.addWidget(self.checkbox_safetensor)

        self.groupBox_onnx = QGroupBox(self.centralwidget)
        self.groupBox_onnx.setObjectName(u"groupBox_onnx")
        self.groupBox_onnx.setCheckable(True)
        self.groupBox_onnx.setChecked(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_onnx)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 9, 9, 9)
        self.widget_onnx_conversion = OnnxConversionWidget(self.groupBox_onnx)
        self.widget_onnx_conversion.setObjectName(u"widget_onnx_conversion")

        self.verticalLayout_2.addWidget(self.widget_onnx_conversion)


        self.layout_conversion.addWidget(self.groupBox_onnx)

        self.groupBox_tensorrt = QGroupBox(self.centralwidget)
        self.groupBox_tensorrt.setObjectName(u"groupBox_tensorrt")
        self.groupBox_tensorrt.setCheckable(True)
        self.groupBox_tensorrt.setChecked(False)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_tensorrt)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(9, 9, 9, 9)
        self.widget_tensorrt_conversion = TensorRTConversionWidget(self.groupBox_tensorrt)
        self.widget_tensorrt_conversion.setObjectName(u"widget_tensorrt_conversion")

        self.verticalLayout_3.addWidget(self.widget_tensorrt_conversion)


        self.layout_conversion.addWidget(self.groupBox_tensorrt, 0, Qt.AlignmentFlag.AlignTop)


        self.verticalLayout_4.addLayout(self.layout_conversion)

        self.verticalLayout_4.setStretch(1, 1)
        self.verticalLayout_4.setStretch(2, 2)
        self.verticalLayout_4.setStretch(3, 3)

        self.horizontalLayout.addLayout(self.verticalLayout_4)


        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.layout_control = QHBoxLayout()
        self.layout_control.setObjectName(u"layout_control")
        self.layout_control.setContentsMargins(0, -1, -1, -1)
        self.button_convert = QPushButton(self.centralwidget)
        self.button_convert.setObjectName(u"button_convert")

        self.layout_control.addWidget(self.button_convert)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)
        self.progressBar.setTextVisible(False)

        self.layout_control.addWidget(self.progressBar)


        self.verticalLayout_6.addLayout(self.layout_control)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Model conversion", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Conversion", None))
        self.label_out_type.setText(QCoreApplication.translate("MainWindow", u"Save as", None))
        self.button_out_browse.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.checkbox_out_autonaming.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.checkbox_safetensor.setText(QCoreApplication.translate("MainWindow", u"SafeTensor", None))
        self.groupBox_onnx.setTitle(QCoreApplication.translate("MainWindow", u"Onnx", None))
        self.groupBox_tensorrt.setTitle(QCoreApplication.translate("MainWindow", u"TensorRT", None))
        self.button_convert.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.progressBar.setFormat("")
    # retranslateUi

