from dataclasses import dataclass
import os
from pathlib import Path
import sys
# from PySide6.QtCore import (
# )
from PySide6.QtGui import (
    QFont,
    QPainter,
    QPixmap,
    QColor,
    QImage,
)
from PySide6.QtWidgets import (
    QStyle,
    QStyledItemDelegate,
)
from hutils import parent_directory, path_basename



TITLE_BAR_ICON_PATH = os.path.join(parent_directory(__file__), "icons")

def load_png_icon(filename: str, color: str) -> QPixmap:
    filepath = os.path.join(TITLE_BAR_ICON_PATH, filename)
    if not os.path.exists(filepath):
        raise ValueError(f"image {filepath} does not exist")
    qimage: QImage = QImage(filepath)
    color = QColor(color)

    painter: QPainter = QPainter()
    painter.begin(qimage)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.setBrush(color)
    painter.setPen(color)
    painter.drawRect(qimage.rect())
    painter.end()
    return QPixmap(qimage)





class BoldHoverDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Make font bold on hover or selection
        if option.state & QStyle.StateFlag.State_MouseOver or \
           option.state & QStyle.StateFlag.State_Selected:
            font = QFont(option.font)
            font.setBold(True)
            option.font = font
        super().paint(painter, option, index)



def load_qss(qss_fp: str, variant: str = "") -> str:
    variant = f"_{variant}" if variant else ""
    css_dir: Path = Path(__file__).parent / "css"

    common_fp = css_dir.joinpath(
        Path(f"{path_basename(qss_fp)}{variant}.qss")
    )
    with open(common_fp, 'r') as f:
        qss = f.read()

    platform_fp = css_dir.joinpath(
        Path(f"{path_basename(qss_fp)}{variant}_{sys.platform}.qss")
    )
    if platform_fp.exists():
        with open(platform_fp, 'r') as f:
            qss += "\n" + f.read()

    return qss





@dataclass(slots=True)
class HStyle:
    window_bgd: str = "#181819"

    # Combobox
    widget_bgd: str = "#353538"
    text_color: str = "#d4d4d8"
    # selection_bgd: str = "#454546"
    hover_bgd: str = "#505053"
    selection_bgd: str = "#5545bd"

    checked: str = "#6a5bcc"


    # checkbox
    enabled = "#1565C0"
    disabled = "#424242"




    # Accent (hover)	"#4e83c2"	 # Slightly lighter for hover feedback
    # Accent (pressed)	"#345d8a"	# Darker variant for pressed/active states
    # Accent (disabled)	"#2e3c4f"	# Desaturated accent for disabled controls
    # Base background	"#1e1f22"	# Main window / panel background
    # Widget background	"#2a2c30"	# Lighter inner surfaces (e.g. combobox, buttons)
    # Hover background	"#34373d"	# Light hover elevation
    # Text (normal)	"#e6e6e6"	# Soft white for text, not full white
    # Text (disabled)	"#777"	# Dimmed gray
    # Border (neutral)	"#3a3d42"	# Subtle border for structure
    # Border (focus)	"#3d6ea8"	# Accent border when focused


# Checked / Active	#422ca1	Checkbox, radio, selected item
# Hover / Focused	#5948c4	Slightly brighter — gives visual lift
# Pressed	#352283	Darker tone for click feedback
# Disabled	#2d2b3e	Muted, low-contrast desaturation

# 1080p
dp_to_px = 1.6
# 1440p
# dp_to_px = 1.2


COMBOBOX_HEIGHT = 32
COMBOBOX_RADIUS = 7
COMBOBOX_PADDING = 10

RADIO_RADIUS = 7
RADIO_BORDER_WIDTH = 2


# STATE_LAYER_SIZE: int = round(48/(2 * dp_to_px)) * 2
CHECKBOX_STATE_LAYER_SIZE: int = 40
# Icons are from Material website
CHECKBOX_ICON_SIZE: int = 24
# blank margin in Material icons -> real button size in icon is 18x18
CHECKBOX_BUTTON_SIZE: int = 18




LINEEDIT_HEIGHT = 32
LINEEDIT_RADIUS = 4
LINEEDIT_PADDING = 12
LINEEDIT_MIN_WIDTH = int(64 / dp_to_px)

