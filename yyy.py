# test_combo_style.py
import sys
from PySide6.QtWidgets import QApplication, QComboBox, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class TestCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Important: make editable first so lineEdit() exists
        self.setEditable(True)
        le = self.lineEdit()
        le.setObjectName("comboLineEdit")
        le.setReadOnly(True)


        # direct styling on the lineEdit (most reliable)
        le.setStyleSheet(f"""
            color: blue;
            background-color: green;
                         background:red;
            padding-right: 10px;
            border: none;
        """)

        # optional: still set combobox stylesheet for other parts
        self.setStyleSheet("""
            QComboBox { color: yellow; background: #1E1E1E; border: 1px solid gray; padding-left: 8px; }
            QComboBox::drop-down { width: 0px; }
        """)

        # Force polish/unpolish to ensure the line edit picks up the style
        le.style().unpolish(le)
        le.style().polish(le)
        le.update()

        # add some items
        self.addItems(["short text", "a very very long text that should elide"])


        print("lineEdit exists:", bool(self.lineEdit()))
        print("lineEdit objectName:", self.lineEdit().objectName())
        print("lineEdit stylesheet (direct):", repr(self.lineEdit().styleSheet()))
        print("combo stylesheet:", repr(self.styleSheet()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    l = QVBoxLayout(w)
    c = TestCombo()
    l.addWidget(c)
    w.show()


    sys.exit(app.exec())
