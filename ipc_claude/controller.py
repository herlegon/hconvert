import json
import subprocess
import sys
import time
import threading
from PySide6.QtCore import QThread, Signal


class BackendController(QThread):
    """Controller thread that manages backend process communication"""
    
    backend_output = Signal(dict)  # Structured output from backend
    backend_log = Signal(str)      # Log messages from backend
    backend_error = Signal(str)    # Error messages
    backend_died = Signal()        # Backend process died
    task_completed = Signal()      # Task completed successfully
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.running = False
        self.last_pong = time.time()
        self.heartbeat_timeout = 10  # 10 seconds to account for processing
        self.heartbeat_interval = 5  # Send heartbeat every 5 seconds
        
    def run(self):
        """Main thread loop"""
        self.running = True
        self.start_backend()
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        # Start stdout reader thread
        stdout_thread = threading.Thread(target=self.read_stdout, daemon=True)
        stdout_thread.start()
        
        # Start stderr reader thread
        stderr_thread = threading.Thread(target=self.read_stderr, daemon=True)
        stderr_thread.start()
        
        # Monitor backend health
        while self.running:
            time.sleep(1)
            
            # Check if backend is still alive
            if self.process and self.process.poll() is not None:
                self.backend_error.emit(f"Backend exited with code {self.process.returncode}")
                self.backend_died.emit()
                break
            
            # Check heartbeat timeout
            if time.time() - self.last_pong > self.heartbeat_timeout:
                self.backend_error.emit("Backend heartbeat timeout")
                self.backend_died.emit()
                self.kill_backend()
                break
    
    def start_backend(self):
        """Start the backend process"""
        try:
            self.process = subprocess.Popen(
                [sys.executable, "backend.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.last_pong = time.time()
            self.backend_log.emit("Backend started successfully")
        except Exception as e:
            self.backend_error.emit(f"Failed to start backend: {e}")
            self.backend_died.emit()
    
    def heartbeat_loop(self):
        """Send periodic heartbeats to backend"""
        while self.running and self.process:
            try:
                self.send_command({"command": "heartbeat"})
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                self.backend_error.emit(f"Heartbeat error: {e}")
                break
    
    def read_stdout(self):
        """Read and process stdout from backend"""
        while self.running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Handle different message types
                    msg_type = data.get("type")
                    
                    if msg_type == "pong":
                        self.last_pong = time.time()
                    elif msg_type == "result":
                        self.backend_output.emit(data)
                        self.task_completed.emit()
                    elif msg_type == "progress":
                        self.backend_output.emit(data)
                    else:
                        self.backend_output.emit(data)
                        
                except json.JSONDecodeError:
                    self.backend_log.emit(f"Invalid JSON from stdout: {line}")
                    
            except Exception as e:
                self.backend_error.emit(f"Error reading stdout: {e}")
                break
    
    def read_stderr(self):
        """Read and process stderr from backend (logs)"""
        while self.running and self.process:
            try:
                line = self.process.stderr.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.backend_log.emit(line)
                    
            except Exception as e:
                self.backend_error.emit(f"Error reading stderr: {e}")
                break
    
    def send_command(self, command_dict):
        """Send a command to backend via stdin"""
        if not self.process or self.process.poll() is not None:
            return
        
        try:
            json_command = json.dumps(command_dict) + "\n"
            self.process.stdin.write(json_command)
            self.process.stdin.flush()
        except Exception as e:
            self.backend_error.emit(f"Error sending command: {e}")
    
    def send_conversion_command(self, filepath, settings):
        """Send conversion command to backend"""
        command = {
            "command": "convert",
            "filepath": filepath,
            "settings": settings
        }
        self.send_command(command)
    
    def send_kill_task_command(self):
        """Send kill task command to backend"""
        self.send_command({"command": "kill_task"})
    
    def kill_backend(self):
        """Forcefully kill the backend process"""
        if self.process:
            try:
                self.process.kill()
                self.process.wait(timeout=5)
            except:
                pass
            self.process = None
    
    def restart_backend(self):
        """Restart the backend process"""
        self.kill_backend()
        time.sleep(1)
        self.start_backend()
        self.last_pong = time.time()
    
    def stop(self):
        """Stop the controller and backend"""
        self.running = False
        
        # Send quit command
        if self.process and self.process.poll() is None:
            self.send_command({"command": "quit"})
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.kill_backend()
        
        self.kill_backend()