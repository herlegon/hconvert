
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
)
from string import Template


from hutils import blue, lightcyan, lightgreen, lightgrey, orange, parent_directory, purple, yellow
sys.path.append(os.path.join(parent_directory(__file__), "hwidgets"))

from hstyle import *

import logging
hlogger = logging.getLogger("hwidgets")
logging.disable(logging.CRITICAL)




class RLineEdit(QLineEdit):

    def __init__(self, parent: Optional[QWidget]) -> None:

        super().__init__(parent)
        # self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(LINEEDIT_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.set_style()
        self.setClearButtonEnabled(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(300)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,LINEEDIT_PADDING,0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addStretch(1)

        self.clear_button = QPushButton(self)
        self.clear_button.setFixedSize(QSize(LINEEDIT_HEIGHT, LINEEDIT_HEIGHT))
        self.clear_button.setFlat(True)
        self.clear_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.released.connect(self.clear_button_released)
        icon = QIcon()
        icon.addPixmap(
            load_png_icon("cancel_FILL0_wght300_GRAD0_opsz24.png", "#E1E1E1"),
            QIcon.Mode.Normal, QIcon.State.Off
        )
        self.clear_button.setIcon(icon)
        self.main_layout.addWidget(self.clear_button, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(self.main_layout)

        self.clear_button.hide()
        self.textChanged[str].connect(self.text_changed)
        self.textEdited[str].connect(self.text_changed)


    def clear_button_released(self):
        self.clear()
        self.clear_button.hide()


    def text_changed(self, text: str) -> None:
        if len(text) > 0:
            self.clear_button.show()
        else:
            self.clear_button.hide()


    # def enterEvent(self, event: QEnterEvent) -> None:
    #     if len(self.text()) > 0:
    #         self.clear_button.show()
    #     return super().enterEvent(event)


    def set_style(self) -> None:
        self._update_stylesheet()
        self.setStyleSheet(self.stylesheets[True])
        self.repaint()


    def _update_stylesheet(self) -> None:
        stylesheet = """
            QPushButton {{
                border: 0px;
                outline: none;
            }}

            LineEdit {{
                color: {color};
                border: 1px solid;
                border-radius: {radius}px;
                border-color: {border_color};
                padding-left: {padding}px;
                padding-right: {padding_right}px;
                min-width: {min_width}px;
                background-color: {bgd_color};

            }}
            LineEdit:focus {{
                color: {color_hover};
                border-color: {bgd_color_hover};
            }}
            LineEdit:hover {{
                color: {color_hover};
                border-color: {bgd_color_hover};
            }}
            LineEdit:disabled {{
                color: {color_disabled};
                background-color: {bgd_color_disabled};
            }}
        """
        hstyle = HStyle()


        self.stylesheets: dict[bool, str] = {
            True: stylesheet.format(
                border_color=hstyle.selection_bgd,
                radius=min(COMBOBOX_RADIUS, int(self.height()/2)),
                min_width=LINEEDIT_MIN_WIDTH,
                padding=LINEEDIT_PADDING,
                padding_right=LINEEDIT_HEIGHT + LINEEDIT_PADDING,

                color=hstyle.text_color,
                bgd_color=hstyle.widget_bgd,
                color_hover=hstyle.text_color,
                bgd_color_hover=hstyle.selection_bgd,
                color_pressed=hstyle.text_color,
                bgd_color_pressed=hstyle.widget_bgd,
                bgd_color_checked=hstyle.checked,
                color_disabled=hstyle.disabled,
                bgd_color_disabled=hstyle.disabled,
            )
        }





# class HLineEditNew(QLineEdit):

#     def __init__(
#         self,
#         /,
#         parent: QWidget | None = ...,
#         *,
#         hstyle: HStyle,
#         inputMask: str | None = ...,
#         text: str | None = ...,
#         maxLength: int | None = ...,
#         frame: bool | None = ...,
#         echoMode: QLineEdit.EchoMode | None = ...,
#         displayText: str | None = ...,
#         cursorPosition: int | None = ...,
#         alignment: Qt.AlignmentFlag | None = ...,
#         modified: bool | None = ...,
#         hasSelectedText: bool | None = ...,
#         selectedText: str | None = ...,
#         dragEnabled: bool | None = ...,
#         readOnly: bool | None = ...,
#         undoAvailable: bool | None = ...,
#         redoAvailable: bool | None = ...,
#         acceptableInput: bool | None = ...,
#         placeholderText: str | None = ...,
#         cursorMoveStyle: Qt.CursorMoveStyle | None = ...,
#         clearButtonEnabled: bool | None = ...
#     ) -> None: ...

#         # @typing.overload
#         # def __init__(
#         # self,
#         #  /,
#         # parent: QWidget | None = ..., *,
#         # inputMask: str | None = ...,
#         # text: str | None = ...,
#         # maxLength: int | None = ...,
#         # frame: bool | None = ...,
#         # echoMode: QLineEdit.EchoMode | None = ...,
#         # displayText: str | None = ...,
#         # cursorPosition: int | None = ...,
#         # alignment: Qt.AlignmentFlag | None = ...,
#         # modified: bool | None = ...,
#         # hasSelectedText: bool | None = ...,
#         # selectedText: str | None = ...,
#         # dragEnabled: bool | None = ...,
#         # readOnly: bool | None = ...,
#         # undoAvailable: bool | None = ...,
#         # redoAvailable: bool | None = ...,
#         # acceptableInput: bool | None = ...,
#         # placeholderText: str | None = ...,
#         # cursorMoveStyle: Qt.CursorMoveStyle | None = ...,
#         # clearButtonEnabled: bool | None = ...
#         # ) -> None: ...

#         super().__init__(parent)


#         self.setCursor(Qt.CursorShape.ArrowCursor)

#         self.setHeight(COMBOBOX_HEIGHT, COMBOBOX_RADIUS)
#         self.setFixedWidth(230)
#         self.setAcceptDrops(True)
#         self.load_dd_icon("keyboard_arrow_down_FILL0_wght500_GRAD0_opsz24.png")

#         self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
#         self.setSizePolicy(
#             QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
#         )

#         self.setEditable(True)
#         self.lineEdit().setReadOnly(True)
#         self.set_stylesheet(hstyle=hstyle)

#         self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
#         self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
#         self.lineEdit().setCursor(Qt.CursorShape.PointingHandCursor)


#         self.can_hide: bool = False
#         self.is_popup_visible = False
#         self.counter: int = 0

#         # Install event filter on the line edit
#         if self.lineEdit():
#             self.lineEdit().installEventFilter(self)
#             self.lineEdit().setReadOnly(True)
#         # self.setEditable(True)
#         # self.setEditable(True)
#         self.installEventFilter(self)


#     def set_stylesheet(self, hstyle: HStyle):



#         # self.variant = "_premiere"
#         self.variant = "_hrl"

#         with open(Path(__file__).parent / Path(f"hLineEdit{self.variant}.qss"), "r") as f:
#             qss_template = Template(f.read())

#         qss = qss_template.substitute(
#             radius=f"{COMBOBOX_RADIUS}px",
#             padding=f"{COMBOBOX_PADDING}px",
#             padding_right=f"{COMBOBOX_PADDING + COMBOBOX_RADIUS}px",
#             padding_left=f"{COMBOBOX_RADIUS}px",
#             arrow_space = f"{24 + COMBOBOX_PADDING}px",
#             combobox_height=f"{COMBOBOX_HEIGHT - COMBOBOX_RADIUS}px",
#             margin=f"{COMBOBOX_RADIUS}px",
#             list_margin=f"{COMBOBOX_RADIUS * 4}px",
#             popup_width = f"{self.width()}px",
#             window_bgd=hstyle.window_bgd,
#             widget_bgd=hstyle.widget_bgd,
#             text_color=hstyle.text_color,
#             selection_bgd=hstyle.selection_bgd,
#         )
#         self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
#         self.setStyleSheet(qss)



#     def load_dd_icon(self, icon: str | Path) -> None:
#         filepath = os.path.join(TITLE_BAR_ICON_PATH, icon)
#         try:
#             self.dd_pixmap = load_png_icon(filepath, "#E1E1E1")
#         except:
#             raise ValueError(f"{filepath} not found")

#         if self.dd_pixmap.size() != self.dd_size:
#             self.dd_pixmap = self.dd_pixmap.scaled(
#                 self.dd_size,
#                 aspectMode=Qt.AspectRatioMode.KeepAspectRatio
#             )


#     def paintEvent(self, e: QPaintEvent) -> None:
#         super().paintEvent(e)
#         painter: QPainter = QPainter(self)
#         x = self.width() - self.dd_width - COMBOBOX_PADDING
#         y = int(self.height() - self.dd_pixmap.height())/2

#         painter.drawPixmap(QPoint(x, y), self.dd_pixmap)




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

    qlineedit = QLineEdit(window)
    qlineedit_rw = QLineEdit(window)

    hlineedit = RLineEdit(window) #, hstyle=hrl_style)
    hlineedit_rw = RLineEdit(window) #, hstyle=hrl_style)


    main_layout.addWidget(qlineedit, 1, 0, 1, 1)
    main_layout.addWidget(hlineedit, 1, 1, 1, 1)
    main_layout.addWidget(qlineedit_rw, 0, 0, 1, 1)
    main_layout.addWidget(hlineedit_rw, 0, 1, 1, 1)

    window.show()
    sys.exit(app.exec())
