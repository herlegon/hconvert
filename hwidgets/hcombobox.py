
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
    QPen,
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
    QBitmap,
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
)
from string import Template


from hutils import blue, lightcyan, lightgreen, lightgrey, orange, parent_directory, purple, yellow
sys.path.append(os.path.join(parent_directory(__file__), "hwidgets"))

from hstyle import *

import logging
hlogger = logging.getLogger("hwidgets")
logging.disable(logging.CRITICAL)





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




class RoundedListView(QListView):
    def __init__(self, stylesheet: str, radius: int, bgd_color: str, parent=None):
        super().__init__(parent)
        self.radius = radius + 1
        self.bgd_color = QColor(bgd_color)
        self.setStyleSheet(stylesheet)
        self.setSpacing(0)
        self.setUniformItemSizes(True)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.margin_top = 0
        self.margin_bottom = COMBOBOX_RADIUS

    def paintEvent(self, event):
        """Paint rounded background with bottom corners rounded only."""
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.viewport().rect().adjusted(0, self.margin_top, 1, -self.margin_bottom)
        path = QPainterPath()

        # Only bottom corners rounded
        path.moveTo(rect.topLeft())
        path.lineTo(rect.bottomLeft().x(), rect.bottomLeft().y() - self.radius)
        path.quadTo(rect.bottomLeft(), rect.bottomLeft() + QPoint(self.radius, 0))
        path.lineTo(rect.bottomRight().x() - self.radius, rect.bottomRight().y())
        path.quadTo(rect.bottomRight(), rect.bottomRight() + QPoint(0, -self.radius))
        path.lineTo(rect.topRight())

        painter.fillPath(path, self.bgd_color)
        super().paintEvent(event)



class HComboBox(QComboBox):
    signal_f_selected = Signal(str)


    def __init__(
        self,
        /,
        parent: QWidget | None = None,
        *,
        hstyle: HStyle,
        editable: bool | None = ...,
        count: int | None = ...,
        currentText: str | None = ...,
        currentIndex: int | None = ...,
        currentData: Any | None = ...,
        maxVisibleItems: int | None = ...,
        maxCount: int | None = ...,
        insertPolicy: QComboBox.InsertPolicy | None = ...,
        sizeAdjustPolicy: QComboBox.SizeAdjustPolicy | None = ...,
        minimumContentsLength: int | None = ...,
        iconSize: QSize | None = ...,
        placeholderText: str | None = ...,
        duplicatesEnabled: bool | None = ...,
        frame: bool | None = ...,
        modelColumn: int | None = ...,
        labelDrawingMode: QComboBox.LabelDrawingMode | None = ...,
    ) -> None:
        super().__init__(parent)

        # # Apply optional parameters if provided
        # if editable is not None:
        #     self.setEditable(editable)
        # if currentIndex is not None:
        #     self.setCurrentIndex(currentIndex)
        # if currentText is not None:
        #     self.setCurrentText(currentText)
        # if maxVisibleItems is not None:
        #     self.setMaxVisibleItems(maxVisibleItems)
        # if maxCount is not None:
        #     self.setMaxCount(maxCount)
        # if insertPolicy is not None:
        #     self.setInsertPolicy(insertPolicy)
        # if sizeAdjustPolicy is not None:
        #     self.setSizeAdjustPolicy(sizeAdjustPolicy)
        # if minimumContentsLength is not None:
        #     self.setMinimumContentsLength(minimumContentsLength)
        # if iconSize is not None:
        #     self.setIconSize(iconSize)
        # if placeholderText is not None:
        #     self.setPlaceholderText(placeholderText)
        # if duplicatesEnabled is not None:
        #     self.setDuplicatesEnabled(duplicatesEnabled)
        # if frame is not None:
        #     self.setFrame(frame)
        # if modelColumn is not None:
        #     self.setModelColumn(modelColumn)
        # if labelDrawingMode is not None:
        #     self.setLabelDrawingMode(labelDrawingMode)


        self.setCursor(Qt.CursorShape.ArrowCursor)

        self.setHeight(COMBOBOX_HEIGHT, COMBOBOX_RADIUS)
        self.setFixedWidth(230)
        self.setAcceptDrops(True)
        self.load_dd_icon("keyboard_arrow_down_FILL0_wght500_GRAD0_opsz24.png")

        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        )

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.set_stylesheet(hstyle=hstyle)

        self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.lineEdit().setCursor(Qt.CursorShape.PointingHandCursor)


        self.can_hide: bool = False
        self.is_popup_visible = False
        self.counter: int = 0

        # Install event filter on the line edit
        if self.lineEdit():
            self.lineEdit().installEventFilter(self)
            self.lineEdit().setReadOnly(True)
        # self.setEditable(True)
        # self.setEditable(True)
        self.installEventFilter(self)


    def set_stylesheet(self, hstyle: HStyle):
        self.variant = ""

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        qss_template = Template(load_qss(f"hcombobox_abstractitemview.css", variant=self.variant))
        self.popup_qss = qss_template.substitute(
            radius=f"{COMBOBOX_RADIUS}px",
            padding=f"{COMBOBOX_PADDING}px",
            margin=f"{COMBOBOX_RADIUS}px",
            margin_top=f"{COMBOBOX_RADIUS // 2}px",
            popup_width = f"{self.width()}px",
            combobox_height=f"{int(1.5 * (COMBOBOX_HEIGHT - COMBOBOX_RADIUS))}px",
            padding_left=f"{COMBOBOX_RADIUS}px",
            window_bgd=hstyle.window_bgd,
            widget_bgd=hstyle.widget_bgd,
            text_color=hstyle.text_color,
            selection_bgd=hstyle.selection_bgd,

        )

        if sys.platform == 'win32':
            view = RoundedListView(
                stylesheet=self.popup_qss,
                radius=COMBOBOX_RADIUS,
                bgd_color=hstyle.widget_bgd,
                parent=self
            )
            self.setView(view)
            self.view().setWindowFlags(Qt.Widget)
        else:
            self.view().setStyleSheet(self.popup_qss)

        qss_template = Template(load_qss(f"hcombobox.css", variant=self.variant))
        qss = qss_template.substitute(
            radius=f"{COMBOBOX_RADIUS}px",
            padding=f"{COMBOBOX_PADDING}px",
            padding_right=f"{COMBOBOX_PADDING + COMBOBOX_RADIUS}px",
            padding_left=f"{COMBOBOX_RADIUS}px",
            arrow_space = f"{24 + COMBOBOX_PADDING}px",
            combobox_height=f"{COMBOBOX_HEIGHT - COMBOBOX_RADIUS}px",
            margin=f"{COMBOBOX_RADIUS}px",
            list_margin=f"{COMBOBOX_RADIUS * 4}px",
            popup_width = f"{self.width()}px",
            window_bgd=hstyle.window_bgd,
            widget_bgd=hstyle.widget_bgd,
            text_color=hstyle.text_color,
            selection_bgd=hstyle.selection_bgd,
            hover_bgd=hstyle.hover_bgd
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(qss)

        qss_template = Template(load_qss(f"hcombobox_lineedit.css", variant=self.variant))
        qss = qss_template.substitute(
            arrow_space = f"{24 + COMBOBOX_PADDING}px",
            widget_bgd = hstyle.widget_bgd,
            padding=f"{COMBOBOX_PADDING}px",
            # padding_left=f"{int(COMBOBOX_RADIUS * 1.5)}px",
            padding_left=f"{COMBOBOX_RADIUS // 2}px",

            # padding_left=f"0px",
            padding_right=f"{COMBOBOX_PADDING + COMBOBOX_RADIUS}px",
            selection_bgd=hstyle.selection_bgd,

        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.lineEdit().setStyleSheet(qss)


    def showPopup(self):
        self.can_hide = False

        if sys.platform == 'win32':
            self.is_popup_visible = True
            super().showPopup()

        hlogger.debug(purple(f"{int(time.time())}  OPEN"))
        popup = self.view().window()
        if not popup:
            # print(f" no popup")
            return

        # Make the popup a frameless popup and allow transparent background on the window.
        # On Windows this generally works; on some Linux setups true transparency may be
        # limited — but we don't require transparency, because the view draws the background.
        flags = popup.windowFlags()
        popup.setWindowFlags(flags | Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        popup.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        popup.setStyleSheet("QFrame { background: transparent; border: none; }")
        popup.resize(self.width(), popup.height() + 2 * COMBOBOX_RADIUS)
        self.view().setGeometry(0, 0, popup.width(), popup.height())
        self.view().viewport().update()

        if sys.platform == 'linux':
            # self.blockSignals(True)
            super().showPopup()
            self.is_popup_visible = True


    def hidePopup(self):
        if not self.can_hide:
            hlogger.debug(f"  ignore hide, allow for next time")
            self.can_hide = True
            return
        else:
            hlogger.debug(f"  can hide")

        hlogger.debug(purple(f"{int(time.time())}  HIDE"))
        # self.view().removeEventFilter(self.view())
        self.counter = 0
        super().hidePopup()
        self.is_popup_visible = False


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        event_type: QEvent.Type = event.type()
        # if watched == self.view():
        #     if event_type not in (
        #         QEvent.Type.Paint,
        #         QEvent.Type.UpdateLater,
        #     ):
        #         print(lightgreen(f"{int(time.time())} VIEW:"), event)

        #     else:
        #         print(lightgreen(f"{int(time.time())} VIEW:"), event)

        if watched == self.lineEdit():
            if (
                event_type == QEvent.Type.MouseButtonRelease
                and event.button() == Qt.MouseButton.LeftButton
            ):
                hlogger.debug(lightgreen(f"{int(time.time())} LE MouseButtonRelease"))
                hlogger.debug(f"\n    can_hide: {self.can_hide}")
                return True


            elif (
                event_type == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                hlogger.debug(lightgreen(f"{int(time.time())} LE MouseButtonPress"))
                self.lineEdit().deselect()
                if not self.view().isVisible():
                    self.can_hide = False
                    self.showPopup()
                    # print(f" lets open, can't hide now")
                    return True
                return True

            elif event_type == QEvent.Type.HoverLeave:
                hlogger.debug(yellow(f"{int(time.time())} lineedit: HoverLeave, can_hide: {self.can_hide}"))
                if self.view().isVisible():
                    hlogger.debug(f"  is visible")
                    self.can_hide = True

            # else:
            #     print(yellow(f"{int(time.time())} LE:"), event)

        elif watched == self:
            if event_type == QEvent.Type.InputMethodQuery:
                hlogger.debug(f"{lightcyan(f"{int(time.time())} CB: InputMethodQuery")}")
                hlogger.debug(f"{event}")
                if self.view().isVisible() and self.is_popup_visible:
                    hlogger.debug(" is visible")
                    if self.counter > 0:
                        hlogger.debug(" counter > 1, hide popup")
                        self.can_hide = True
                        self.counter = 0
                        self.hidePopup()
                    else:
                        self.counter += 1

            elif (
                event_type == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                hlogger.debug(lightgreen(f"{int(time.time())} CB MouseButtonPress"))
                self.lineEdit().deselect()
                if not self.view().isVisible():
                    self.can_hide = True
                    self.showPopup()
                    # print(f" lets open, can't hide now")
                    return True

            # else:
            #     print(lightcyan(f"{int(time.time())} CB:"), event)


        # else:
        #     print(blue(f"unknown:"), event)


        return super().eventFilter(watched, event)



    def setHeight(self, height: int, radius:int) -> None:
        self.radius = radius
        self.dd_height = height - 2 * radius
        self.dd_width = self.dd_height
        self.dd_size: QSize = QSize(self.dd_width, self.dd_height)
        return super().setFixedHeight(height)


    def load_dd_icon(self, icon: str | Path) -> None:
        filepath = os.path.join(TITLE_BAR_ICON_PATH, icon)
        try:
            self.dd_pixmap = load_png_icon(filepath, "#E1E1E1")
        except:
            raise ValueError(f"{filepath} not found")

        if self.dd_pixmap.size() != self.dd_size:
            self.dd_pixmap = self.dd_pixmap.scaled(
                self.dd_size,
                aspectMode=Qt.AspectRatioMode.KeepAspectRatio
            )


    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)
        painter: QPainter = QPainter(self)
        x = self.width() - self.dd_width - COMBOBOX_PADDING
        y = int(self.height() - self.dd_pixmap.height())/2

        painter.drawPixmap(QPoint(x, y), self.dd_pixmap)




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

    items = [
        "This is a long text you can select if you want",
        "Another item to test a very very very long text to display",
        "Copy me with Ctrl+C you should see some dots in the line",
        "Right-click won't work"
    ]

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

    qcombobox = QComboBox(window)
    qcombobox.addItems(items)

    hcombobox = HComboBox(window, hstyle=hrl_style)
    hcombobox.addItems(items)

    main_layout.addWidget(qcombobox, 0, 0, 1, 1)
    main_layout.addWidget(hcombobox, 0, 1, 1, 1)

    window.show()
    sys.exit(app.exec())
