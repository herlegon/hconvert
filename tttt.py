
import os
from pathlib import Path
import signal
import sys
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
    Signal,
    QSize,
    QTime,
    QUrl,
    QObject,
    Qt,
    QAbstractItemModel,
    QPersistentModelIndex,
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
    QPalette,
    QPixmap,
    QRadialGradient,
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
    QHideEvent,QFontMetrics,
)
from PySide6.QtWidgets import (
    QStyle,
    QApplication,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
    QFileDialog,
    QLabel,
    QCompleter,
    QAbstractItemDelegate,
    QStyleOptionComboBox,
    QAbstractItemView,
    QLineEdit,
        QVBoxLayout,

)

from hutils import parent_directory, lightgreen

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
COMBOBOX_RADIUS = 4
COMBOBOX_PADDING = 12



class HComboBox(QComboBox):
    signal_f_selected = Signal(str)


    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # self.dd_label = QLabel()
        # self.dd_label.setFixedSize(24,24)
        # self.dd_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.main_layout.addWidget(self.dd_label)
        # self.dd_label.setStyleSheet("background-color: red;")
        self.arrow_padding = 6


        # Hidden arrow button
        self.button = QPushButton(self)
        self.button.setFixedSize(24, 24)
        self.button.setStyleSheet("background-color: red;")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setFocusPolicy(Qt.NoFocus)
        # self.button.setStyleSheet("border: none; background: transparent;")
        self.main_layout.addWidget(self.button)

        self.setHeight(COMBOBOX_HEIGHT, COMBOBOX_RADIUS)
        self.setFixedWidth(230)
        self.setAcceptDrops(True)
        self.setEditable(True)

        self.lineEdit().setReadOnly(True)
        # self.lineEdit().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lineEdit().setTextMargins(0, 0, COMBOBOX_PADDING + COMBOBOX_HEIGHT - 2 * COMBOBOX_RADIUS, 0)  # Add right margin for the icon space

        self.lineEdit().setCursorPosition(0)
        # self.lineEdit().setCursor(Qt.CursorShape.ArrowCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.lineEdit().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.lineEdit().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


        self.load_dd_icon("keyboard_arrow_down_FILL0_wght500_GRAD0_opsz24.png")

        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        )

        self._update_stylesheet()

        self.is_popup_opened = False
        self.lineEdit().installEventFilter(self)
        # self.installEventFilter(self)

        self.button.raise_()  # ensure it's on top
        self.update_button_position()
        # self.combo.resizeEvent = self.on_combo_resize
        self.setLayout(self.main_layout)


    def on_combo_resize(self, event):
        self.update_button_position()
        return QComboBox.resizeEvent(self.combo, event)

    def update_button_position(self):
        # position button on the right of combo
        combo_rect = self.rect()
        x = combo_rect.width() - self.button.width()
        y = (combo_rect.height() - self.button.height()) // 2
        self.button.move(x, y)


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

    def _update_stylesheet(self):
        # Calculate right padding to reserve space for arrow
        arrow_space = self.dd_width + COMBOBOX_PADDING

        stylesheet = """
            QComboBox {{
                color: white;
                padding-left: {padding}px;
                /* padding-right: {arrow_space}px; */
                border: 1px solid gray;
                border-radius: {radius}px;
                background-color: {bgd};
            }}

            QComboBox:hover {{
                border: 1px solid green;
            }}

            QComboBox::down-arrow {{
                width: 0px;
            }}

            QComboBox QAbstractItemView {{
                background: {bgd};
                selection-background-color: lightgray;
                border-radius: {radius}px;
                background-color: orange;
            }}

            QComboBox::drop-down {{
                width: 0px;
            }}

            /* Style the embedded QLineEdit */
            /*
            QComboBox QLineEdit {{
                color: blue;
                background-color: green;
                background: green;
                padding-right: {arrow_space}px;
                border: none;
            }}
            QComboBox QLineEdit:read-only {{
                color: blue;
                background: green;
                background-color: green;
                padding-right: {arrow_space}px;
                border: none;
            }}
            */
        """.format(
            name=self.objectName(),
            combobox_height=COMBOBOX_HEIGHT - COMBOBOX_RADIUS,
            margin=COMBOBOX_RADIUS,
            padding=COMBOBOX_PADDING,
            arrow_space=arrow_space,
            radius=COMBOBOX_RADIUS,
            list_margin=COMBOBOX_RADIUS * 4,
            dd_margin=0,
            bgd="#1E1E1E",
            popup_width=self.width(),
        )
        self.setStyleSheet(stylesheet)

        self.lineEdit().setStyleSheet("color: blue; background: green;")

        self.view().setStyleSheet("""
            QListView {{
                background-color: {bgd};
                border: 1px solid gray;
                border-radius: {radius}px;
                margin-top: 0px;
                padding-top: {radius}px;
                padding-bottom: {radius}px;
                padding-left: {padding}px;
                show-decoration-selected: 1;
            }}

            QListView::item {{
                margin-right: {padding_right}px;
                color: white;
            }}

            QListView::item:selected {{
                background: rgb(127,127,127);
                color: #1E1E1E;
                border-radius: {radius}px;
            }}
        """.format(
            name=self.objectName(),
            combobox_height=COMBOBOX_HEIGHT - COMBOBOX_RADIUS,
            margin=COMBOBOX_RADIUS,
            radius=COMBOBOX_RADIUS,
            padding=COMBOBOX_PADDING,
            padding_right=COMBOBOX_PADDING + COMBOBOX_RADIUS,
            list_margin=COMBOBOX_RADIUS * 4,
            dd_margin=0,
            bgd="#1E1E1E",
            popup_width=self.width(),
        ))

        # self.lineEdit().setStyleSheet("""
        #     QLineEdit#comboLineEdit {{
        #         color: blue;
        #         padding-right: {arrow_space}px;
        #         /* background: transparent; */
        #         background-color: green;
        #         border: none;
        #     }}
        #     QLineEdit#comboLineEdit:read-only {{
        #         color: blue;
        #         background-color: green;
        #         padding-right: {arrow_space}px;
        #         margin-left: {arrow_space}px;
        #     }}
        # """.format(arrow_space=2))


        # try:
        #     self.main_layout.removeWidget(self.dd_label)
        # except:
        #     pass
        # if self.dd_pixmap is not None:
        #     self.main_layout.insertWidget(0, self.dd_label)

    # def showPopup(self) -> None:
    #     print("show popup")
    #     return super().showPopup()

    # def hidePopup(self) -> None:
    #     print("hide popup")
    #     if not self.is_popup_opened:
    #         return super().hidePopup()
    #     else:
    #         print(f"  discard")


    def eventFilter(self, obj, event: QEvent):
        if obj is self.lineEdit() and isinstance(event, QMouseEvent):

            if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
                print("\npressed")
                # Compute arrow rect
                # arrow rectangle
                arrow_rect = QRect(
                    self.width() - self.dd_width - self.arrow_padding,
                    0,
                    self.dd_width + self.arrow_padding,
                    self.height()
                )
                if arrow_rect.contains(event.position().toPoint()):  # PySide6: event.position() is QPointF
                    if not self.view().isVisible():
                        self.showPopup()
                    return True  # consume the event

        #     elif event.type() == QEvent.Type.HoverEnter:
        #         # print(f"over enter {self.view().isVisible()}")
        #         # if not self.pop
        #         #     self.showPopup()
        #         return True

        #     elif event.type() == QEvent.Type.MouseButtonRelease:
        #         print("release")
        #         return True

        #     elif event.type() not in (QEvent.Type.HoverMove, QEvent.Type.MouseMove,):
        #         print(event)
        # else:
        #     if event.type() in (
        #         QEvent.Type.FocusAboutToChange,
        #         QEvent.Type.que
        #     ):
        #         # self.is_popup_opened  = True
        #         return True
        #     if event.type() not in (QEvent.Type.HoverMove, QEvent.Type.MouseMove,):
        #         print(lightgreen(event))

        return super().eventFilter(obj, event)



    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)
        painter: QPainter = QPainter(self)
        x = self.width() - self.dd_width - COMBOBOX_PADDING
        y = int(self.height() - self.dd_pixmap.height())/2
        painter.drawPixmap(QPoint(x, y), self.dd_pixmap)

    # Option 1
    # def paintEvent(self, e: QPaintEvent) -> None:
    #     super().paintEvent(e)

    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.SmoothPixmapTransform)

    #     # Compute position (right aligned)
    #     x = self.width() - self.dd_pixmap.width() - COMBOBOX_PADDING
    #     y = (self.height() - self.dd_pixmap.height()) // 2

    #     # Fill background behind arrow to mask long text overlap
    #     painter.fillRect(
    #         QRect(x - 2, 0, self.dd_pixmap.width() + 4, self.height()),
    #         self.palette().base()
    #     )

    #     # Draw the dropdown arrow pixmap
    #     painter.drawPixmap(QPoint(x, y), self.dd_pixmap)

    # Option 3
    # def paintEvent(self, event):
    #     opt = QStyleOptionComboBox()
    #     self.initStyleOption(opt)

    #     painter = QPainter(self)
    #     self.style().drawComplexControl(QStyle.CC_ComboBox, opt, painter, self)
    #     self.style().drawControl(QStyle.CE_ComboBoxLabel, opt, painter, self)

    #     # Draw your icon
    #     x = self.width() - self.dd_pixmap.width() - COMBOBOX_PADDING
    #     y = (self.height() - self.dd_pixmap.height()) // 2
    #     painter.drawPixmap(QPoint(x, y), self.dd_pixmap)


    # def paintEvent(self, event: QPaintEvent):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     fm = QFontMetrics(self.font())


    #     # Draw background and border manually
    #     opt = QStyleOptionComboBox()
    #     self.initStyleOption(opt)
    #     opt.currentText = ""  # prevent style from drawing text
    #     self.style().drawComplexControl(QStyle.ComplexControl.CC_ComboBox, opt, painter, self)
    #     self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, opt, painter, self)


    #     # Draw elided text manually
    #     fm = QFontMetrics(self.font())
    #     available_width = self.width() - self.dd_pixmap.width() - (COMBOBOX_PADDING * 2)
    #     text_rect = QRect(COMBOBOX_PADDING, 0, available_width, self.height())
    #     text = self.currentText()
    #     elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, available_width - 8)

    #     painter.setPen(Qt.GlobalColor.white)
    #     painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided)

    #     # Draw dropdown arrow
    #     x = self.width() - self.dd_pixmap.width() - COMBOBOX_PADDING
    #     y = (self.height() - self.dd_pixmap.height()) // 2
    #     painter.drawPixmap(QPoint(x, y), self.dd_pixmap)



        # # Calculate text area (exclude arrow zone)
        # available_width = self.width() - self.dd_pixmap.width() - (COMBOBOX_PADDING * 2)
        # text_rect = QRect(COMBOBOX_PADDING, 0, available_width, self.height())

        # # Get text and elide it to fit
        # text = self.currentText()
        # elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, available_width - 8)

        # painter.setPen(Qt.GlobalColor.white)
        # painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided)

        # # Draw dropdown arrow
        # x = self.width() - self.dd_pixmap.width() - COMBOBOX_PADDING
        # y = (self.height() - self.dd_pixmap.height()) // 2
        # painter.drawPixmap(QPoint(x, y), self.dd_pixmap)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    window = QWidget()
    vlayout = QVBoxLayout(window)
    vlayout.addWidget(QLabel("Selectable Read-Only Combo Box Test"))

    combo = HComboBox()
    combo.addItems([
        "This is a long text you can select",
        "Another item to test a very very very long text to display",
        "Copy me with Ctrl+C you should see some dots in the line",
        "Right-click won't work"
    ])

    # Get line edit
    line_edit = combo.lineEdit()

    # Disable context menu
    line_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
    combo.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    vlayout.addWidget(combo)

    window.show()
    sys.exit(app.exec())
