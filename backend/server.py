import asyncio
import json
import multiprocessing
import time
import psutil
import websockets
from messages import WorkerCommand, WorkerEvent
from worker import nnlib_worker

# Persistent small-task worker
small_cmd_queue = multiprocessing.Queue()
small_event_queue = multiprocessing.Queue()
small_worker = multiprocessing.Process(target=nnlib_worker, args=(small_cmd_queue, small_event_queue))
small_worker.start()

# Heavy task (spawn on demand)
heavy_process = None
heavy_cmd_queue = None
heavy_event_queue = None

async def send_json(ws, data: dict):
    await ws.send(json.dumps(data))

async def forward_events(ws, event_queue: multiprocessing.Queue):
    """Forward WorkerEvent objects to frontend as JSON."""
    while True:
        try:
            event: WorkerEvent = event_queue.get_nowait()
            await send_json(ws, {"type": event.type, "data": event.data})
        except Exception:
            await asyncio.sleep(0.1)

async def telemetry_loop(ws):
    """Send CPU/RAM/VRAM usage periodically."""
    while True:
        ram = psutil.virtual_memory().used / (1024**2)
        cpu = psutil.cpu_percent(interval=None)
        data = {"type": "system_usage", "cpu": cpu, "ram": ram, "vram": 0}  # fill VRAM if needed
        await send_json(ws, data)
        await asyncio.sleep(2)

async def handle_client(ws):
    global heavy_process, heavy_cmd_queue, heavy_event_queue

    # Start event forwarder for small worker
    asyncio.create_task(forward_events(ws, small_event_queue))

    # Start telemetry
    asyncio.create_task(telemetry_loop(ws))

    async for message in ws:
        msg = json.loads(message)
        cmd_type = msg.get("cmd")
        payload = msg.get("payload", {})

        if cmd_type == "heartbeat":
            await send_json(ws, {"type": "pong"})

        elif cmd_type == "parse":
            small_cmd_queue.put(WorkerCommand(cmd="parse", payload=payload))

        elif cmd_type == "convert":
            # Spawn heavy worker if not running
            if heavy_process is None or not heavy_process.is_alive():
                heavy_cmd_queue = multiprocessing.Queue()
                heavy_event_queue = multiprocessing.Queue()
                heavy_process = multiprocessing.Process(target=nnlib_worker, args=(heavy_cmd_queue, heavy_event_queue))
                heavy_process.start()
                # Start forwarder
                asyncio.create_task(forward_events(ws, heavy_event_queue))
            heavy_cmd_queue.put(WorkerCommand(cmd="convert", payload=payload))

        elif cmd_type == "cancel":
            if heavy_cmd_queue:
                heavy_cmd_queue.put(WorkerCommand(cmd="cancel"))

        elif cmd_type == "shutdown":
            small_cmd_queue.put(WorkerCommand(cmd="shutdown"))
            if heavy_cmd_queue:
                heavy_cmd_queue.put(WorkerCommand(cmd="shutdown"))
            break

async def main():
    async with websockets.serve(handle_client, "127.0.0.1", 8442):
        print("Backend server running on ws://127.0.0.1:8442")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
