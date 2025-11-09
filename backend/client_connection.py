from __future__ import annotations

import asyncio
import json
import multiprocessing as mp
from pprint import pprint
import websockets
from messages import WorkerResponse
from worker import (
    Worker,
    worker_task_list,
)
from hutils import lightcyan, red, yellow
from websockets import (
    ServerConnection,
    connect,
    ConnectionClosed,
    ConnectionClosedOK,
    ConnectionClosedError,
)
from logger import slog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server import BackendServer


class ClientConnectionHandler:
    def __init__(
        self,
        websocket: ServerConnection,
        client_id: str,
        server: BackendServer,
    ):
        """
        websocket: the connected websocket object
        client_id: unique id for this client
        server: reference to the backend server (optional, for broadcasts, etc.)
        """
        # Control flags
        self.running = False
        self.stopping = False

        # List of asyncio tasks for send/recv loops
        self.tasks = []

        # websocket
        self.websocket = websocket
        self.client_id = client_id
        self.server = server

        # Async queues for websocket I/O
        self.to_client = asyncio.Queue()
        self.from_client = asyncio.Queue()

        # Worker management
        self.workers: dict[str, Worker] = {}
        self.task_queues: dict[str, mp.Queue] = {}
        self.result_queues: dict[str, mp.Queue] = {}
        self.stop_events: dict[str, mp.Event] = {}
        self.worker_name = "nnlib"
        self.start_worker(self.worker_name)


    async def route_message(self, msg):
        """
        Decide whether to forward to a worker or handle as control message.
        Expecting `msg` as a dict with at least a 'type' field.
        """
        try:
            msg = json.loads(msg)
        except json.JSONDecodeError:
            slog.warning(f"Received invalid JSON: {msg}")
            return

        cmd: str = msg.get("cmd", "")
        print(lightcyan(f"<<< {cmd}"))

        if cmd == "heartbeat":
            await self.to_client.put(WorkerResponse(type="pong"))

        elif cmd == "shutdown":
            print(lightcyan("shutdown"))
            await self.stop()

        elif cmd in worker_task_list:
            self.submit_task_to_worker(self.worker_name, msg)

        else:
            slog.warning(f"[Handler {self.client_id}] Unknown message type: {cmd}")


    async def reception_task(self):
        """
        Receive messages from the client websocket and route them.
        """
        try:
            async for msg in self.websocket:
                if not self.running:
                    break
                await self.route_message(msg)

        except websockets.ConnectionClosedOK:
            slog.info(f"[Handler {self.client_id}] connection closed")

        except websockets.ConnectionClosedError as e:
            slog.warning(f"[Handler {self.client_id}] disconnected with error {e}")

        except Exception as e:
            slog.warning(f"[Handler {self.client_id}] exception while running reception handler {e}")

        finally:
            self.running = False
            slog.info(f"[Handler {self.client_id}] Reception task ended")


    async def send_task(self):
        while self.running:
            try:
                event: WorkerResponse = await asyncio.wait_for(
                    self.to_client.get(),
                    timeout=0.5
                )
                msg: dict = {
                    "type": event.type,
                    "payload": event.payload
                }
                await self.websocket.send(json.dumps(msg))

            except asyncio.TimeoutError:
                continue

            except websockets.ConnectionClosed:
                slog.info(f"[Handler {self.client_id}] Connection closed while sending")
                self.running = False
                break

            except Exception as e:
                slog.error(f"[Handler {self.client_id}] Failed to send message: {e}")

        slog.info(f"[Handler {self.client_id}] Send task ended")


    async def stop(self):
        """Stop all tasks and workers for this client."""
        if self.stopping:
            slog.info(f"[Handler {self.client_id}] Already stopping")
            return

        self.stopping = True
        slog.info(f"[Handler {self.client_id}] Initiating stop sequence")

        # Step 1: Stop running flag FIRST (stops async tasks from doing work)
        self.running = False

        # Step 2: Notify client of shutdown
        try:
            shutdown_msg = WorkerResponse(
                type="shutdown",
                payload="Server is shutting down"
            )
            await asyncio.wait_for(
                self.websocket.send(json.dumps({
                    "type": shutdown_msg.type,
                    "payload": shutdown_msg.payload
                })),
                timeout=1.0
            )
            slog.info(f"[Handler {self.client_id}] Sent shutdown notification to client")
        except (websockets.ConnectionClosed, asyncio.TimeoutError):
            slog.info(f"[Handler {self.client_id}] Client already disconnected")
        except Exception as e:
            slog.warning(f"[Handler {self.client_id}] Failed to send shutdown message: {e}")

        # Step 3: Close websocket connection
        try:
            await asyncio.wait_for(
                self.websocket.close(code=1000, reason="Server shutting down"),
                timeout=1.0
            )
            slog.info(f"[Handler {self.client_id}] WebSocket closed")
        except asyncio.TimeoutError:
            slog.warning(f"[Handler {self.client_id}] WebSocket close timed out")
        except Exception as e:
            slog.warning(f"[Handler {self.client_id}] Error closing WebSocket: {e}")

        # Step 4: Cancel async tasks individually with error handling
        cancelled_tasks = []
        for i, task in enumerate(self.tasks):
            if not task.done():
                try:
                    task.cancel()
                    cancelled_tasks.append(task)
                except Exception as e:
                    slog.warning(f"[Handler {self.client_id}] Error cancelling task {i}: {e}")

        # Wait for cancelled tasks with timeout
        if cancelled_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*cancelled_tasks, return_exceptions=True),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                slog.warning(f"[Handler {self.client_id}] Task cancellation timed out")
            except Exception as e:
                slog.warning(f"[Handler {self.client_id}] Error gathering tasks: {e}")

            slog.info(f"[Handler {self.client_id}] All async tasks stopped")

        # Step 5: Stop all workers gracefully
        await self._stop_all_workers()

        slog.info(f"[Handler {self.client_id}] Stop sequence complete")


    async def _stop_all_workers(self):
        """Stop all worker processes gracefully"""
        if not self.workers:
            return

        slog.info(f"[Handler {self.client_id}] Stopping {len(self.workers)} worker(s)")

        for name, worker in list(self.workers.items()):
            if not worker.is_alive():
                slog.info(f"[Handler {self.client_id}] Worker {name} already stopped")
                continue

            slog.info(f"[Handler {self.client_id}] Stopping worker {name}...")

            # Send shutdown command
            try:
                self.task_queues[name].put({'cmd': 'shutdown'}, block=False)
            except Exception as e:
                slog.warning(f"[Handler {self.client_id}] Failed to send shutdown to {name}: {e}")

            # Set stop event
            self.stop_events[name].set()

            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, worker.join, 3.0),
                    timeout=4.0
                )
            except asyncio.TimeoutError:
                slog.warning(f"[Handler {self.client_id}] Timeout waiting for worker {name}")

            if worker.is_alive():
                slog.warning(f"[Handler {self.client_id}] Worker {name} didn't stop gracefully, terminating...")
                try:
                    worker.terminate()
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, worker.join, 1.0),
                        timeout=2.0
                    )
                except asyncio.TimeoutError:
                    slog.warning(f"[Handler {self.client_id}] Timeout terminating worker {name}")

            if worker.is_alive():
                slog.error(f"[Handler {self.client_id}] Worker {name} still alive, killing...")
                try:
                    worker.kill()
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, worker.join, 1.0),
                        timeout=2.0
                    )
                except asyncio.TimeoutError:
                    slog.error(f"[Handler {self.client_id}] Timeout killing worker {name}")

            if worker.is_alive():
                slog.error(f"[Handler {self.client_id}] Worker {name} could not be stopped!")
            else:
                slog.info(f"[Handler {self.client_id}] Worker {name} stopped")


    async def handle(self):
        """
        Start the send/recv loops for this client.
        Returns when the client disconnects or stop() is called.
        """
        self.running = True
        slog.info(f"[Handler {self.client_id}] Handler started")

        # Start websocket loops
        reception_task = asyncio.create_task(self.reception_task())
        send_task = asyncio.create_task(self.send_task())

        self.tasks = [reception_task, send_task]

        # Start worker result loop(s)
        for name in self.workers.keys():
            worker_task = asyncio.create_task(self.worker_result_loop(name))
            self.tasks.append(worker_task)

        try:
            # Wait for any task to complete (likely due to disconnect or error)
            done, pending = await asyncio.wait(
                self.tasks,
                return_when=asyncio.FIRST_COMPLETED
            )

            slog.info(f"[Handler {self.client_id}] First task completed, stopping others")

        except asyncio.CancelledError:
            slog.info(f"[Handler {self.client_id}] Handler tasks cancelled")

        except Exception as e:
            slog.error(f"[Handler {self.client_id}] Exception in handler: {e}")

        finally:
            if not self.stopping:
                await self.stop()

        slog.info(f"[Handler {self.client_id}] Handler ended")


    def start_worker(self, name: str):
        """
        Create and start a worker process.
        """
        if name in self.workers and self.workers[name].is_alive():
            print(f"Worker {name} already running")
            return

        task_queue = mp.Queue()
        result_queue = mp.Queue()
        stop_event = mp.Event()

        worker = Worker(
            task_queue=task_queue,
            result_queue=result_queue,
            stop_event=stop_event
        )
        worker.start()

        self.workers[name] = worker
        self.task_queues[name] = task_queue
        self.result_queues[name] = result_queue
        self.stop_events[name] = stop_event

        # Start async loop to forward results from this worker
        self.tasks.append(asyncio.create_task(self.worker_result_loop(name)))
        print(f"[Handler {self.client_id}] Worker {name} started")


    async def worker_result_loop(self, name: str):
        """
        Async loop to forward worker results to the to_client queue.
        """
        loop = asyncio.get_running_loop()
        result_queue = self.result_queues.get(name)

        if not result_queue:
            slog.error(f"[Handler {self.client_id}] No result queue for worker {name}")
            return

        while self.running:
            try:
                # Use a short timeout to allow checking self.running
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, result_queue.get, True, 0.5),
                    timeout=1.0
                )

                if self.running:
                    await self.to_client.put(result)

            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue

            except asyncio.CancelledError:
                slog.info(f"[Handler {self.client_id}] Worker result loop cancelled for {name}")
                break

            except Exception as e:
                if self.running:
                    slog.error(f"[Handler {self.client_id}] Error in worker result loop: {e}")
                break

        slog.info(f"[Handler {self.client_id}] Worker result loop for {name} ended")



    def submit_task_to_worker(self, name: str, task):
        """
        Put a task into the worker's task queue.
        """
        if not name:
            # Get the first key from the dictionary if 'name' is not provided
            name = next(iter(self.task_queues), "")

        if (
            name
            and name in self.task_queues
            and task is not None
        ):
            try:
                self.task_queues[name].put(task, block=False)
            except Exception as e:
                slog.error(f"[Handler {self.client_id}] Failed to submit task to worker {name}: {e}")






















