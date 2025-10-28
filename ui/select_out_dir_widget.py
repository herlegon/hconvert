from copy import deepcopy
import os
from pathlib import (
    Path,
)
from typing import Type
from hutils import (
    absolute_path,
    is_access_granted,
    path_split,
)
from hwidgets import HStyle
from pynnlib import (
    NnModel,
    NnFrameworkType,
)

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
)
from .designer.ui_select_out_dir_widget import Ui_SelectOutDirWidget



class SelectOutDirWidget(QWidget, Ui_SelectOutDirWidget):
    signal_get_out_fp = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        hrl_style = HStyle()
        self.setupUi(self, hrl_style)

        self.in_model_dir: str = ""
        self.out_directory: str = ""
        self.max_items: int = 10

        # Save the previous directory
        self.previous_directory: str = ""

        self.comboBox_out_dir.setAcceptDrops(False)
        self.comboBox_out_dir.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.comboBox_out_dir.lineEdit().setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.comboBox_out_dir.clear()

        self.button_out_dir_browse.released.connect(self.event_select_dir_clicked)
        self.button_input_folder.released.connect(self.event_select_in_dir)


    def apply_user_settings(self, prefs: dict) -> None:
        history = prefs.get('out_dir', [])
        if not history:
            return

        self.comboBox_out_dir.blockSignals(True)
        self.comboBox_out_dir.clear()
        self.comboBox_out_dir.lineEdit().clear()
        for f in history[:self.max_items]:
            if f and os.path.isdir(f):
                self.comboBox_out_dir.addItem(str(Path(f)))
        self.comboBox_out_dir.blockSignals(False)


    def get_user_settings(self) -> dict:
        return {
            'out_dir': list([
                Path(self.comboBox_out_dir.itemText(i)).as_posix()
                for i in range(self.comboBox_out_dir.count())
            ])
        }


    def editable_widgets(self) -> list[Type[QWidget]]:
        editable_widgets: list[Type[QWidget]] = [
            self.comboBox_out_dir,
            self.comboBox_out_dir.lineEdit(),
        ]
        return editable_widgets


    def block_signals(self, b: bool) -> None:
        self.button_input_folder.blockSignals(b)
        self.button_out_dir_browse.blockSignals(b)
        self.comboBox_out_dir.blockSignals(b)


    def clear(self) -> None:
        self.block_signals(True)
        self.comboBox_out_dir.clear()
        self.block_signals(False)


    def append_to_combobox(self, out_dir: str) -> None:
        # Do not append home
        if Path(out_dir) == Path.home():
            return

        self.block_signals(True)
        out_dir = str(Path(out_dir))
        index: int = self.comboBox_out_dir.findText(out_dir)
        if index >= 0:
            self.comboBox_out_dir.removeItem(index)
        self.comboBox_out_dir.insertItem(0, out_dir)
        self.comboBox_out_dir.setCurrentIndex(0)

        while self.comboBox_out_dir.count() > self.max_items:
            self.comboBox_out_dir.removeItem(self.comboBox_out_dir.count() - 1)
        self.block_signals(False)


    def refresh_model_info(self, model: NnModel) -> None:
        if model is None or model.framework.type == NnFrameworkType.TENSORRT:
            self.setEnabled(False)

        self.setEnabled(True)

        self.in_model_fp = model.filepath
        lineedit_text: str = self.comboBox_out_dir.lineEdit().text()

        self.block_signals(True)
        if lineedit_text and not self.button_input_folder.isChecked():
            # Not the directory of the model and has already been set
            #   use it if exists. Otherwise, input dir
            if not os.path.exists(absolute_path(lineedit_text)):
                self.button_input_folder.setChecked(True)
                self.event_select_in_dir()

        else:
            # The selected input directory is the same as the model dir.
            # or use the model directory otherwise
            self.button_input_folder.setChecked(True)
            self.event_select_in_dir()

        self.append_to_combobox(self.comboBox_out_dir.lineEdit().text())
        self.block_signals(False)


    def event_select_in_dir(self) -> None:
        if self.button_input_folder.isChecked():
            # Initial: use the initial output naming
            directory, _, _ = path_split(absolute_path(self.in_model_fp))
            if not directory:
                directory = os.path.abspath(__file__)
            self.comboBox_out_dir.lineEdit().setText(directory)
            self.in_model_dir = directory


    def conversion_ended(self) -> None:
        # Append the output directory if it wasn't an existing folder
        self.append_to_combobox(self.comboBox_out_dir.lineEdit().text())


    def event_select_dir_clicked(self) -> None:
        # Initial output directory
        lineedit_text: str = self.comboBox_out_dir.lineEdit().text()
        output_dir: str = absolute_path("~")
        if lineedit_text:
            initial_out_dir: str = absolute_path(lineedit_text)
            if os.path.isdir(initial_out_dir) and is_access_granted(initial_out_dir, 'w'):
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

            # Cancelled or not exists
            if not selected or not os.path.exists(selected):
                selected_dir = output_dir
                break

            # Check if the folder is writable
            if is_access_granted(selected, 'w'):
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
        self.comboBox_out_dir.lineEdit().setText(selected_dir)

        # Append to the combobox
        self.append_to_combobox(selected_dir)




    def out_dir(self) -> str:
        return self.comboBox_out_dir.lineEdit().text()
