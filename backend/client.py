import asyncio
from asyncio import log
import json
import multiprocessing
import signal
import time
import psutil
import websockets
# from tasks import run_long_task_async
from hutils import lightcyan, lightgreen, yellow
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
from worker import nn_cmd_queue, nn_event_queue

# Only one client
client_task: asyncio.Task = None
client_ws: ServerConnection = None
shutdown_event = asyncio.Event()




async def forward_events(ws: ServerConnection, event_queue: multiprocessing.Queue):
    """Forward WorkerEvent objects to frontend as JSON."""
    try:
        while True:
            try:
                event: WorkerEvent = event_queue.get_nowait()
            except Exception:
                await asyncio.sleep(0.1)
                continue

            try:
                msg: dict = {
                    "type": event.type,
                    "data": event.data
                }
                print(lightcyan(f"send:"), msg)
                await send_json(ws, msg)
            except websockets.ConnectionClosed:
                # Client disconnected, exit loop
                break
            except Exception as e:
                slog.warning(f"Failed to forward event: {e}")
    except asyncio.CancelledError:
        # Task was cancelled (on client disconnect)
        pass



async def handle_client(ws: ServerConnection):
    global client_task, client_ws
    slog.info(f"Client connected: {ws.remote_address}")
    client_ws = ws


    # Forward worker events to this client
    forward_task = asyncio.create_task(forward_events(ws, nn_event_queue))

    # Start telemetry task
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
                print(lightcyan(cmd))
                slog.info("Shutdown command received from client")
                shutdown_event.set()
                break

            elif cmd == "parse":
                slog.info(f"parse model: {data}")
                nn_cmd_queue.put(
                    WorkerCommand(
                        cmd=cmd,
                        payload=data.get('payload', {})
                    )
                )


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

        # Cancel event forwarder task
        if forward_task:
            forward_task.cancel()
            await asyncio.gather(forward_task, return_exceptions=True)

        slog.info(f"Cleaned up client: {ws.remote_address}")
        client_ws = None
        client_task = None
