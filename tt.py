from PySide6.QtWidgets import QComboBox, QApplication
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent, QMouseEvent


class ReadOnlyComboBox(QComboBox):
    """
    A read-only combobox that allows:
    - Text selection
    - Copy (Ctrl+C, Ctrl+Insert)
    - Navigation (arrows, home, end)

    Blocks:
    - Text editing
    - Paste
    - Context menu
    - Delete/Backspace
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(True)

        # Get line edit
        line_edit = self.lineEdit()

        # Disable context menu
        line_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # Make read-only but keep selection enabled
        line_edit.setReadOnly(True)

        # Remove focus border/outline (aggressive approach for Linux)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        line_edit.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)

        # Remove all focus indicators
        self.setStyleSheet("""

            QComboBox:focus {
                border: none;
                outline: none;
            }

            QLineEdit:focus {
                border: none;
                outline: none;
            }
        """)


        # Install event filter for keyboard handling
        line_edit.installEventFilter(self)

    def eventFilter(self, obj, event: QEvent):
        """Handle keyboard events on the line edit."""
        if obj is self.lineEdit():
            if event.type() == QEvent.Type.KeyPress:
                return self._handle_key_press(event)

        return super().eventFilter(obj, event)

    def _handle_key_press(self, event: QKeyEvent) -> bool:
        """
        Handle key press events.
        Returns True to block event, False to allow.
        """
        modifiers = event.modifiers()
        key = event.key()

        # Allow Ctrl+C (copy)
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_C:
                self._copy_selected_text()
                return True
            # Ctrl+Insert (Linux alternative for copy)
            if key == Qt.Key.Key_Insert:
                self._copy_selected_text()
                return True

        # Allow Shift+arrows for text selection
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            if key in (Qt.Key.Key_Left, Qt.Key.Key_Right,
                      Qt.Key.Key_Home, Qt.Key.Key_End):
                return False  # Let Qt handle selection

        # Allow plain navigation (no modifiers or Ctrl modifier for word jump)
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right,
                  Qt.Key.Key_Home, Qt.Key.Key_End):
            return False  # Let Qt handle navigation

        # Allow Ctrl+A (select all)
        if (modifiers == Qt.KeyboardModifier.ControlModifier and
            key == Qt.Key.Key_A):
            self.lineEdit().selectAll()
            return True

        # Block everything else (typing, paste, delete, etc.)
        return True

    def _copy_selected_text(self):
        """Manually copy selected text to clipboard."""
        line_edit = self.lineEdit()
        if line_edit.hasSelectedText():
            selected_text = line_edit.selectedText()
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_text)


# Test code
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("ReadOnly ComboBox Test")

            # Create central widget
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)

            # Add label
            layout.addWidget(QLabel("Try to: select text, Ctrl+C, right-click, type"))

            # Add readonly combobox
            combo = ReadOnlyComboBox()
            combo.addItems([
                "This is a long text you can select regregreg reg re gre g",
                "Another item to test",
                "Copy me with Ctrl+C!",
                "Right-click won't work"
            ])
            layout.addWidget(combo)

            # Add normal combobox for comparison
            layout.addWidget(QLabel("\nPaste here to test copy:"))
            normal_combo = QComboBox()
            normal_combo.setEditable(True)
            layout.addWidget(normal_combo)

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
