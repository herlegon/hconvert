import asyncio
from asyncio import log
import json
import multiprocessing
import os
import signal
import socket
import sys
import time
import psutil
import websockets
from client import handle_client
from hutils import red, yellow
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
from client import client_ws, shutdown_event
import multiprocessing as mp
from worker import nn_cmd_queue, nn_worker





async def shutdown(server):
    """Gracefully close websocket server and all subprocesses."""
    slog.info("Shutting down backend...")

    # Close websocket client if needed
    global client_ws
    if client_ws and not client_ws.closed:
        print("disconnect clients")
        try:
            await client_ws.close(code=1000, reason="Server shutting down")
        except Exception as e:
            slog.warning(f"Error closing client WS: {e}")

    # Terminate and join the worker
    nn_cmd_queue.put("shutdown")
    if nn_worker.is_alive():
        nn_worker.join(timeout=2)  # wait for exit
        if nn_worker.is_alive():
            slog.warning(f"Worker {nn_worker.name} still alive, sending SIGKILL")
            os.kill(nn_worker.pid, signal.SIGKILL)
            nn_worker.join(timeout=1)

    # Close server
    try:
        server.close()
        await server.wait_closed()
        slog.info(yellow("WebSocket server closed."))
    except Exception as e:
        slog.warning(f"Error closing server: {e}")

    # Terminate any multiprocessing children
    from multiprocessing.context import SpawnProcess
    Processes = SpawnProcess
    if sys.platform == 'linux':
        from multiprocessing.context import ForkProcess
        Processes = ForkProcess | SpawnProcess


    for child in mp.active_children():
        slog.info(yellow(f"Terminating child {child.name}"))
        child.terminate()  # sends SIGTERM
        try:
            child.join(timeout=2)  # wait for it to be reaped
            if child.is_alive():
                slog.warning(f"Child {child.name} still alive, sending SIGKILL")
                os.kill(child.pid, signal.SIGKILL)
                child.join(timeout=1)
        except Exception as e:
            slog.error(f"Error terminating child {child.name}: {e}")


    # current_process = psutil.Process()
    # children = current_process.children(recursive=True)
    # print(children)
    # for child in children:
    #     if isinstance(child, Processes):
    #         print(red(f"cannot stop process: {child.name()}"))
    #         continue
    #     print(f"Child pid is {child.pid}, {child.name()}")
    #     if child.is_running():
    #         try:
    #             print(child.memory_info())
    #         except:
    #             pass
    #     child.terminate()
    #     # child.kill()

    # print(active_children)
    # for c in mp.active_children():
    #     print(type(c))
    #     c.join()

    shutdown_event.set()
    slog.info("Shutdown complete.")
    # raise


async def main():
    slog.info("start")
    server = None
    host, port = "127.0.0.1", 8442

    server = await websockets.serve(
        handler=handle_client,
        host=host,
        port=port,
        ping_interval=5,
        ping_timeout=10,
        reuse_port=True # Linux
    )
    slog.info(f"Backend server running on ws://{host}:{port}")
    # Signal handler
    loop = asyncio.get_running_loop()

   # --- Signal handler ---
    def signal_handler(signum, frame):
        slog.info(f"Signal {signum} received — initiating shutdown...")
        # Schedule shutdown on the running loop
        loop.call_soon_threadsafe(lambda: asyncio.create_task(shutdown(server)))

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)

    print("READY")
    try:
        await shutdown_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        await shutdown(server)



if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Should not normally trigger because signal handler handles it
        slog.info("KeyboardInterrupt — exiting gracefully.")
