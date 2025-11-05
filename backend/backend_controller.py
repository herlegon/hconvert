# backend_controller.py
import subprocess
import threading
import json
import time
import sys
import os
from PySide6.QtCore import QObject, Signal

PYTHON_EXEC = sys.executable  # path to python interpreter
BACKEND_SCRIPT = "backend.py"

class BackendController(QObject):
    stdout_message = Signal(dict)   # emitted for JSON results/info from backend stdout
    stderr_line = Signal(str)       # emitted for logging lines from backend stderr
    backend_down = Signal()         # emitted when backend is detected dead and restart failed

    def __init__(self, parent=None, auto_restart=True):
        super().__init__(parent)
        self.proc = None
        self._stdout_thread = None
        self._stderr_thread = None
        self._lock = threading.Lock()
        self._should_run = True
        self._heartbeat_interval = 5.0
        self._pong_received = threading.Event()
        self._auto_restart = auto_restart
        self._start_backend()

        # start heartbeat sender thread
        self._hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._hb_thread.start()

    def _start_backend(self):
        with self._lock:
            if self.proc is not None and self.proc.poll() is None:
                return
            cmd = [PYTHON_EXEC, "-u", BACKEND_SCRIPT]  # -u to unbuffer stdout/stderr
            self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         text=True, bufsize=1)
            self._stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
            self._stdout_thread.start()
            self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self._stderr_thread.start()
            # reset pong flag
            self._pong_received.clear()

    def _read_stdout(self):
        try:
            for raw in self.proc.stdout:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except Exception:
                    # Not JSON? emit as raw info
                    self.stdout_message.emit({"type":"raw","line":raw})
                    continue
                # handle pong specially
                if obj.get("type") == "pong":
                    self._pong_received.set()
                # emit everything to GUI
                self.stdout_message.emit(obj)
        except Exception as e:
            self.stderr_line.emit(f"stdout reader error: {e}")

    def _read_stderr(self):
        try:
            for line in self.proc.stderr:
                self.stderr_line.emit(line.rstrip("\n"))
        except Exception as e:
            # emit error to GUI logger
            self.stderr_line.emit(f"stderr reader error: {e}")

    def send_command(self, obj: dict):
        """Send a JSON command to backend stdin (thread-safe)."""
        with self._lock:
            if self.proc is None or self.proc.poll() is not None:
                raise RuntimeError("Backend not running")
            data = json.dumps(obj, separators=(",",":")) + "\n"
            try:
                self.proc.stdin.write(data)
                self.proc.stdin.flush()
            except Exception as e:
                self.stderr_line.emit(f"Failed to send command: {e}")

    def _heartbeat_loop(self):
        while self._should_run:
            try:
                # send heartbeat
                try:
                    self.send_command({"cmd":"heartbeat"})
                except Exception:
                    # backend not running
                    self._handle_no_pong()
                    time.sleep(self._heartbeat_interval)
                    continue
                # wait for pong for a while
                got = self._pong_received.wait(timeout=3.0)
                if got:
                    self._pong_received.clear()
                else:
                    # no pong: check process alive, try restart
                    self._handle_no_pong()
                time.sleep(self._heartbeat_interval)
            except Exception as e:
                self.stderr_line.emit(f"heartbeat loop error: {e}")
                time.sleep(self._heartbeat_interval)

    def _handle_no_pong(self):
        # Check if process is alive
        with self._lock:
            alive = (self.proc is not None and self.proc.poll() is None)
            if not alive:
                self.stderr_line.emit("Backend not running -> attempt restart")
                if self._auto_restart:
                    try:
                        self._start_backend()
                        self.stderr_line.emit("Backend restarted")
                    except Exception as e:
                        self.stderr_line.emit(f"Failed restarting backend: {e}")
                        self.backend_down.emit()
                else:
                    self.backend_down.emit()
            else:
                # Process is alive but didn't pong: maybe stuck. Try graceful restart:
                self.stderr_line.emit("Backend alive but no pong: terminating and restarting")
                try:
                    self.proc.terminate()
                    # wait briefly
                    time.sleep(1.0)
                    if self.proc.poll() is None:
                        self.proc.kill()
                except Exception as e:
                    self.stderr_line.emit(f"Error terminating stuck backend: {e}")
                # restart
                if self._auto_restart:
                    try:
                        self._start_backend()
                        self.stderr_line.emit("Backend restarted after no-pong")
                    except Exception as e:
                        self.stderr_line.emit(f"Failed restarting backend: {e}")
                        self.backend_down.emit()
                else:
                    self.backend_down.emit()

    def start_task(self, task_id, filepath, settings):
        self.send_command({"cmd":"start_task","id":task_id,"filepath":filepath,"settings":settings})

    def kill_task(self):
        try:
            self.send_command({"cmd":"kill_task"})
        except Exception:
            # If backend not responding, try to kill worker by sending SIGTERM to backend
            with self._lock:
                if self.proc:
                    try:
                        self.proc.terminate()
                    except Exception:
                        pass

    def shutdown(self):
        self._should_run = False
        try:
            self.send_command({"cmd":"quit"})
        except Exception:
            pass
        with self._lock:
            if self.proc:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
