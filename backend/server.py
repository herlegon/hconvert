import asyncio
from asyncio import log
import json
import multiprocessing
import signal
import sys
import time
import psutil
import websockets
from client import handle_client
from hutils import yellow
from utils import send_json
from telemetry import telemetry_loop
from messages import WorkerCommand, WorkerEvent
from worker import nnlib_worker
from websockets import (
    ServerConnection,
    connect,
    ConnectionClosed,
    ConnectionClosedOK,
    ConnectionClosedError,
)
from logger import alog
from client import client_ws, shutdown_event




async def forward_events(ws: ServerConnection, event_queue: multiprocessing.Queue):
    """Forward WorkerEvent objects to frontend as JSON."""
    while True:
        try:
            event: WorkerEvent = event_queue.get_nowait()
            await send_json(ws, {"type": event.type, "data": event.data})
        except Exception:
            await asyncio.sleep(0.1)




async def main():
    server = await websockets.serve(
        handler=handle_client,
        host="127.0.0.1",
        port=8442,
        ping_interval=5,
        ping_timeout=10,
    )
    alog.info("Backend server running on ws://127.0.0.1:8442")

    # Wait until shutdown_event is triggered
    await shutdown_event.wait()

    # Close client connection if still open
    if client_ws and not client_ws.closed:
        await client_ws.close(code=1000, reason="Server shutting down")

    # Close the server
    server.close()
    await server.wait_closed()
    alog.info("Server closed. Exiting.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    asyncio.run(main())
