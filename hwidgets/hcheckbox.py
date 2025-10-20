from dataclasses import dataclass
import os
from pathlib import Path
from pprint import pprint
import sys
import time
from typing import Any, Literal, Optional, Sequence
from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QRectF,
    Signal,
    QSize,
    QTime,
    QUrl,
    QObject,
    Qt,
    QAbstractItemModel,
    QPersistentModelIndex,
    QSize,
    QEvent,
    QTimer,
    QPointF,

)
from PySide6.QtGui import (
    QPolygonF,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QDragEnterEvent,
    QEnterEvent,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPalette,
    QPixmap,
    QRadialGradient,
    QRegion,
    QTransform,
    QWheelEvent,
    QFocusEvent,
    QPaintEvent,
    QContextMenuEvent,
    QKeyEvent,
    QResizeEvent,
    QInputMethodEvent,
    QValidator,
    QShowEvent,
    QHideEvent,
    QPen,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QCompleter,
    QAbstractItemDelegate,
    QStyleOptionComboBox,
    QAbstractItemView,
    QLineEdit,
    QGridLayout,
    QFrame,
    QListView,
    QAbstractButton,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
)
from string import Template

from hutils import blue, lightcyan, lightgreen, lightgrey, orange, parent_directory, purple, yellow
sys.path.append(os.path.join(parent_directory(__file__), "hwidgets"))

import logging

from hstyle import *
hlogger = logging.getLogger("hwidgets")
logging.disable(logging.CRITICAL)


class HCheckBox(QCheckBox):

    def __init__(
        self,
        /,
        parent: QWidget | None = None,
        *,
        hstyle: HStyle,
    ) -> None:

        size: int = 16
        radius: int = 3
        border_width: int = 2
        accent_color: str = "#422ca1"    # checked / accent
        bg_color: str = "#2a2d32"       # unchecked background
        border_color: str = "#3a3d44"    # normal border
        disabled_color: str = "#4a4a4a"   # disabled tint


        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        # geometry & style parameters
        self._size = size
        self._radius = radius
        self._border_width = border_width

        # Colors (QColor objects for speed)
        self._accent = QColor(hstyle.widget_bgd)
        self.checked = QColor(hstyle.text_color)
        self._bg = QColor(hstyle.widget_bgd)
        self._border = QColor(border_color)
        self._disabled = QColor(disabled_color)
        self._hover = False
        self._pressed = False

        # make widget small—sizeHint will be used by layouts
        self.setMinimumSize(self.sizeHint())

    def sizeHint(self) -> QSize:
        # width reserves space for little box + spacing (no text, or can adapt)
        extra = 4
        return QSize(self._size + extra, self._size + extra)

    # ---- hit test: accept clicks inside the rounded rect (or a slightly larger area) ----
    def _inside_box(self, x: float, y: float) -> bool:
        # box rectangle
        r = QRectF(
            self._border_width/2 - 1,
            self._border_width/2 - 1,
            self._size + 2,
            self._size + 2
        )
        # simple bounding-box test first
        if not r.contains(x, y):
            return False
        # optional: allow rectangle hits (common) or do circular/rounded hit test
        # We'll just accept bounding rectangle for easier UX (you can tighten it)
        return True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            # toggle only when released inside the box area
            pos = event.position()
            if self._inside_box(pos.x(), pos.y()):
                # call toggle through click() to emit signals normally
                self.click()
            self._pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # compute rect for checkbox
        x = self._border_width/2
        y = (self.height() - self._size) / 2.0
        box = QRectF(x, y, self._size, self._size)

        # choose colors depending on state
        if not self.isEnabled():
            border_col = self._disabled
            fill_col = self._disabled
            tick_color = self.checked.darker(140)
        else:
            border_col = self._accent if (self._hover and not self.isChecked()) else self._border
            # when checked we fill with accent, else background
            fill_col = self._accent if self.isChecked() else self._bg
            tick_color = self.checked if self.isChecked() else QColor("transparent")

        # draw outer rounded rect (background)
        pen = QPen(border_col, self._border_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill_col))
        painter.drawRoundedRect(box, self._radius, self._radius)

        # draw inner tick or check mark when checked
        if self.isChecked():
            # option 1: filled smaller rounded rect (block style)
            # inset = max(2, int(self._size * 0.22))
            # inner = QRectF(box.left()+inset, box.top()+inset, box.width()-2*inset, box.height()-2*inset)
            # painter.setPen(Qt.NoPen)
            # painter.setBrush(QBrush(check_col))
            # painter.drawRoundedRect(inner, max(1, self._radius//2), max(1, self._radius//2))

            # option 2: draw a checkmark instead (uncomment if you prefer)
            painter.setPen(QPen(tick_color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p1 = QPointF(box.left()+box.width()*0.22, box.top()+box.height()*0.52)
            p2 = QPointF(box.left()+box.width()*0.45, box.top()+box.height()*0.75)
            p3 = QPointF(box.left()+box.width()*0.78, box.top()+box.height()*0.28)

            # painter.drawLine(p1, p2)
            # painter.drawLine(p2, p3)
            # # painter.setBrush(color)
            # painter.drawEllipse(p2, 1, 1)

            painter.drawPolyline(QPolygonF([p1, p2, p3]))

        # optionally draw focus rectangle or extra hover stroke
        if self._hover and self.isEnabled(): # and not self.isChecked():
            glow_pen = QPen(self._accent, 1.2)
            glow_pen.setColor(self._accent.lighter(130))
            painter.setPen(glow_pen)
            # slight outer stroke to indicate hover
            outer = QRectF(box.left()-1, box.top()-1, box.width()+2, box.height()+2)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(outer, self._radius+1, self._radius+1)

        painter.end()

    # convenience setters to tweak theme at runtime
    def setAccentColor(self, hexcolor: str):
        self._accent = QColor(hexcolor)
        self.update()

    def setBackgroundColor(self, hexcolor: str):
        self._bg = QColor(hexcolor)
        self.update()



# class HCheckBox(QWidget):

#     class _HCheckbox(QAbstractButton):

#         def __init__(self, parent: QWidget | None = ...) -> None:
#             super().__init__(parent)

#         def paintEvent(self, e: QPaintEvent) -> None:
#             return


#     def __init__(
#         self,
#         text: str,
#         /,
#         parent: QWidget | None = None,
#         *,
#         hstyle: HStyle,
#         tristate: bool = False,
#     ) -> None:

#         super().__init__(parent)
#         self.setCursor(Qt.CursorShape.PointingHandCursor)

#         self.is_tristate: bool = tristate
#         self.state: Qt.CheckState = Qt.CheckState.Unchecked

#         unchecked = "check_box_outline_blank_FILL0_wght500_GRAD0_opsz24.png"
#         partially = "indeterminate_check_box_FILL0_wght500_GRAD0_opsz24.png"
#         checked = "check_box_FILL0_wght500_GRAD0_opsz24.png"

#         self.pixmaps: dict[Qt.CheckState, dict[bool, QPixmap]] = {
#             Qt.CheckState.Unchecked: {
#                 True: self._generate_pixmap(filename=unchecked, color=hstyle.enabled),
#                 False: self._generate_pixmap(filename=unchecked, color=hstyle.disabled),
#             },
#             Qt.CheckState.PartiallyChecked: {
#                 True: self._generate_pixmap(filename=partially, color=hstyle.enabled),
#                 False: self._generate_pixmap(filename=partially, color=hstyle.disabled),
#             },
#             Qt.CheckState.Checked: {
#                 True: self._generate_pixmap(filename=checked, color=hstyle.enabled),
#                 False: self._generate_pixmap(filename=checked, color=hstyle.disabled),
#             },
#         }

#         self.setFixedSize(QSize(CHECKBOX_STATE_LAYER_SIZE, CHECKBOX_STATE_LAYER_SIZE))

#         layout = QHBoxLayout(self)
#         self.button = self._HCheckbox(self)
#         self.button.setFixedSize(QSize(CHECKBOX_BUTTON_SIZE, CHECKBOX_BUTTON_SIZE))
#         margins = [int((CHECKBOX_STATE_LAYER_SIZE - CHECKBOX_BUTTON_SIZE)/2) ] * 4
#         layout.setContentsMargins(*margins)
#         layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
#         self.setLayout(layout)

#         origin = [int((CHECKBOX_STATE_LAYER_SIZE - CHECKBOX_ICON_SIZE)/2)] * 2
#         self.pixmap_origin = QPoint(*origin)
#         self.painter = QPainter()

#         self.button.clicked[bool].connect(self.clicked_event)
#         self.button.pressed.connect(self.pressed_event)
#         self.button.released.connect(self.released_event)
#         self.button.toggled[bool].connect(self.toggled_event)


#     def _generate_pixmap(self, filename: str, color: str) -> QPixmap:
#         filepath = os.path.join(TITLE_BAR_ICON_PATH, filename)
#         if not os.path.exists(filepath):
#             raise ValueError(f"image {filepath} does not exist")
#         qimage: QImage = QImage(filepath)
#         color = QColor(color)

#         painter: QPainter = QPainter()
#         painter.begin(qimage)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
#         painter.setBrush(color)
#         painter.setPen(color)
#         painter.drawRect(qimage.rect())
#         painter.end()
#         return QPixmap(qimage)


#     def checkState(self) -> Qt.CheckState:
#         return self.state


#     # def hitButton(self, pos: QPoint) -> bool:
#     #     return self.checkbox.hitButton(pos)


#     def setCheckState(self, state: Qt.CheckState) -> None:
#         self.state = state


#     def setTristate(self, enabled: bool) -> None:
#         self.is_tristate = enabled


#     def isTristate(self) -> bool:
#         return self.is_tristate


#     def clicked_event(self, state: bool) -> None:
#         pass


#     def pressed_event(self) -> None:
#         pass


#     def released_event(self) -> None:
#         state: int = self.state.value
#         state = (state + 1) % 3 if self.is_tristate else ~state & 0x2
#         self.state: Qt.CheckState = Qt.CheckState._value2member_map_[state]
#         self.repaint()


#     def toggled_event(self, state: bool) -> None:
#         pass


#     def paintEvent(self, event: QPaintEvent) -> None:
#         pixmap = self.pixmaps[self.checkState()][self.isEnabled()]
#         self.painter.begin(self)
#         self.painter.drawPixmap(self.pixmap_origin, pixmap)

#         # For debug:
#         # pen = QPen('red')
#         # pen.setWidth(1)
#         # self.painter.setPen(pen)
#         # layer_rect = QRect(0, 0, CHECKBOX_WIDGET_SIZE-1, CHECKBOX_WIDGET_SIZE-1)
#         # self.painter.drawRect(layer_rect)

#         self.painter.end()






if __name__ == "__main__":
    import signal
    from argparse import ArgumentParser

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser()
    parser.add_argument("--debug", "-debug", action="store_true", required=False)
    arguments = parser.parse_args()
    if arguments.debug:
        import logging
        hlogger: logging.Logger = logging.getLogger("hwidgets")
        hlogger.addHandler(logging.StreamHandler(sys.stdout))
        logging.disable(logging.NOTSET)
        hlogger.setLevel("DEBUG")


    app = QApplication(sys.argv)

    hrl_style = HStyle()


    window = QWidget()
    window.setStyleSheet(f"""
        background-color: {hrl_style.window_bgd};
        color: {hrl_style.text_color};
    """)
    p = window.palette()
    p.setColor(window.backgroundRole(), hrl_style.window_bgd)
    window.setPalette(p)


    main_layout = QGridLayout(window)
    main_layout.setContentsMargins(50,50,50,300)
    main_layout.setSpacing(64)

    qcheckbox = QCheckBox(window)
    main_layout.addWidget(qcheckbox, 0, 1, 1, 1)

    hcheckbox = HCheckBox(window, hstyle=hrl_style)
    main_layout.addWidget(hcheckbox, 1, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

    window.show()

    sys.exit(app.exec())
