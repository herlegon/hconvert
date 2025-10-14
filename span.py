from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PySide6.QtCore import Qt

app = QApplication([])

widget = QWidget()
layout = QGridLayout(widget)

layout.addWidget(QLabel("R0C0"), 0, 0)
layout.addWidget(QLabel("R1C0"), 1, 0)

merged = QLabel("Merged (col 1, rows 0-1)")
merged.setAlignment(Qt.AlignCenter)
layout.addWidget(merged, 0, 1, 2, 1)  # ⬅️ merge vertically here

layout.addWidget(QLabel("R0C2"), 0, 2)
layout.addWidget(QLabel("R1C2"), 1, 2)

widget.show()
app.exec()
