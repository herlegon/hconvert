import logging
import os
import sys
from typing import Optional

from hytils import darkgrey, green, yellow, red, white


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: white,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: red,
    }

    def format(self, record: logging.LogRecord) -> str:
        color_fn = self.COLORS.get(record.levelno, lambda x: x)
        msg = super().format(record)

        # Use relative path for readability
        try:
            rel_path = os.path.relpath(record.pathname)
        except ValueError:
            rel_path = os.path.basename(record.pathname)

        filename = darkgrey(os.path.basename(record.pathname))
        link = f"{rel_path}:{record.lineno}"

        formatted = f"[{record.levelname}]  {filename}: {record.getMessage()}  ({link})"
        return color_fn(formatted)


class SimpleFormatter(logging.Formatter):
    """Non-colored formatter (for file or GUI)."""
    def format(self, record: logging.LogRecord) -> str:
        try:
            rel_path = os.path.relpath(record.pathname)
        except ValueError:
            rel_path = os.path.basename(record.pathname)
        link = f"{rel_path}:{record.lineno}"
        return f"[{record.levelname}]  {os.path.basename(record.pathname)}: {record.getMessage()}  ({link})"


def setup_alog(
    log_file: Optional[str] = None,
    to_stdout: bool = True,
    to_gui: Optional[logging.Handler] = None,
    stdout_formatter: Optional[logging.Formatter] = None,
    gui_formatter: Optional[logging.Formatter] = None,
    file_formatter: Optional[logging.Formatter] = None,
):
    """Reconfigure the global logger."""
    logger = logging.getLogger("herlegon_convert")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # Console handler
    if to_stdout:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(stdout_formatter or ColorFormatter())
        logger.addHandler(stream_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setFormatter(file_formatter or SimpleFormatter())
        logger.addHandler(file_handler)

    # GUI handler
    if to_gui:
        to_gui.setFormatter(gui_formatter or SimpleFormatter())
        logger.addHandler(to_gui)

    return logger


# Default initialization (basic mode)
alog: logging.Logger = setup_alog(to_stdout=True)


# logging.disable(logging.CRITICAL)

# alog: logging.Logger = logging.getLogger("herlegon_convert")

# handler = logging.StreamHandler(sys.stdout)
# formatter = ColorFormatter()
# handler.setFormatter(formatter)
# alog.addHandler(handler)
# alog.setLevel(logging.DEBUG)
