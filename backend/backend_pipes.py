import asyncio
import json
import logging
import os
import signal
import sys
import time
import traceback
from multiprocessing import Process, Queue

from hutils import lightgreen


# log = logging.getLogger('Backend')
# logger.setLevel(logging.INFO)
# handler = logging.StreamHandler(sys.stderr)
# formatter = logging.Formatter('BACKEND LOG: %(levelname)s: %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)



if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HEARTBEAT_TIMEOUT = 12.0



def run_long_job(filepath, settings, q_out):
    """Blocking long-running function (executed in separate process)."""
    try:
        duration = settings.get("duration", 10)
        start = time.time()
        logging.info(f"Worker: starting job on {filepath} for {duration}s")
        end = start + duration
        # Simulate CPU-bound work
        while time.time() < end:
            _ = sum(i*i for i in range(2000))
        q_out.put({"status": "ok", "result": {"file": filepath, "elapsed": time.time() - start}})
    except Exception:
        q_out.put({"status": "error", "error": traceback.format_exc()})



async def send_stdout(obj):
    """Send JSON message to stdout."""
    try:
        line = json.dumps(obj, separators=(",", ":")) + "\n"
        sys.stdout.write(line)
        await asyncio.to_thread(sys.stdout.flush)
    except Exception:
        logging.exception("Failed to send JSON to stdout")


async def watch_worker(task_id, proc, q_out):
    """Async watcher for a multiprocessing worker."""
    while True:
        if not proc.is_alive():
            # Process ended, get result
            try:
                if not q_out.empty():
                    out = q_out.get_nowait()
                    await send_stdout({"type": "result", "id": task_id, **out})
                else:
                    await send_stdout({"type": "result", "id": task_id,
                                       "status": "error", "error": "worker died"})
            except Exception as e:
                await send_stdout({"type": "result", "id": task_id, "status": "error", "error": str(e)})
            return
        await asyncio.sleep(0.5)


async def heartbeat_monitor(last_ping_func, stop_event):
    """Monitor for missing heartbeats."""
    while not stop_event.is_set():
        await asyncio.sleep(1)
        if time.time() - last_ping_func() > HEARTBEAT_TIMEOUT:
            logging.error("No heartbeat for %.1fs, exiting", time.time() - last_ping_func())
            os._exit(1)



async def read_stdin_lines():
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        yield line


async def main():
    logging.info("Asyncio backend starting (stdin/stdout mode)")

    task_proc = None
    task_queue = None
    last_ping = time.time()
    stop_event = asyncio.Event()

    # Heartbeat
    asyncio.create_task(heartbeat_monitor(lambda: last_ping, stop_event))

    # Continuously read stdin
    async for line in read_stdin_lines():
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            logging.error("Invalid JSON: %s", line)
            continue

        cmd = msg.get("cmd")
        if cmd == "heartbeat":
            last_ping = time.time()
            await send_stdout({"type": "pong"})

        elif cmd == "start_task":
            if task_proc and task_proc.is_alive():
                await send_stdout({
                    "type": "result",
                    "id": msg.get("id"),
                    "status": "error",
                    "error": "another task already running"
                })
                continue

            filepath = msg.get("filepath")
            settings = msg.get("settings", {})
            task_queue = Queue()
            task_proc = Process(target=run_long_job, args=(filepath, settings, task_queue))
            task_proc.start()
            await send_stdout({"type": "info", "message": f"task_started id={msg.get('id')}"})
            asyncio.create_task(watch_worker(msg.get("id"), task_proc, task_queue))
            print(lightgreen("started"))

        elif cmd == "kill_task":
            if task_proc and task_proc.is_alive():
                logging.info("Killing worker process")
                task_proc.terminate()
                await send_stdout({"type": "info", "message": "task killed"})
            else:
                await send_stdout({"type": "info", "message": "no active task"})

        elif cmd == "quit":
            logging.info("Quit command received")
            stop_event.set()
            if task_proc and task_proc.is_alive():
                task_proc.terminate()
            await send_stdout({"type": "info", "message": "bye"})
            break
        else:
            await send_stdout({"type": "error", "message": f"unknown command {cmd}"})

    logging.info("Backend shutting down")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        # Use asyncio.run() which handles loop creation and execution
        # Pass main_loop without the 'loop' argument, as asyncio.run() manages the loop
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Uncaught exception in main process: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Backend shutdown complete.")
