import re
from typing import Type
from hwidgets import HStyle

from PySide6.QtCore import (
    Qt,
    Signal,
    QObject,
)
from PySide6.QtGui import (
    QColor,
    QTextCursor,
    QTextCharFormat,
    QPalette,
    QFontDatabase,
)
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
    QSizePolicy,
)

from .designer.ui_log_widget import Ui_LogWidget
from .pynnlib_api import (
    NnModel,
)
import logging





class QtLogHandler(QObject, logging.Handler):
    # Emit both message and log level name
    new_log = Signal(str, int)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)


    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.new_log.emit(msg, record.levelno)



class LogWidget(QWidget, Ui_LogWidget):
    signal_inject_metadata = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        hrl_style = HStyle()
        self.setupUi(self, hrl_style)
        self._editable_widgets: list[type[QWidget]] = [
            *self.findChildren(QLineEdit),
            *self.findChildren(QTextEdit),
        ]

        # --- GUI Log Handler ---
        self.gui_handler = QtLogHandler()
        self.gui_handler.new_log.connect(self.append_colored_log)

        # --- Terminal-like style ---
        te = self.h_textedit_log
        te.setReadOnly(True)
        # te.setLineWrapMode(QPlainTextEdit.NoWrap)
        te.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # ✅ Optional: padding for nicer layout
        existing_style = self.h_textedit_log.styleSheet()
        terminal_styles = """
            QPlainTextEdit {
                font-family: "Consolas", "Courier New", "Monospace", ;
                font-size: 11pt;
                background-color: #1e1e1e;    /* dark terminal background */
                color: #d4d4d4;               /* default text color */
                padding: 4px;
                border: none;
            }
        """
        # Append terminal styles to the existing stylesheet
        self.h_textedit_log.setStyleSheet(existing_style + terminal_styles)

        self.h_textedit_log.setReadOnly(True)
        # self.h_textedit_log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NO_WRAP)
        self.h_textedit_log.setTextInteractionFlags(Qt.TextSelectableByMouse)

    _COLOR_MAP = {
        logging.DEBUG: QColor("#efefef"),   # gray
        logging.INFO: QColor("#55aa55"),    # green
        logging.WARNING: QColor("#ffaa00"), # orange
        logging.ERROR: QColor("#ff5555"),   # red
        logging.CRITICAL: QColor("#ff0000") # bright red
    }

    _ANSI_COLOR_MAP = {
        "30": QColor("#000000"),  # Black
        "31": QColor("#ff5555"),  # Red
        "32": QColor("#55ff55"),  # Green
        "33": QColor("#ffff55"),  # Yellow
        "34": QColor("#5555ff"),  # Blue
        "35": QColor("#ff55ff"),  # Magenta
        "36": QColor("#55ffff"),  # Cyan
        "37": QColor("#ffffff"),  # White
        "90": QColor("#888888"),  # Bright black (gray)
        "91": QColor("#ff7777"),
        "92": QColor("#77ff77"),
        "93": QColor("#ffff77"),
        "94": QColor("#7777ff"),
        "95": QColor("#ff77ff"),
        "96": QColor("#77ffff"),
        "97": QColor("#ffffff"),
    }

    _ansi_pattern = re.compile(r"\x1B\[(\d+)(;\d+)*m")

    _LEVEL_SYMBOLS = {
        logging.DEBUG: "•",
        logging.INFO: "→",
        logging.WARNING: "⚠",
        logging.ERROR: "✖",
        logging.CRITICAL: "‼",
    }

    _LEVEL_PREFIX = {
        logging.DEBUG: "[D]",
        5: "[V]",               # example VERBOSE custom level if used
        logging.INFO: "[I]",
        logging.WARNING: "[W]",
        logging.ERROR: "[E]",
        logging.CRITICAL: "[C]",
    }

    def append_colored_log(self, msg: str, levelno: int):
        """Append a log message with ANSI and log-level colors."""

        cursor = self.h_textedit_log.textCursor()
        cursor.movePosition(QTextCursor.End)

        default_color = self._COLOR_MAP.get(levelno, QColor(HStyle().text_color))

        fmt = QTextCharFormat()
        fmt.setForeground(default_color)

        if False:
            # Create format for the symbol
            # Insert symbol
            sym_fmt = QTextCharFormat()
            sym_fmt.setForeground(default_color)
            symbol = self._LEVEL_SYMBOLS.get(levelno, ">")
            cursor.insertText(symbol + " ", sym_fmt)

        else:
            prefix = self._LEVEL_PREFIX.get(levelno, "[?]") + " "

            # Insert the prefix
            prefix_fmt = QTextCharFormat()
            prefix_fmt.setForeground(default_color)
            cursor.insertText(prefix, prefix_fmt)

        # Split text by ANSI color codes
        parts = self._ansi_pattern.split(msg)
        # parts looks like ['[DEBUG] ', '93', None, '<<< parsed', '00', None, '']

        current_color = default_color
        for part in parts:
            if part is None:
                continue
            if part.isdigit() and part in self._ANSI_COLOR_MAP:
                current_color = self._ANSI_COLOR_MAP[part]
                fmt.setForeground(current_color)
            elif part == "00":
                # reset code
                fmt.setForeground(default_color)
                current_color = default_color
            else:
                cursor.insertText(part, fmt)

        cursor.insertText("\n", fmt)

        # Scroll to bottom
        self.h_textedit_log.moveCursor(QTextCursor.End)


    def block_signals(self, b: bool) -> None:
        pass


    def editable_widgets(self) -> list[Type[QWidget]]:
        return self._editable_widgets


    def clear(self) -> None:
        for w in self._editable_widgets:
            w.clear()


    def set_enabled(self, b: bool) -> None:
        pass


