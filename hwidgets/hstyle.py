from dataclasses import dataclass
import os
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
from hutils import parent_directory



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


@dataclass(slots=True)
class HStyle:
    window_bgd: str = "#181819"

    # Combobox
    widget_bgd: str = "#303031"
    text_color: str = "#d4d4d8"
    # selection_bgd: str = "#454546"
    selection_bgd: str = "#5545bd"

    checked: str = "#552ca1"


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



COMBOBOX_HEIGHT = 32
COMBOBOX_RADIUS = 5
COMBOBOX_PADDING = 10


# def apply_stylesheet(app, dark=False):
#     qss_file = "fluent_dark.qss" if dark else "fluent.qss"
#     qss = qss_template.format(
#         radius=f"{COMBOBOX_RADIUS}",
#         padding=COMBOBOX_PADDING,
#         padding_right=COMBOBOX_PADDING + COMBOBOX_RADIUS
#     )

#     with open(qss_file, "r") as f:
#         f.read()
#         app.setStyleSheet()


class BoldHoverDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Make font bold on hover or selection
        if option.state & QStyle.StateFlag.State_MouseOver or \
           option.state & QStyle.StateFlag.State_Selected:
            font = QFont(option.font)
            font.setBold(True)
            option.font = font
        super().paint(painter, option, index)



# 1080p
dp_to_px = 1.6
# 1440p
# dp_to_px = 1.2

# M3 material (use CHeckboxe dimensions)
#   Container width     18dp
#   Container height    18dp
#   Container shape     2dp
#   Icon size           18dp
#   Icon alignment      Center-aligned
#   Target size         48dp
#   State-layer size    40dp
STATE_LAYER_SIZE: int = int(1.5 * COMBOBOX_HEIGHT/(2 * dp_to_px))
# Icons are from Material website
ICON_SIZE: int = 24
# blank margin in Material icons -> real button size in icon is 18x18
BUTTON_SIZE: int = 16





