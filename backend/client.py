import asyncio
from asyncio import log
import json
import multiprocessing
import signal
import time
import psutil
import websockets
# from tasks import run_long_task_async
from hutils import lightgreen, yellow
from utils import send_json
from telemetry import telemetry_loop
from messages import WorkerCommand, WorkerEvent
from websockets import (
    ServerConnection,
    connect,
    ConnectionClosed,
    ConnectionClosedOK,
    ConnectionClosedError,
)
from logger import slog

# Only one client
client_task: asyncio.Task = None
client_ws: ServerConnection = None
shutdown_event = asyncio.Event()


async def handle_client(ws: ServerConnection):
    global client_task, client_ws
    slog.info(f"Client connected: {ws.remote_address}")
    client_ws = ws

    # Start telemetry background task
    client_task = asyncio.create_task(telemetry_loop(ws))

    try:

        async for msg in ws:
            # Handle incoming messages
            try:
                data = json.loads(msg)

            except json.JSONDecodeError:
                slog.warning(f"Received invalid JSON: {msg}")
                continue

            cmd = data.get("cmd")
            print(lightgreen(cmd))

            if cmd == "heartbeat":
                await send_json(ws, {"type": "pong"})

            elif cmd == "short_task":
                # Example of a small task (<5s)
                result = {"type": "result", "data": {"value": "ok"}}
                await send_json(ws, result)

            # elif cmd == "long_task":
            #     # Here dispatch to worker process
            #     result = await run_long_task_async(data.get("params", {}))
            #     await send_json(ws, {"type": "result", "data": result})

            elif cmd == "shutdown":
                slog.info("Shutdown command received from client")
                shutdown_event.set()
                break

            else:
                slog.warning(f"Unknown command: {cmd}")

    except websockets.ConnectionClosedOK:
        slog.info("Client disconnected normally")

    except websockets.ConnectionClosedError as e:
        slog.warning(f"Client disconnected with error: {e}")

    finally:
        # Cancel telemetry task
        if client_task:
            client_task.cancel()
            await asyncio.gather(client_task, return_exceptions=True)
        slog.info(f"Cleaned up client: {client_ws.remote_address}")
        client_ws = None
        client_task = None

