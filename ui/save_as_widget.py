from copy import deepcopy
import os
from typing import Any
from backend.path_utils import absolute_path, path_split
from pynnlib import (
    NnModel,
    NnFrameworkType,
)
from PySide6.QtCore import (
    QEvent,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
    QComboBox,
)
from .designer.ui_save_as_widget import Ui_SaveAsWidget


class SaveAsWidget(QWidget, Ui_SaveAsWidget):
    signal_get_out_fp = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.in_model_fp: str = ""
        self.out_directory: str = ""

        # Save the previous directory
        self.previous_directory: str = ""

        self.lineEdit_out_dir.setAcceptDrops(False)
        self.lineEdit_out_dir.clear()
        self.lineEdit_out_dir.setReadOnly(True)

        self.button_out_dir_browse.released.connect(self.event_out_dir_picker)
        self.button_input_folder.released.connect(self.event_out_folder)


    def clear(self) -> None:
        self.lineEdit_out_dir.clear()


    def refresh_model_info(self, model: NnModel) -> None:
        if model is None or model.framework.type == NnFrameworkType.TENSORRT:
            self.setEnabled(False)

        self.setEnabled(True)
        self.in_model_fp = model.filepath

        # Initial: use the initial output naming
        directory, _, _ = path_split(absolute_path(self.in_model_fp))
        if not directory:
            directory = os.path.abspath(__file__)
        self.lineEdit_out_dir.setText(directory)


    def event_out_dir_picker(self):
        self.button_input_folder.setChecked(False)



    def event_out_folder(self) -> None:
        if self.button_input_folder.isChecked():
            # Initial: use the initial output naming
            directory, _, _ = path_split(absolute_path(self.in_model_fp))
            if not directory:
                directory = os.path.abspath(__file__)
            self.lineEdit_out_dir.setText(directory)

            self.lineEdit_out_dir.setReadOnly(True)


    def set_output_filename(self, filename: str) -> None:
        # self.out_model_fp = self.in_model_fp + filepath
        # if self.checkbox_same_as_input.isChecked():
        #     self.combobox_out_name.setCurrentText(self.out_model_fp)
        pass