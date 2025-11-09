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
        self._server: Server = None
        self._shutting_down: bool = False
        self._shutdown_event: asyncio.Event = None

        self.clients: dict[str, ClientConnectionHandler] = {}


    async def shutdown(self) -> None:
        """Initiate graceful shutdown sequence"""
        if self._shutting_down:
            slog.info("Shutdown already in progress")
            return

        self._shutting_down = True
        slog.info("Starting graceful shutdown...")

        # Step 1: Stop accepting new connections
        if self._server is not None:
            slog.info("Closing server socket (refusing new connections)...")
            self._server.close()
            await self._server.wait_closed()
            slog.info("Server socket closed")

        # Step 2: Notify all connected clients and initiate their shutdown
        if self.clients:
            slog.info(f"Notifying {len(self.clients)} client(s) of shutdown...")
            handlers = list(self.clients.values())

            # Stop all client handlers (they will notify clients and stop workers)
            await asyncio.gather(
                *[handler.stop() for handler in handlers],
                return_exceptions=True
            )
            self.clients.clear()
            slog.info("All clients disconnected")

        # Step 3: Verify no child processes remain
        active_children = mp.active_children()
        if active_children:
            slog.warning(f"Still have {len(active_children)} active child processes:")
            for child in active_children:
                slog.warning(f"  - {child.name} (PID: {child.pid})")

        slog.info("Shutdown complete")

        # Signal shutdown complete
        if self._shutdown_event:
            self._shutdown_event.set()


    def register_client(self, server_connection: ServerConnection) -> str | None:
        """Register a new client connection, returns the uuid"""
        if self._shutting_down:
            slog.warning("Refusing new connection - server is shutting down")
            return None

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
        # Check if we're shutting down before accepting
        if self._shutting_down:
            slog.info("Rejecting connection - server is shutting down")
            await server_connection.close(code=1001, reason="Server shutting down")
            return

        client_id = self.register_client(server_connection=server_connection)

        if client_id is None:
            await server_connection.close(code=1001, reason="Server shutting down")
            return

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

        self._shutdown_event = asyncio.Event()

        self._server = await serve(
            self.handle_new_client,
            self.host,
            self.port
        )
        slog.info(f"Server listening on {self.host}:{self.port}")

        # Wait until shutdown is requested
        await self._shutdown_event.wait()
        slog.info("Server run loop ended")


    async def broadcast(self, message):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return

        # Use gather to send to all clients concurrently
        handlers = list(self.clients.values())
        await asyncio.gather(
            *[handler.to_client.put(message) for handler in handlers],
            return_exceptions=True
        )


async def main():
    slog.info("Server starting")
    host, port = "127.0.0.1", 8442

    server = BackendServer(host=host, port=port)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()

    def signal_handler(signum, frame):
        sig_name = signal.Signals(signum).name
        slog.info(f"Received signal {sig_name} ({signum})")
        # Schedule shutdown in the event loop
        asyncio.create_task(server.shutdown())

    # Register signal handlers
    # for sig in (signal.SIGINT, signal.SIGTERM):
    #     loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)


    try:
        # Run server (will block until shutdown completes)
        await server.run()

    except Exception as e:
        slog.error(f"Server error: {e}", exc_info=True)
        await server.shutdown()

    slog.info("Main exiting")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        slog.info("KeyboardInterrupt received")
    except Exception as e:
        slog.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    slog.info("Process exit")




