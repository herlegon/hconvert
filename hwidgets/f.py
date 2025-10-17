import signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QGroupBox,
     QCheckBox, QRadioButton, QComboBox,

)
from PySide6.QtCore import Qt
import sys, os

def apply_stylesheet(app, dark=False):
    with open("hcombobox.qss", "r") as f:
        app.setStyleSheet(f.read())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.setWindowTitle("Fluent-Inspired App")
        self.resize(400, 250)

        layout = QVBoxLayout(self)

        # Example UI
        self.group = QGroupBox("Example Form")
        inner = QVBoxLayout()
        self.input = QLineEdit()
        self.button = QPushButton("Click Me")
        self.status = QLabel("Ready.")
        inner.addWidget(QLabel("Enter something:"))
        inner.addWidget(self.input)
        inner.addWidget(self.button)
        inner.addWidget(self.status)
        self.group.setLayout(inner)

        self.toggle_theme = QPushButton("🌗 Toggle Dark/Light")
        self.toggle_theme.clicked.connect(self.toggle_dark_mode)



        cb1 = QCheckBox("Enable feature")
        cb2 = QCheckBox("Send notifications")
        rb1 = QRadioButton("Option A")
        rb2 = QRadioButton("Option B")

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])

        layout.addWidget(QLabel("Select an option:"))
        layout.addWidget(combo)
        layout.addWidget(cb1)
        layout.addWidget(cb2)
        layout.addWidget(rb1)
        layout.addWidget(rb2)


        layout.addWidget(self.group)
        layout.addWidget(self.toggle_theme)

        # Logic demo
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        text = self.input.text().strip()
        self.status.setText(f"You typed: {text}" if text else "Nothing entered")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        apply_stylesheet(QApplication.instance(), dark=self.dark_mode)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    apply_stylesheet(app, dark=False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
