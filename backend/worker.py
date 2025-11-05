import multiprocessing
import signal
import time
from hutils import yellow
from messages import WorkerCommand, WorkerEvent

def nnlib_worker(cmd_queue: multiprocessing.Queue, event_queue: multiprocessing.Queue):
    """
    Persistent worker for short tasks (<5s).
    """

    while True:
        try:
            cmd: WorkerCommand = cmd_queue.get()
            if cmd.cmd == "shutdown":
                break
            elif cmd.cmd == "parse":
                try:
                    model_path = cmd.payload.get("path")
                    # simulate parsing task
                    for i in range(3):
                        time.sleep(0.5)
                        event_queue.put(WorkerEvent(type="progress", data={"value": (i+1)/3}))
                        event_queue.put(WorkerEvent(type="log", data=f"Parsing step {i+1}/3"))
                    # final result
                    event_queue.put(WorkerEvent(type="result", data={"output": f"parsed_{model_path}"}))
                except Exception as e:
                    event_queue.put(WorkerEvent(type="error", data=str(e)))
        except:
            break
    print(yellow(f"Terminated nnlib_worker"))
