
import os
from pathlib import Path
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
    QHideEvent,
)
from PySide6.QtWidgets import (
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
        self.setObjectName("open_dialog")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.dd_label = QLabel()
        self.dd_label.setFixedSize(24,24)
        self.main_layout.addWidget(self.dd_label)

        self.setHeight(COMBOBOX_HEIGHT, COMBOBOX_RADIUS)
        self.setFixedWidth(230)
        self.setAcceptDrops(True)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.load_dd_icon("keyboard_arrow_down_FILL0_wght500_GRAD0_opsz24.png")

        # self.button_browse = QPushButton(self)
        # self.button_browse.setSizePolicy(
        #     QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # )
        # self.button_browse.setMaximumSize(QSize(25, COMBOBOX_HEIGHT-4))

        # layout.addWidget(self.button_browse)

        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtCurrent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        )

        self._update_stylesheet()
        self.is_activated: bool = False

        # self.button_browse.clicked.connect(self.activated)
        # self.mouseReleased.connect(self.activated)
        # self.currentIndexChanged.connect(self.selected)
        self.installEventFilter(self)
        self.lineEdit().installEventFilter(self)
        # self.combobox_path.mouseReleased.connect(self.picker_event)
        # self.combobox_path.activated.connect(self.activated)
        # activated                # activated(int)
        # currentIndexChanged      # currentIndexChanged(int)
        # currentTextChanged       # currentTextChanged(QString)
        # editTextChanged          # editTextChanged(QString)
        # highlighted              # highlighted(int)
        # textActivated            # textActivated(QString)
        # textHighlighted          # textHighlighted(QString)

        self.setLayout(self.main_layout)



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
        stylesheet = """
        /*
            #{name} {{
                border: 1px solid red;
                border-radius: {radius}px;
                background-color: {bgd};
                color: white;
            }}
        */
            QComboBox {{
                color: white;
                /* margin-left: {padding}px; */
                padding-left: {padding}px;

                 border: 1px solid gray;
                border-radius: {radius}px;
                background-color: {bgd};
                /* padding: 8px; */
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
                /* color: white; */
                /* border-top: 30px solid; */
                /* border-color: transparent;*/
                border-radius: {radius}px;
                /*width: {popup_width}px; */
                background-color: orange;
            }}

            QComboBox::drop-down {{
                width: 0px;
            }}

        """.format(
            name=self.objectName(),
            combobox_height=COMBOBOX_HEIGHT-COMBOBOX_RADIUS,
            margin=COMBOBOX_RADIUS,
            padding=COMBOBOX_PADDING,
            radius=COMBOBOX_RADIUS,
            list_margin = COMBOBOX_RADIUS*4,
            dd_margin = 0,
            bgd="#1E1E1E",
            popup_width = self.width(),
        )
        self.setStyleSheet(stylesheet)


        self.view().setStyleSheet(
            """
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
            combobox_height=COMBOBOX_HEIGHT-COMBOBOX_RADIUS,
            margin=COMBOBOX_RADIUS,
            radius=COMBOBOX_RADIUS,
            padding=COMBOBOX_PADDING,
            padding_right=COMBOBOX_PADDING+COMBOBOX_RADIUS,
            list_margin = COMBOBOX_RADIUS*4,
            dd_margin = 0,
            bgd="#1E1E1E",
            popup_width = self.width(),
        )
        )

        self.lineEdit().setStyleSheet(
            """
            QLineEdit {{
                color: white;
            }}
            QLineEdit:read-only {{
                color: white;
            }}
        """)


        try:
            self.main_layout.removeWidget(self.dd_label)
        except:
            pass
        if self.dd_pixmap is not None:
            self.main_layout.insertWidget(0, self.dd_label)


    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        event_type = event.type()
        if isinstance(watched, QLineEdit):
            # print(f"{watched} {event}")
            if event_type == QEvent.Type.MouseButtonRelease:
                # self.showPopup()
                pass

        return super().eventFilter(watched, event)


    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)
        painter: QPainter = QPainter(self)
        x = self.width() - self.dd_width - COMBOBOX_PADDING
        y = int(self.height() - self.dd_pixmap.height())/2

        painter.drawPixmap(
            # QRect(
            #     self.width() - self.dd_width - COMBOBOX_PADDING,
            #     self.radius,
            #     self.dd_height,
            #     self.dd_height),
            QPoint(x, y),
            self.dd_pixmap,
            # QRect(0,0,self.dd_width,self.dd_width)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    vlayout = QVBoxLayout(window)
    vlayout.addWidget(QLabel("Selectable Read-Only Combo Box Test"))

    combo = HComboBox()
    combo.addItems([
        "This is a long text you can select",
        "Another item to test",
        "Copy me with Ctrl+C!",
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
