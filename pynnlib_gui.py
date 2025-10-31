from argparse import ArgumentParser
import logging
import os
import signal
import sys

from PySide6.QtWidgets import QApplication
from backend.controller import Controller


if sys.platform == "win32":
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "pynnlib.gui"
    )


def main():
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--dev",
        "-dev",
        action="store_true",
        required=False,
        help="Unlock all for dev"
    )

    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="",
        required=False,
        help="Load this model"
    )

    arguments = parser.parse_args()

    # FileOutputHandler = logging.FileHandler('l



    application = QApplication(sys.argv)
    QApplication.setStyle("Fusion")
    controller = Controller(model_fp=arguments.model, dev=arguments.dev)

    from ui.main_window import MainWindow
    main_window = MainWindow(controller=controller)
    controller.set_view(main_window)
    main_window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()

