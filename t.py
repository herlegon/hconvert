import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QToolButton, QMenu, QHBoxLayout,QLineEdit
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeySequence, QCursor, QAction

class ReadOnlyComboBox(QWidget):
    """ComboBox replacement: selectable text, read-only, dropdown works, no blinking cursor."""
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self.current_index = 0

        # Horizontal layout: line edit + arrow button
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Display line edit (read-only, selectable)
        self.line_edit = QLineEdit(self)
        self.line_edit.setReadOnly(True)  # prevent typing
        self.line_edit.setText(self.items[0] if self.items else "")
        self.line_edit.setCursor(Qt.ArrowCursor)  # hide blinking I-beam
        self.line_edit.setContextMenuPolicy(Qt.NoContextMenu)  # block right-click menu
        self.line_edit.installEventFilter(self)
        layout.addWidget(self.line_edit)

        # Dropdown arrow button
        self.button = QToolButton(self)
        self.button.setText("▼")
        self.button.setCursor(Qt.ArrowCursor)
        self.button.setPopupMode(QToolButton.InstantPopup)
        layout.addWidget(self.button)

        # Menu for dropdown
        self.menu = QMenu(self)
        self.button.setMenu(self.menu)
        for i, item in enumerate(self.items):
            act = QAction(item, self)
            act.triggered.connect(lambda checked=False, idx=i: self.set_current_index(idx))
            self.menu.addAction(act)

        self.setFocusProxy(self.line_edit)  # forward focus to line edit

    def set_current_index(self, idx: int):
        if 0 <= idx < len(self.items):
            self.current_index = idx
            self.line_edit.setText(self.items[idx])

    def currentText(self):
        return self.line_edit.text()

    def eventFilter(self, obj, event):
        if obj is self.line_edit and event.type() == QEvent.KeyPress:
            ke = event
            # Ctrl+C: copy selected text, fallback to full text
            if ke.matches(QKeySequence.Copy):
                selected_text = self.line_edit.selectedText()
                if not selected_text:
                    selected_text = self.line_edit.text()
                QApplication.clipboard().setText(selected_text)
                return True

            # allow navigation keys
            if ke.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End,
                            Qt.Key_Tab, Qt.Key_Backtab):
                return False

            # block all other keys (typing, delete, paste)
            return True

        return super().eventFilter(obj, event)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    vlayout = QVBoxLayout(window)
    vlayout.addWidget(QLabel("Selectable Read-Only Combo Box Test"))

    combo = ReadOnlyComboBox(items=["model1.onnx", "model2.pth", "model3.trt"])
    vlayout.addWidget(combo)

    window.show()
    sys.exit(app.exec())
