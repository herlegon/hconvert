import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QPushButton, QTextEdit, QLabel, QLineEdit, 
                                QFileDialog, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt
from controller import BackendController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Async Backend Application")
        self.setMinimumSize(800, 600)
        
        # Initialize controller
        self.controller = BackendController()
        self.controller.backend_output.connect(self.on_backend_output)
        self.controller.backend_log.connect(self.on_backend_log)
        self.controller.backend_error.connect(self.on_backend_error)
        self.controller.backend_died.connect(self.on_backend_died)
        self.controller.task_completed.connect(self.on_task_completed)
        
        self.setup_ui()
        
        # Start the controller thread
        self.controller.start()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # File selection
        file_layout = QVBoxLayout()
        self.file_label = QLabel("No file selected")
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(QLabel("Input File:"))
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_file_btn)
        layout.addLayout(file_layout)
        
        # Conversion settings
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("Conversion Settings:"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(75)
        settings_layout.addWidget(QLabel("Quality:"))
        settings_layout.addWidget(self.quality_spin)
        layout.addLayout(settings_layout)
        
        # Control buttons
        button_layout = QVBoxLayout()
        self.start_btn = QPushButton("Start Conversion")
        self.start_btn.clicked.connect(self.start_conversion)
        self.start_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("Stop Current Task")
        self.stop_btn.clicked.connect(self.stop_task)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)
        
        # Output display
        layout.addWidget(QLabel("Backend Output:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # Log display
        layout.addWidget(QLabel("Backend Logs:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        self.selected_file = None
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(file_path)
            self.start_btn.setEnabled(True)
    
    def start_conversion(self):
        if not self.selected_file:
            return
        
        settings = {
            "quality": self.quality_spin.value()
        }
        
        self.controller.send_conversion_command(self.selected_file, settings)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.output_text.append("\n--- Starting conversion ---")
    
    def stop_task(self):
        self.controller.send_kill_task_command()
        self.stop_btn.setEnabled(False)
        self.output_text.append("\n--- Stopping task ---")
    
    def on_backend_output(self, data):
        """Handle structured output from backend"""
        self.output_text.append(f"Result: {json.dumps(data, indent=2)}")
    
    def on_backend_log(self, message):
        """Handle log messages from backend"""
        self.log_text.append(message)
    
    def on_backend_error(self, error):
        """Handle error messages from backend"""
        self.log_text.append(f"ERROR: {error}")
        QMessageBox.warning(self, "Backend Error", f"Backend error: {error}")
    
    def on_backend_died(self):
        """Handle backend process death"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.output_text.append("\n!!! Backend process died !!!")
        
        reply = QMessageBox.question(
            self, "Backend Died", 
            "Backend process is not responding. Restart it?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.controller.restart_backend()
            self.start_btn.setEnabled(bool(self.selected_file))
    
    def on_task_completed(self):
        """Handle task completion"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def closeEvent(self, event):
        """Clean shutdown"""
        self.controller.stop()
        self.controller.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())