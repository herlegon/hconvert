
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

)
from PySide6.QtGui import (
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
)
from string import Template

from hutils import blue, lightcyan, lightgreen, lightgrey, orange, parent_directory, purple, yellow
sys.path.append(os.path.join(parent_directory(__file__), "hwidgets"))

import logging

from hstyle import *
hlogger = logging.getLogger("hwidgets")
logging.disable(logging.CRITICAL)




class HRadioButton(QRadioButton):
    def __init__(
        self,
        text: str,
        /,
        parent: QWidget | None = None,
        *,
        hstyle: HStyle,
    ) -> None:

        super().__init__(parent)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._hover = False
        self.setMouseTracking(True)

        # Colors
        self.bg_color = QColor(hstyle.widget_bgd)
        self.border_color = QColor(hstyle.widget_bgd)
        self.disabled_color = QColor(hstyle.disabled)

        self.hover_border_color = QColor(hstyle.selection_bgd)
        self.checked_color = QColor(hstyle.checked)

        # Dimensions
        self.radius = RADIO_RADIUS
        self.border_width = RADIO_BORDER_WIDTH


    def sizeHint(self):
        # Only the circle size matters
        return QSize(
            self.radius*2 + self.border_width*2,
            self.radius*2 + self.border_width*2
        )


    def leaveEvent(self, event: QEvent):
        hlogger.debug(f"{self.__class__}: leave")
        self._hover = False
        self.update()
        super().leaveEvent(event)


    def enterEvent(self, event: QEvent):
        hlogger.debug(f"{self.__class__}: over")
        self._hover = True
        self.update()
        super().enterEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        hlogger.debug(f"{self.__class__}: clicked")
        if self._hover:
            self.click()
        return super().mouseReleaseEvent(event)


    # To use if we want to detect mouse inside the circle and not the outer rect
    #  might have a speed impact and "frustrating" with small radio buttons
    #
    # def hitButton(self, pos):
    #     """Only toggle if click is inside the circle.
    #     The probleme is that the hover is done when in the rectangle. If hovered,
    #     with this method, the mouse click button doesn't work
    #     """
    #     center = self.rect().center()
    #     radius = self.radio_radius + self.border_width / 2
    #     dx = pos.x() - center.x()
    #     dy = pos.y() - center.y()
    #     return dx*dx + dy*dy <= radius*radius
    #
    #
    # def _is_inside_circle(self, x, y):
    #     """Check if point (x, y) is inside the circular area of the button."""
    #     radius = min(self.width(), self.height()) / 2
    #     dx = x - self.width() / 2
    #     dy = y - self.height() / 2
    #     return dx*dx + dy*dy <= radius*radius
    #
    #
    # def leaveEvent(self, event: QEvent):
    #     hlogger.debug(f"{self.__class__}: leave")
    #     pos = self.mapFromGlobal(self.cursor().pos())
    #     if not self._is_inside_circle(pos.x(), pos.y()):
    #         self._hover = True
    #         self.update()
    #     super().leaveEvent(event)
    #
    #
    # def enterEvent(self, event: QEnterEvent):
    #     pos = self.mapFromGlobal(self.cursor().pos())
    #     if self._is_inside_circle(pos.x(), pos.y()):
    #         self._hover = True
    #         self.update()
    #     super().enterEvent(event)
    #
    #
    # def mouseMoveEvent(self, event: QMouseEvent):
    #     inside = self._is_inside_circle(event.position().x(), event.position().y())
    #     if inside != self._hover:
    #         self._hover = inside
    #         self.update()
    #     super().mouseMoveEvent(event)


    def paintEvent(self, event: QEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Determine border color
        if not self.isEnabled():
            border_col = self.disabled_color
        else:
            border_col = self.hover_border_color if self._hover else self.border_color

        # Draw the outer circle
        outer_rect = QRectF(
            1,
            (self.height() - self.radius*2)/2,
            self.radius*2,
            self.radius*2
        )
        pen = QPen(border_col, self.border_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.bg_color if self.isEnabled() else self.disabled_color))
        painter.drawEllipse(outer_rect)

        # Draw the inner circle if checked
        if self.isChecked():
            inner_radius = self.radius / 2 + 1
            inner_rect = QRectF(
                outer_rect.center().x() - inner_radius,
                outer_rect.center().y() - inner_radius,
                inner_radius*2,
                inner_radius*2
            )
            painter.setBrush(QBrush(self.checked_color if self.isEnabled() else self.disabled_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(inner_rect)

        # # Draw the text
        # painter.setPen(QPen(QColor("white") if self.isEnabled() else self.disabled_color))
        # text_x = self.radio_radius*2 + 8
        # text_y = 0
        # text_rect = QRectF(text_x, text_y, self.width() - text_x, self.height())
        # painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())

        painter.end()




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

    qradiobutton = QRadioButton(window)
    qradiobutton2 = QRadioButton(window)
    qbuttonGroup = QButtonGroup(window)
    qbuttonGroup.addButton(qradiobutton)
    qbuttonGroup.addButton(qradiobutton2)
    main_layout.addWidget(qradiobutton, 0, 1, 1, 1)
    main_layout.addWidget(qradiobutton2, 0, 0, 1, 1)

    hradiobutton = HRadioButton(window, hstyle=hrl_style)
    hradiobutton2 = HRadioButton(window, hstyle=hrl_style)
    hbuttonGroup = QButtonGroup(window)
    hbuttonGroup.addButton(hradiobutton)
    hbuttonGroup.addButton(hradiobutton2)
    main_layout.addWidget(hradiobutton, 1, 1, 1, 1, Qt.AlignmentFlag.AlignRight)
    main_layout.addWidget(hradiobutton2, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)

    window.show()




    sys.exit(app.exec())
