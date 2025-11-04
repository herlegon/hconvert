import json
import subprocess
import sys
import time
from pathlib import Path
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import QUrl


class Controller(QThread):
    """Controller thread that manages WebSocket connection to backend"""

    # Signals
    backend_ready = Signal()
    backend_disconnected = Signal()
    backend_reconnecting = Signal()
    message_received = Signal(dict)  # Any message from backend
    log_received = Signal(str)       # Log messages
    progress_received = Signal(dict) # Progress updates
    result_received = Signal(dict)   # Task results
    error_received = Signal(str)     # Errors

    def __init__(self):
        super().__init__()
        self.ws = None
        self.backend_process = None
        self.running = False
        self.connected = False
        self.last_pong = time.time()
        self.heartbeat_timeout = 15  # seconds
        self.ws_url = "ws://localhost:8765"
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3

    def run(self):
        """Main controller thread loop"""
        self.running = True
        self.start_backend()

        # Wait a bit for backend to start
        time.sleep(1)

        # Connect to WebSocket
        self.connect_websocket()

        # Start heartbeat monitoring
        while self.running:
            time.sleep(1)

            # Check if backend process is alive
            if self.backend_process and self.backend_process.poll() is not None:
                self.error_received.emit(
                    f"Backend process died with code {self.backend_process.returncode}"
                )
                self.handle_backend_failure()
                continue

            # Check heartbeat timeout
            if self.connected and (time.time() - self.last_pong > self.heartbeat_timeout):
                self.error_received.emit("Backend heartbeat timeout")
                self.handle_backend_failure()
                continue

            # Send heartbeat if connected
            if self.connected:
                self.send_command({"cmd": "ping"})

    def start_backend(self):
        """Start the backend subprocess"""
        try:
            backend_path = Path(__file__).parent.parent / "backend" / "server.py"
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.log_received.emit(f"Backend process started (PID: {self.backend_process.pid})")
        except Exception as e:
            self.error_received.emit(f"Failed to start backend: {e}")

    def connect_websocket(self):
        """Connect to backend WebSocket server"""
        self.ws = QWebSocket()
        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_message)
        self.ws.error.connect(self.on_error)

        self.log_received.emit(f"Connecting to {self.ws_url}...")
        self.ws.open(QUrl(self.ws_url))

    def on_connected(self):
        """Handle WebSocket connection established"""
        self.connected = True
        self.last_pong = time.time()
        self.reconnect_attempts = 0
        self.log_received.emit("Connected to backend")
        self.backend_ready.emit()

    def on_disconnected(self):
        """Handle WebSocket disconnection"""
        was_connected = self.connected
        self.connected = False

        if was_connected and self.running:
            self.log_received.emit("Disconnected from backend")
            self.backend_disconnected.emit()
            self.handle_backend_failure()

    def on_message(self, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            # Update last pong time
            if msg_type == "pong":
                self.last_pong = time.time()

            # Emit specific signals based on message type
            if msg_type == "ready":
                self.backend_ready.emit()
            elif msg_type == "log":
                self.log_received.emit(data.get("message", ""))
            elif msg_type == "progress":
                self.progress_received.emit(data)
            elif msg_type == "result":
                self.result_received.emit(data)
            elif msg_type == "error":
                self.error_received.emit(data.get("message", "Unknown error"))

            # Always emit general message signal
            self.message_received.emit(data)

        except json.JSONDecodeError as e:
            self.error_received.emit(f"Invalid JSON from backend: {e}")
        except Exception as e:
            self.error_received.emit(f"Error processing message: {e}")

    def on_error(self, error_code):
        """Handle WebSocket error"""
        if self.ws:
            error_msg = self.ws.errorString()
            self.log_received.emit(f"WebSocket error: {error_msg}")

    def send_command(self, command_dict):
        """Send command to backend via WebSocket"""
        if not self.connected or not self.ws:
            self.log_received.emit("Cannot send command: not connected")
            return False

        try:
            message = json.dumps(command_dict)
            self.ws.sendTextMessage(message)
            return True
        except Exception as e:
            self.error_received.emit(f"Error sending command: {e}")
            return False

    def send_task(self, task_name, params):
        """Send task command to backend"""
        return self.send_command({
            "cmd": "task",
            "task": task_name,
            "params": params
        })

    def cancel_task(self):
        """Cancel current running task"""
        return self.send_command({"cmd": "cancel"})

    def handle_backend_failure(self):
        """Handle backend failure and attempt recovery"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.error_received.emit(
                f"Failed to reconnect after {self.max_reconnect_attempts} attempts"
            )
            return

        self.reconnect_attempts += 1
        self.backend_reconnecting.emit()
        self.log_received.emit(
            f"Attempting to restart backend (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})..."
        )

        # Kill existing backend
        self.kill_backend()

        # Wait a bit
        time.sleep(2)

        # Restart
        self.start_backend()
        time.sleep(2)
        self.connect_websocket()

    def kill_backend(self):
        """Kill the backend process"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                self.backend_process.wait()
            except:
                pass
            self.backend_process = None

        if self.ws and self.connected:
            self.ws.close()

    def shutdown(self):
        """Graceful shutdown"""
        self.running = False

        # Send shutdown command to backend
        if self.connected:
            self.send_command({"cmd": "shutdown"})
            time.sleep(1)

        # Close WebSocket
        if self.ws:
            self.ws.close()

        # Kill backend process
        self.kill_backend()
