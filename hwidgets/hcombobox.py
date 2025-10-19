
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





class ComboBoxItem:
    def __init__(self, text: str, user_data: Any | None = None) -> None:
        self._text = text
        self._user_data = user_data
    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text

    @property
    def user_data(self) -> Any:
        return self._user_data

    @user_data.setter
    def user_data(self, user_data: Any) -> None:
        self._user_data = user_data




COMBOBOX_HEIGHT = 32
COMBOBOX_RADIUS = 8
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




class RoundedListView(QListView):
    def __init__(self, stylesheet: str, radius=20, bg_color="#00ff00", parent=None):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = QColor(bg_color)
        # Make viewport transparent so we can paint the rounded background there
        self.setStyleSheet(stylesheet)
        self.setSpacing(0)
        self.setUniformItemSizes(True)
        # ensure hover/selection mouse tracking
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

    def paintEvent(self, event):
        # paint rounded background into the viewport, then let QListView draw items
        vp = self.viewport()
        painter = QPainter(vp)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = vp.rect()
        # small inset so selection rounded corners don't clip
        path = QPainterPath()

        path.addRoundedRect(QRectF(rect), self.radius, self.radius)
        painter.fillPath(path, self.bg_color)
        painter.setPen(Qt.NoPen)
        super().paintEvent(event)




class HComboBox(QComboBox):
    signal_f_selected = Signal(str)


    def __init__(
        self,
        /,
        parent: QWidget | None = None,
        *,
        bgd: str,
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
        self.set_stylesheet(window_bgd=bgd)
        self.window_bgd = bgd

        self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.lineEdit().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.lineEdit().setCursor(Qt.CursorShape.PointingHandCursor)


        self.can_hide: bool = False
        self.counter: int = 0

        # Install event filter on the line edit
        if self.lineEdit():
            self.lineEdit().installEventFilter(self)
            self.lineEdit().setReadOnly(True)
        # self.setEditable(True)
        # self.setEditable(True)
        self.installEventFilter(self)


    def set_stylesheet(self, window_bgd: str):

        self.widget_bgd = "#202020"

        self.variant = "_premiere"

        with open(Path(__file__).parent / Path(f"hcombobox{self.variant}.qss"), "r") as f:
            qss_template = Template(f.read())

        qss = qss_template.substitute(
            radius=f"{COMBOBOX_RADIUS}px",
            padding=f"{COMBOBOX_PADDING}px",
            padding_right=f"{COMBOBOX_PADDING + COMBOBOX_RADIUS}px",
            arrow_space = f"{24 + COMBOBOX_PADDING}px",
            combobox_height=f"{COMBOBOX_HEIGHT - COMBOBOX_RADIUS}px",
            margin=f"{COMBOBOX_RADIUS}px",
            list_margin=f"{COMBOBOX_RADIUS * 4}px",
            popup_width = f"{self.width()}px",
            window_bgd=window_bgd,
            widget_bgd=self.widget_bgd,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(qss)



        with open(Path(__file__).parent / Path(f"hcombobox_lineedit{self.variant}.qss"), "r") as f:
            qss_template = Template(f.read())
        qss = qss_template.substitute(
            arrow_space = f"{24 + COMBOBOX_PADDING}px",
            widget_bgd = self.widget_bgd
        )
        self.lineEdit().setStyleSheet(qss)


        with open(Path(__file__).parent / Path(f"hcombobox_abstractitemview{self.variant}.qss"), "r") as f:
            qss_template = Template(f.read())
        self.popup_qss = qss_template.substitute(
            radius=f"{COMBOBOX_RADIUS//2}px",
            padding=f"{COMBOBOX_PADDING}px",
            margin=f"{COMBOBOX_RADIUS}px",
            popup_width = f"{self.width()}px",
            widget_bgd=self.widget_bgd,
            window_bgd=window_bgd,
            combobox_height=f"{int(1.5 * (COMBOBOX_HEIGHT - COMBOBOX_RADIUS))}px",

        )
        # self.view().setStyleSheet(self.popup_qss)

        # delegate = BoldHoverDelegate()
        # self.view().setItemDelegate(delegate)
        # self.view().setSpacing(COMBOBOX_PADDING//2)


        view = RoundedListView(
            stylesheet=self.popup_qss,
            radius=COMBOBOX_RADIUS,
            bg_color=self.widget_bgd
        )
        self.setView(view)



    def showPopup(self):
        super().showPopup()

        print(purple(f"{int(time.time())}  OPEN"))
        popup = self.view().window()
        if not popup:
            return

        if False:
            popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)

            # popup.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


            # Get parent background color
            # parent_bg = self.palette().color(self.backgroundRole())

            # Set popup frame background to match parent (creates illusion of transparency)
            # self.view().setFrameShape(QFrame.NoFrame)
            self.view().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.view().setStyleSheet(f"""
                QFrame {{
                    background-color: green;
                    /* border: none; */
                    border-radius: 20px;
                                    padding-left: 30px;
                }}
            """)

            popup.resize(self.width(), popup.height())
            popup.move(self.mapToGlobal(QPoint(0, self.height() + COMBOBOX_PADDING)))


            # popup.setStyleSheet(f"""
            #     QFrame {{
            #         background-color: red;
            #         /* border: none; */
            #         border-radius: 20px;
            #     }}
            # """)
            # self.view().setFrameShape(QFrame.NoFrame)
            # self.view().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

            # self.view().setStyleSheet(self.popup_qss)

            # Force update
            # self.view().update()
            # self.view().installEventFilter(self)



        # Make the popup a frameless popup and allow transparent background on the window.
        # On Windows this generally works; on some Linux setups true transparency may be
        # limited — but we don't require transparency, because the view draws the background.
        flags = popup.windowFlags()
        popup.setWindowFlags(flags | Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        # popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # popup.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # self.view().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        popup.resize(self.width(), popup.height() + 2*  COMBOBOX_RADIUS)
        # popup.resize(self.width(), popup.height())
        if self.variant:
            popup.move(self.mapToGlobal(QPoint(0, self.height() - 1)))
        # popup.move(self.mapToGlobal(QPoint(0, self.height() + COMBOBOX_PADDING)))

        # Ensure popup has no default background painted
        # popup.setStyleSheet("QFrame { background: transparent; border: none; }")
        # popup.setStyleSheet(self.popup_qss)


        # Make the view fill the popup client rect exactly
        # self.view().setGeometry(0, 0, popup.width(), popup.height())
        # self.view().viewport().update()
        # self.view().update()

        self.can_hide = False




    def hidePopup(self):
        if not self.can_hide:
            print(f"  ignore hide, allow for next time")
            self.can_hide = True
            return

        print(purple(f"{int(time.time())}  HIDE"))
        # self.view().removeEventFilter(self.view())
        self.counter = 0
        super().hidePopup()


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
                # print(lightgreen(f"{int(time.time())} LE MouseButtonRelease")
                #     ,f"can_hide: {self.can_hide}"
                # )
                # print(f"   can_hide: {self.can_hide}")
                return True


            elif (
                event_type == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                # print(lightgreen(f"{int(time.time())} LE MouseButtonPress"))
                self.lineEdit().deselect()
                if not self.view().isVisible():
                    self.can_hide = False
                    self.showPopup()
                    # print(f" lets open, can't hide now")
                    return True
                return True

            elif event_type == QEvent.Type.HoverLeave:
                # print(yellow(f"{int(time.time())} lineedit: HoverLeave, can_hide: {self.can_hide}"))
                self.can_hide = True

            # else:
            #     print(yellow(f"{int(time.time())} LE:"), event)

        elif watched == self:
            if event_type == QEvent.Type.InputMethodQuery:
                # print(lightcyan(f"{int(time.time())} CB: InputMethodQuery"), event)
                if self.view().isVisible():
                    if self.counter > 1:
                        # print(" hide")
                        self.can_hide = True
                        self.counter = 0
                        self.hidePopup()
                    else:
                        self.counter += 1

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

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    items = [
        "This is a long text you can select if you want",
        "Another item to test a very very very long text to display",
        "Copy me with Ctrl+C you should see some dots in the line",
        "Right-click won't work"
    ]

    bgd = "#323336"

    window = QWidget()
    window.setStyleSheet(f"background-color: {bgd}; color: white;")
    p = window.palette()
    p.setColor(window.backgroundRole(), bgd)
    window.setPalette(p)

    main_layout = QGridLayout(window)
    main_layout.setContentsMargins(50,50,50,300)
    main_layout.setSpacing(64)

    qcombobox = QComboBox(window)
    qcombobox.addItems(items)

    hcombobox = HComboBox(window, bgd=bgd)
    hcombobox.addItems(items)

    main_layout.addWidget(qcombobox, 0, 0, 1, 1)
    main_layout.addWidget(hcombobox, 0, 1, 1, 1)

    window.show()
    sys.exit(app.exec())
