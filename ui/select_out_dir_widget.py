from copy import deepcopy
import os
from backend.path_utils import absolute_path, is_access_granted, parent_directory, path_split
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
    QWidget,
    QComboBox,
    QFileDialog,
    QMessageBox,
)
from .designer.ui_select_out_dir_widget import Ui_SelectOutDirWidget


class SelectOutDirWidget(QWidget, Ui_SelectOutDirWidget):
    signal_get_out_fp = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.in_model_dir: str = ""
        self.out_directory: str = ""

        # Save the previous directory
        self.previous_directory: str = ""

        self.lineEdit_out_dir.setAcceptDrops(False)
        self.lineEdit_out_dir.clear()

        self.button_out_dir_browse.released.connect(self.event_select_output_folder)
        self.button_input_folder.released.connect(self.event_use_in_model_dir)


    def clear(self) -> None:
        self.lineEdit_out_dir.clear()


    def block_signals(self, enabled: bool) -> None:
        self.button_input_folder.blockSignals(enabled)
        self.button_out_dir_browse.blockSignals(enabled)


    def refresh_model_info(self, model: NnModel) -> None:
        if model is None or model.framework.type == NnFrameworkType.TENSORRT:
            self.setEnabled(False)

        self.setEnabled(True)

        self.in_model_fp = model.filepath
        lineedit_text: str = self.lineEdit_out_dir.text()

        self.block_signals(True)
        if lineedit_text and not self.button_input_folder.isChecked():
            # Not the directory of the model and has already been set
            #   use it if exists. Otherwise, input dir
            if not os.path.exists(absolute_path(self.lineEdit_out_dir.text())):
                self.button_input_folder.setChecked(True)
                self.event_use_in_model_dir()

        else:
            # The selected input directory is the same as the model dir.
            # or use the model directory otherwise
            self.button_input_folder.setChecked(True)
            self.event_use_in_model_dir()

        self.block_signals(False)


    def event_use_in_model_dir(self) -> None:
        if self.button_input_folder.isChecked():
            # Initial: use the initial output naming
            directory, _, _ = path_split(absolute_path(self.in_model_fp))
            if not directory:
                directory = os.path.abspath(__file__)
            self.lineEdit_out_dir.setText(directory)
            self.in_model_dir = directory


    def event_select_output_folder(self) -> None:
        # Initial output directory
        lineedit_text: str = self.lineEdit_out_dir.text()
        output_dir: str = absolute_path("~")
        if lineedit_text:
            initial_out_dir: str = absolute_path(lineedit_text)
            if os.path.exists(initial_out_dir):
                output_dir = initial_out_dir

        # Default is initial directory
        selected_dir: str = output_dir

        # Loop until a valid directory is found or cancelled
        while True:
            selected = QFileDialog.getExistingDirectory(
                None,
                "Select Output Folder",
                output_dir,
                QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
            )
            print(selected)

            # Cancelled or not exists
            if not selected or not os.path.exists(selected):
                selected_dir = output_dir
                break

            # Check if the folder is writable
            if is_access_granted(selected, 'w'):
                print("granted")
                selected_dir = selected
                break

            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Permission Error")
                msg_box.setText("The selected folder is not writable.")
                msg_box.setInformativeText("Please select a different folder.")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()

        self.button_input_folder.setChecked(bool(selected_dir == self.in_model_dir))
        self.lineEdit_out_dir.setText(selected_dir)

