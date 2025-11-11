from argparse import ArgumentParser
import signal
import sys

from PySide6.QtWidgets import QApplication


if sys.platform == "win32":
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "herlegon_convert.gui"
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

    args = parser.parse_args()

    # FileOutputHandler = logging.FileHandler('l

    application = QApplication(sys.argv)
    QApplication.setStyle("Fusion")

    from .main_window import MainWindow
    main_window = MainWindow(args=args)
    main_window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()

