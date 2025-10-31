import logging
import os
import sys

from hutils import lightcyan, green, yellow, red, white

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
        # Use relative path from current working directory
        try:
            rel_path = os.path.relpath(record.pathname)
        except ValueError:
            # Fallback to basename if relpath fails (e.g., different drives on Windows)
            rel_path = os.path.basename(record.pathname)

        link = f"{rel_path}:{record.lineno}"
        return color_fn(f"{msg}  ({link})")

# logging.disable(logging.CRITICAL)


alog: logging.Logger = logging.getLogger("heron")

handler = logging.StreamHandler(sys.stdout)
formatter = ColorFormatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
alog.addHandler(handler)
alog.setLevel(logging.DEBUG)
