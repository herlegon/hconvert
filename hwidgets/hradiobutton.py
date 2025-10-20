
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
)
from string import Template

from hutils import blue, lightcyan, lightgreen, lightgrey, orange, parent_directory, purple, yellow
sys.path.append(os.path.join(parent_directory(__file__), "hwidgets"))

import logging

from hstyle import *
hlogger = logging.getLogger("hwidgets")
logging.disable(logging.CRITICAL)








class HRadioButton(QAbstractButton):
    signal_f_selected = Signal(str)

    def __init__(
        self,
        text: str,
        /,
        parent: QWidget | None = None,
        *,
        hstyle: HStyle,
    ) -> None:

        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.checked: bool = False
        self.setChecked(False)

        unchecked = "radio_button_unchecked_FILL0_wght500_GRAD0_opsz20.png"
        checked = "radio_button_checked_FILL0_wght500_GRAD0_opsz20.png"

        self.pixmaps: dict[bool, dict[bool, QPixmap]] = {
            False: {
                True: self._generate_pixmap(
                    filename=unchecked,
                    color=hstyle.enabled
                ),
                False: self._generate_pixmap(
                    filename=unchecked, color=hstyle.disabled
                ),
            },
            True: {
                True: self._generate_pixmap(
                    filename=checked, color=hstyle.enabled
                ),
                False: self._generate_pixmap(
                    filename=checked, color=hstyle.disabled
                ),
            },
        }
        self.setFixedSize(QSize(STATE_LAYER_SIZE, STATE_LAYER_SIZE))
        origin = [int((STATE_LAYER_SIZE - ICON_SIZE)/2)] * 2
        self.pixmap_origin = QPoint(*origin)
        self.painter = QPainter()
        self.setText("")

        self.released.connect(self.released_event)
        # self.toggled[bool].connect(self.toggled_event)
        # self.clicked[bool].connect(self.clicked_event)
        # self.pressed.connect(self.pressed_event)


    # def toggled_event(self, state):
    #     print("toggled_event")

    # def clicked_event(self, state):
    #     print("clicked_event")

    # def pressed_event(self):
    #     print("pressed_event")


    def _generate_pixmap(self, filename: str, color: str) -> QPixmap:
        filepath = os.path.join(TITLE_BAR_ICON_PATH, filename)
        if not os.path.exists(filepath):
            raise ValueError(f"Missing icon: {filepath}")
        qimage: QImage = QImage(filepath)
        color = QColor(color)

        painter: QPainter = QPainter()
        painter.begin(qimage)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawRect(qimage.rect().adjusted(1,1,-1,-1))
        painter.end()
        return QPixmap(qimage)


    def setText(self, text: str) -> None:
        pass


    def released_event(self) -> None:
        self.setChecked(not self.checked)


    def setChecked(self, checked: bool) -> None:
        self.checked = checked
        super().setChecked(self.checked)
        self.update()


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        event_type = event.type()
        # print(f"{self.id}: 0x{event_type:02x}")
        return super().eventFilter(watched, event)


    def paintEvent(self, event: QPaintEvent) -> None:
        pixmap = self.pixmaps[self.checked][self.isEnabled()]
        self.painter.begin(self)
        self.painter.drawPixmap(self.pixmap_origin, pixmap)

        # For debug:
        # pen = QPen('red')
        # pen.setWidth(1)
        # self.painter.setPen(pen)
        # layer_rect = QRect(0, 0, STATE_LAYER_SIZE-1, STATE_LAYER_SIZE-1)
        # self.painter.drawRect(layer_rect)

        self.painter.end()




if __name__ == "__main__":
    import signal
    from argparse import ArgumentParser

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser()
    parser.add_argument("--debug", "-debug", action="store_true", required=False)
    arguments = parser.parse_args()
    if arguments.debug:
        import logging
        logger: logging.Logger = logging.getLogger("hwidgets")
        hlogger.addHandler(logging.StreamHandler(sys.stdout))
        logging.disable(logging.NOTSET)
        hlogger.setLevel("DEBUG")


    app = QApplication(sys.argv)

    hrl_style = HStyle()
    pprint(hrl_style)


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

    hradiobutton = HRadioButton(window, hstyle=hrl_style)

    main_layout.addWidget(qradiobutton, 0, 0, 1, 1)
    main_layout.addWidget(hradiobutton, 0, 1, 1, 1)

    window.show()
    sys.exit(app.exec())
