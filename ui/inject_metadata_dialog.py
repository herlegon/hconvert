from hutils import get_extension
import os
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
)


def inject_metadata_dialog(parent: QWidget, model_fp: str) -> str | None:
    """
    Opens a "Save As" dialog for '.pth' or '.onnx' files depending on initial_filepath.
    Prompts for overwrite if file exists.

    Returns the selected file path as a string, or None if cancelled.
    """
    suffix = get_extension(model_fp)

    if suffix == ".pth":
        filter_str = "PyTorch model (*.pth)"
        default_suffix = "pth"

    elif suffix == ".onnx":
        filter_str = "ONNX model (*.onnx)"
        default_suffix = "onnx"

    else:
        filter_str = "All Files (*)"
        default_suffix = ""

    dialog = QFileDialog(parent, "Save As", model_fp)
    dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dialog.setNameFilter(filter_str)
    if default_suffix:
        dialog.setDefaultSuffix(default_suffix)

    if dialog.exec():
        selected_files = dialog.selectedFiles()
        if not selected_files:
            return None
        selected_path = selected_files[0]
        directory = os.path.dirname(selected_path)
        filename = os.path.basename(selected_path)

        # Check if directory exists and is writable
        if not os.path.exists(directory):
            QMessageBox.warning(parent, "Directory Error",
                                f"The directory '{directory}' does not exist.")
            return None
        if not os.access(directory, os.W_OK):
            QMessageBox.warning(parent, "Permission Error",
                                f"The directory '{directory}' is not writable.")
            return None

        if os.path.exists(selected_path):
            if not os.access(selected_path, os.W_OK):
                QMessageBox.warning(parent, "Permission Error",
                                    f"The file '{filename}' is not writable.")
                return None

            reply = QMessageBox.question(
                parent,
                "Overwrite File?",
                f"The file '{filename}' already exists.\nDo you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return None

        return selected_path

    return None
