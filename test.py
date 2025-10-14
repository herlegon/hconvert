from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QGroupBox, QPushButton, QLabel, QSizePolicy)
from PySide6.QtCore import QTimer
import sys


class ConversionWidget(QWidget):
    """Widget with multiple groupboxes that can be shown/hidden."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Create three groupboxes with different heights
        self.groupbox1 = QGroupBox("Input Settings")
        self.groupbox1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gb1_layout = QVBoxLayout(self.groupbox1)
        for i in range(3):
            gb1_layout.addWidget(QLabel(f"Input field {i+1}"))

        self.groupbox2 = QGroupBox("Conversion Options")
        self.groupbox2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gb2_layout = QVBoxLayout(self.groupbox2)
        for i in range(6):
            gb2_layout.addWidget(QLabel(f"Option {i+1}"))

        self.groupbox3 = QGroupBox("Output Settings")
        self.groupbox3.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gb3_layout = QVBoxLayout(self.groupbox3)
        for i in range(4):
            gb3_layout.addWidget(QLabel(f"Output field {i+1}"))

        # Add groupboxes to layout
        layout.addWidget(self.groupbox1)
        layout.addWidget(self.groupbox2)
        layout.addWidget(self.groupbox3)
        layout.addStretch()

        # Set size policy to allow vertical shrinking, horizontal expanding
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def toggle_groupbox(self, groupbox: QGroupBox, visible: bool):
        """Show or hide a groupbox and trigger resize."""
        groupbox.setVisible(visible)
        self.adjust_size()

    def adjust_size(self):
        """Adjust widget size based on visible groupboxes."""
        # Update layout to recalculate sizes
        self.updateGeometry()
        self.adjustSize()

        # Notify parent window to resize
        if self.window():
            QTimer.singleShot(0, self.window().adjust_to_content)


class MainWindow(QMainWindow):
    """Main window that resizes based on content."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Resize Example")
        self.setup_ui()

    def setup_ui(self):
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Create conversion widget
        self.conversion_widget = ConversionWidget()
        main_layout.addWidget(self.conversion_widget)

        # Add control buttons
        controls_layout = QVBoxLayout()

        self.btn1 = QPushButton("Toggle Input Settings")
        self.btn1.setCheckable(True)
        self.btn1.setChecked(True)
        self.btn1.clicked.connect(lambda: self.toggle_groupbox(0))

        self.btn2 = QPushButton("Toggle Conversion Options")
        self.btn2.setCheckable(True)
        self.btn2.setChecked(True)
        self.btn2.clicked.connect(lambda: self.toggle_groupbox(1))

        self.btn3 = QPushButton("Toggle Output Settings")
        self.btn3.setCheckable(True)
        self.btn3.setChecked(True)
        self.btn3.clicked.connect(lambda: self.toggle_groupbox(2))

        controls_layout.addWidget(self.btn1)
        controls_layout.addWidget(self.btn2)
        controls_layout.addWidget(self.btn3)

        main_layout.addLayout(controls_layout)

        # Set initial size
        self.adjust_to_content()

    def toggle_groupbox(self, index: int):
        """Toggle visibility of a groupbox."""
        groupboxes = [
            self.conversion_widget.groupbox1,
            self.conversion_widget.groupbox2,
            self.conversion_widget.groupbox3
        ]
        buttons = [self.btn1, self.btn2, self.btn3]

        if 0 <= index < len(groupboxes):
            visible = buttons[index].isChecked()
            self.conversion_widget.toggle_groupbox(groupboxes[index], visible)

    def adjust_to_content(self):
        """Adjust main window size to fit content."""
        # Save current width
        current_width = self.width()

        # Reset minimum size to allow shrinking
        self.setMinimumSize(0, 0)

        # Force layout to recalculate
        self.centralWidget().adjustSize()

        # Calculate desired size
        content_size = self.centralWidget().sizeHint()

        # Account for window frame and margins
        new_height = content_size.height() + self.menuBar().height()

        # Set minimum height to content height
        self.setMinimumHeight(new_height)

        # Resize window to minimum height, keeping width unchanged
        self.resize(current_width, new_height)

        # Reset minimum to allow future resizing by user
        QTimer.singleShot(100, lambda: self.setMinimumSize(0, 0))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
