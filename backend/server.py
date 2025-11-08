import asyncio
from client_connection import ClientConnectionHandler
from hutils import red, yellow
import logging
from logger import slog
import multiprocessing as mp
import os
import signal
import sys
import uuid
from websockets import (
    ServerConnection,
    serve,
    Server,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


class BackendServer:
    def __init__(self, host="127.0.0.1", port=8442):
        self.host = host
        self.port = port

        self.clients: dict[str, ClientConnectionHandler] = {}
        self._server: Server = None
        self._running: bool = False


    def register_client(self, server_connection: ServerConnection) -> str:
        """Register a new client connection, returns the uuid"""
        client_id = str(uuid.uuid4())
        handler = ClientConnectionHandler(
            server_connection,
            client_id=client_id,
            server=self
        )
        self.clients[client_id] = handler
        slog.info(f"Client registerd: {client_id}")
        return client_id


    async def unregister_client(self, client_id: str) -> None:
        """Unregister client connection and clean up."""
        handler = self.clients.pop(client_id, None)
        if handler:
            await handler.stop()
        print(f"[Server] Client {client_id} disconnected (total={len(self.clients)})")


    async def handle_new_client(self, server_connection: ServerConnection):
        """Called by websockets.serve() for each new connection."""
        client_id = self.register_client(server_connection=server_connection)
        print(f"[Server] Client connected: {client_id} (total={len(self.clients)})")
        handler: ClientConnectionHandler = self.clients[client_id]
        try:
            await handler.handle()

        except Exception as e:
            print(f"[Server] Client {client_id} error: {e}")

        finally:
            await self.unregister_client(client_id)


    async def run(self):
        """Start the websocket server."""
        slog.info(f"Starting WebSocket server on {self.host}:{self.port}")

        self._server = await serve(
            self.handle_new_client,
            self.host,
            self.port
        )
        print(f"Server listening on {self.host}:{self.port}")
        self._running = True

        # Wait until shutdown is requested
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

        slog.info(f"WebSocket server stopped serving on {self.host}:{self.port}")


    async def shutdown(self):
        """Clean shutdown."""
        print("[Server] Shutting down...")

        # Stop accepting new connections
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()


        # Gracefully stop all handlers concurrently
        # ensures all handlers attempt to stop even if some fail
        handlers = list(self.clients.values())
        await asyncio.gather(
            *[handler.stop() for handler in handlers],
            return_exceptions=True
        )

        self.clients.clear()
        print("[Server] Shutdown complete.")
        self._running = False


    async def broadcast(self, message):
        # Use gather to send to all clients concurrently
        handlers = list(self.clients.values())
        await asyncio.gather(
            *[handler.to_client.put(message) for handler in handlers],
            return_exceptions=True
        )


async def shutdown_gracefully():
    """Graceful shutdown triggered by signal"""
    slog.info("Starting graceful shutdown...")

    # Find the server instance (we'll need to store it globally or pass it)
    # For now, let's modify main() to handle this
    pass


def signal_handler(signum, frame):
    """Handle termination signals"""
    slog.info(f"Received signal {signum}")

    # Get the running event loop and schedule shutdown
    try:
        loop = asyncio.get_running_loop()
        # Schedule the shutdown coroutine
        loop.create_task(shutdown_gracefully())
    except RuntimeError:
        # No running loop, exit immediately
        sys.exit(0)




# def signal_handler(signum, frame):
#     """Handle termination signals"""
#     slog.info(f"Received signal {signum}")

#     # Terminate any multiprocessing children
#     from multiprocessing.context import SpawnProcess
#     Processes = SpawnProcess
#     if sys.platform == 'linux':
#         from multiprocessing.context import ForkProcess
#         Processes = ForkProcess | SpawnProcess


#     for child in mp.active_children():
#         slog.info(yellow(f"Terminating child {child.name}"))
#         child.terminate()  # sends SIGTERM
#         try:
#             child.join(timeout=2)  # wait for it to be reaped
#             if child.is_alive():
#                 slog.warning(f"Child {child.name} still alive, sending SIGKILL")
#                 os.kill(child.pid, signal.SIGKILL)
#                 child.join(timeout=1)
#         except Exception as e:
#             slog.error(f"Error terminating child {child.name}: {e}")

#     sys.exit(0)


async def main():
    slog.info("start")
    host, port = "127.0.0.1", 8442

    server = BackendServer(host=host, port=port)

    # Create shutdown event
    shutdown_event = asyncio.Event()

    # Setup signal handlers (cross-platform)
    def handle_signal(signum, frame):
        slog.info(f"Shutdown signal {signum} received")
        shutdown_event.set()

    # Use standard signal.signal (works on both Windows and Linux)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        # Run server in background
        server_task = asyncio.create_task(server.run())

        # Wait for shutdown signal
        await shutdown_event.wait()

        slog.info("Initiating shutdown...")
        server._running = False

        # Wait for server to finish
        await server_task

    except Exception as e:
        slog.error(f"Server error: {e}", exc_info=True)
    finally:
        await server.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        slog.info("KeyboardInterrupt - exiting gracefully.")

    except Exception as e:
        slog.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)






# async def shutdown(server):
#     """Gracefully close websocket server and all subprocesses."""
#     slog.info("Shutting down backend...")

#     # Close websocket client if needed
#     global client_ws
#     if client_ws and not client_ws.closed:
#         print("disconnect clients")
#         try:
#             await client_ws.close(code=1000, reason="Server shutting down")
#         except Exception as e:
#             slog.warning(f"Error closing client WS: {e}")

#     # Terminate and join the worker
#     global nn_worker
#     nn_cmd_queue.put("shutdown")
#     if nn_worker is not None and nn_worker.is_alive():
#         nn_worker.join(timeout=2)  # wait for exit
#         if nn_worker.is_alive():
#             slog.warning(f"Worker {nn_worker.name} still alive, sending SIGKILL")
#             os.kill(nn_worker.pid, signal.SIGKILL)
#             nn_worker.join(timeout=1)

#     # Close server
#     try:
#         server.close()
#         await server.wait_closed()
#         slog.info(yellow("WebSocket server closed."))
#     except Exception as e:
#         slog.warning(f"Error closing server: {e}")

#     # Terminate any multiprocessing children
#     from multiprocessing.context import SpawnProcess
#     Processes = SpawnProcess
#     if sys.platform == 'linux':
#         from multiprocessing.context import ForkProcess
#         Processes = ForkProcess | SpawnProcess


#     for child in mp.active_children():
#         slog.info(yellow(f"Terminating child {child.name}"))
#         child.terminate()  # sends SIGTERM
#         try:
#             child.join(timeout=2)  # wait for it to be reaped
#             if child.is_alive():
#                 slog.warning(f"Child {child.name} still alive, sending SIGKILL")
#                 os.kill(child.pid, signal.SIGKILL)
#                 child.join(timeout=1)
#         except Exception as e:
#             slog.error(f"Error terminating child {child.name}: {e}")


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

    # shutdown_event.set()
    # slog.info("Shutdown complete.")
    # raise



# async def main():
#     slog.info("start")
#     server = None
#     host, port = "127.0.0.1", 8442

#     global nn_worker, nn_cmd_queue, nn_event_queue
#     nn_cmd_queue = mp.Queue()
#     nn_event_queue = mp.Queue()

#     nn_worker = mp.Process(
#         target=nnlib_worker,
#         name="nnlib_worker",
#         args=(nn_cmd_queue, nn_event_queue),
#     )
#     nn_worker.start()

#     server = await websockets.serve(
#         handler=connection_handler,
#         host=host,
#         port=port,
#         ping_interval=5,
#         ping_timeout=10,
#         reuse_port=True if sys.platform == 'linux' else False
#     )
#     slog.info(f"Backend server running on ws://{host}:{port}")
#     # Signal handler
#     loop = asyncio.get_running_loop()

#    # --- Signal handler ---
#     def signal_handler(signum, frame):
#         slog.info(f"Signal {signum} received - initiating shutdown...")
#         # Schedule shutdown on the running loop
#         loop.call_soon_threadsafe(lambda: asyncio.create_task(shutdown(server)))

#     for sig in (signal.SIGINT, signal.SIGTERM):
#         signal.signal(sig, signal_handler)

#     print("READY")
#     try:
#         await shutdown_event.wait()
#     except asyncio.CancelledError:
#         pass
#     finally:
#         await shutdown(server)



# if __name__ == "__main__":
#     # signal.signal(signal.SIGINT, signal.SIG_DFL)
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         # Should not normally trigger because signal handler handles it
#         slog.info("KeyboardInterrupt - exiting gracefully.")
