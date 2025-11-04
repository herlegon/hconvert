#!/usr/bin/env python3
# backend.py
import sys
import json
import time
import logging
import traceback
from multiprocessing import Process, Queue
from threading import Thread, Event

# Configure logging to stderr
logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

HEARTBEAT_TIMEOUT = 12.0  # seconds: if no heartbeat ping from frontend -> exit

def long_running_uninterruptible(filepath, settings):
    """
    Example "uninterruptible" job.
    Replace with your real function. This runs in a separate process so
    the parent can terminate it immediately if needed.
    """
    # Simulate heavy CPU or blocking code
    # NOTE: This function does not check for interrupts - that's why it's run in another process.
    t0 = time.time()
    # Example heavy work: busy loop for N seconds (replace with real work)
    duration = settings.get("duration", 10)
    logging.info(f"Worker: starting heavy work on {filepath} for ~{duration}s")
    end = time.time() + duration
    # Busy loop to simulate uninterruptible task
    while time.time() < end:
        # do heavy work...
        _ = sum(i*i for i in range(2000))
    logging.info("Worker: finished")
    return {"processed": filepath, "elapsed": time.time() - t0}

def worker_process_main(q_in: Queue, q_out: Queue):
    """
    Child worker main (used if you prefer to start a fresh Python process from code).
    Not required for Process(target=...), but kept here for reference.
    """
    pass

class Backend:
    def __init__(self):
        self.last_ping = time.time()
        self.task_proc = None      # multiprocessing.Process for the long running task
        self.task_queue = None     # Queue to receive result from worker
        self.stop_event = Event()
        # Start the stdin reader
        self.stdin_thread = Thread(target=self._stdin_reader, daemon=True)
        self.stdin_thread.start()
        # Start the heartbeat monitor
        self.hb_thread = Thread(target=self._heartbeat_monitor, daemon=True)
        self.hb_thread.start()

    def _stdin_reader(self):
        for raw in sys.stdin:
            raw = raw.strip()
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except Exception:
                logging.exception("Failed parsing JSON from stdin")
                continue
            try:
                self.handle_message(msg)
            except Exception:
                logging.exception("Error handling message")

    def _heartbeat_monitor(self):
        while not self.stop_event.is_set():
            now = time.time()
            if now - self.last_ping > HEARTBEAT_TIMEOUT:
                logging.error("No heartbeat received for %.1fs. Exiting.", now - self.last_ping)
                # flush any logs and exit
                sys.stderr.flush()
                sys.stdout.flush()
                # Try to clean up worker
                self._terminate_worker()
                # Exit process
                os._exit(1)
            time.sleep(1.0)

    def handle_message(self, msg):
        cmd = msg.get("cmd")
        if cmd == "heartbeat":
            self.last_ping = time.time()
            self._send_stdout({"type": "pong"})
            logging.debug("Received heartbeat, sent pong.")
        elif cmd == "start_task":
            task_id = msg.get("id")
            filepath = msg.get("filepath")
            settings = msg.get("settings", {})
            self._start_task(task_id, filepath, settings)
        elif cmd == "kill_task":
            self._terminate_worker()
            self._send_stdout({"type": "info", "message": "task killed"})
        elif cmd == "quit":
            logging.info("Quit command received. Shutting down.")
            self._terminate_worker()
            self._send_stdout({"type": "info", "message": "exiting"})
            sys.exit(0)
        else:
            logging.warning("Unknown command: %r", cmd)

    def _start_task(self, task_id, filepath, settings):
        if self.task_proc is not None and self.task_proc.is_alive():
            self._send_stdout({"type":"result","id":task_id,"status":"error","error":"another task is running"})
            return
        self.task_queue = Queue()
        def target(q_out, filepath, settings):
            try:
                res = long_running_uninterruptible(filepath, settings)
                q_out.put({"status":"ok","result":res})
            except Exception:
                tb = traceback.format_exc()
                q_out.put({"status":"error","error":tb})
        self.task_proc = Process(target=target, args=(self.task_queue, filepath, settings))
        self.task_proc.start()
        self._send_stdout({"type":"info","message":f"task_started id={task_id}"})
        # Start a watcher thread that will send result to stdout when ready
        Thread(target=self._watch_task, args=(task_id,), daemon=True).start()

    def _watch_task(self, task_id):
        if self.task_queue is None:
            return
        # Wait for result put by worker, or for process death
        while True:
            if self.task_proc is None:
                return
            if not self.task_proc.is_alive():
                # if child died without putting result, send error
                try:
                    # attempt to get any queued result non-blocking
                    if not self.task_queue.empty():
                        out = self.task_queue.get_nowait()
                        self._send_stdout({"type":"result","id":task_id, **out})
                    else:
                        self._send_stdout({"type":"result","id":task_id,"status":"error","error":"worker died"})
                except Exception:
                    self._send_stdout({"type":"result","id":task_id,"status":"error","error":"worker died (exception reading queue)"})
                return
            try:
                # block until a result is available
                out = self.task_queue.get(timeout=0.5)
                self._send_stdout({"type":"result","id":task_id, **out})
                return
            except Exception:
                # loop, continue waiting
                pass

    def _terminate_worker(self):
        if self.task_proc is not None and self.task_proc.is_alive():
            logging.info("Terminating worker process pid=%s", getattr(self.task_proc, "pid", "?"))
            try:
                self.task_proc.terminate()
                self.task_proc.join(timeout=2.0)
            except Exception:
                logging.exception("Error terminating worker")
        self.task_proc = None
        self.task_queue = None

    def _send_stdout(self, obj):
        try:
            sys.stdout.write(json.dumps(obj, separators=(",",":")) + "\n")
            sys.stdout.flush()
        except Exception:
            logging.exception("Failed to write to stdout")

if __name__ == "__main__":
    import os
    try:
        b = Backend()
        # Keep main thread alive while background threads run
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt -> exiting")
    except Exception:
        logging.exception("Uncaught exception in backend main")
        # also print traceback to stderr (logging already does)
        sys.exit(1)
