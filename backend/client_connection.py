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
from hutils import lightcyan, red
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
            print(f"[Handler {self.client_id}] Unknown message type: {cmd}")


    async def reception_task(self):
        """
        Receive messages from the client websocket and route them.
        """
        try:
            async for msg in self.websocket:
                await self.route_message(msg)

        except websockets.ConnectionClosedOK:
            slog.info(f"[Handler {self.client_id}] connection closed")

        except websockets.ConnectionClosedError as e:
            slog.warning(f"[Handler {self.client_id}] disconnected with error {e}")

        except Exception as e:
            slog.warning(f"[Handler {self.client_id}] exception while running reception handler {e}")

        self.running = False
        slog.info(f"[Handler {self.client_id}] sending task ended")


    async def send_task(self):
        while self.running:
            try:
                event: WorkerResponse = await self.to_client.get()
                msg: dict = {
                    "type": event.type,
                    "payload": event.payload
                }

                print("*************")
                print(type(msg))
                pprint(msg)
                print("-------------")
                print(json.dumps(msg))
                await self.websocket.send(json.dumps(msg))

            except websockets.ConnectionClosed:
                print(f"[Handler {self.client_id}] connection closed while sending")
                self.running = False
                break

            except Exception as e:
                slog.warning(f"Failed to send message: {str(e)}")

        slog.info(f"[Handler {self.client_id}] sending task ended")


    async def stop(self):
        """Stop all tasks and workers for this client."""
        if not self.running:
            return

        print(lightcyan(f"stop"))
        self.running = False

        # Cancel websocket tasks
        for t in self.tasks:
            t.cancel()

        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Stop workers gracefully
        for name, worker in self.workers.items():
            slog.info(f"Stopping worker {name}...")
            self.submit_task_to_worker(
                self.worker_name, {'cmd': 'shutdown'}
            )

            # Set stop event
            self.stop_events[name].set()

            # Wait for graceful shutdown
            worker.join(timeout=2.0)

            if worker.is_alive():
                slog.warning(f"Worker {name} didn't stop, terminating...")
                worker.terminate()
                worker.join(timeout=1.0)

            if worker.is_alive():
                slog.error(f"Worker {name} still alive, killing...")
                worker.kill()
                worker.join()

        print(f"[Handler {self.client_id}] stopped")


    async def handle(self):
        """
        Start the send/recv loops for this client.
        Returns when the client disconnects or stop() is called.
        """
        self.running = True
        print(f"[Handler {self.client_id}] started")

        # Start websocket loops
        self.tasks = [
            asyncio.create_task(self.reception_task()),
            asyncio.create_task(self.send_task())
        ]

        # Start worker result loop(s)
        for name in self.workers.keys():
            self.tasks.append(asyncio.create_task(self.worker_result_loop(name)))

        try:
            await asyncio.gather(*self.tasks)

        except asyncio.CancelledError:
            pass

        except Exception as e:
            slog.error(red(f"handle: exception {str(e)}"))

        finally:
            slog.info(f"stopping handle")
            await self.stop()


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
        result_queue = self.result_queues[name]

        while self.running:
            try:
                # Blocking get in executor to avoid blocking the event loop
                result = await loop.run_in_executor(None, result_queue.get)
                await self.to_client.put(result)
            except asyncio.CancelledError:
                break


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
            self.task_queues[name].put(task)





















    # async def start_worker(self):
    #     """Start worker process"""

    #     # Start worker process
    #     # When starting for the first time, wait for the worker
    #     # to avoid UI polling and manage a single error only

    #     # Wait for worker to be alive with timeout
    #     worker_timeout = 3.0  # seconds
    #     wait_time = 0.0
    #     check_interval = 0.1
    #     worker_alive = False

    #     while wait_time < worker_timeout:
    #         if self.worker_process and self.worker_process.is_alive():
    #             worker_alive = True
    #             break
    #         await asyncio.sleep(check_interval)
    #         wait_time += check_interval

    #     timeout_occurred = wait_time >= worker_timeout

    #     self.worker_process = Worker(
    #         self.task_queue,
    #         self.result_queue,
    #         self.stop_event
    #     )
    #     self.worker_process.start()
    #     slog.info(f"Worker process started (PID: {self.worker_process.pid})")

    #     if self.worker_process and not timeout_occurred:
    #         # Send ready message to stdout
    #         print("READY", flush=True)
    #         slog.info("Backend fully ready - sent ready signal to stdout")
    #     else:
    #         print("FAILED", flush=True)
    #         slog.error(f"Worker failed to start (timeout: {timeout_occurred}, alive: {worker_alive})")
    #         print(json.dumps({"status": "error", "message": "Worker failed to start"}), flush=True)


    # def stop_worker(self):
    #     """Stop worker process"""
    #     if self.worker_process and self.worker_process.is_alive():
    #         slog.info("Stopping worker process...")
    #         self.task_queue.put({"task": "shutdown"})
    #         self.worker_process.join(timeout=5)

    #         if self.worker_process.is_alive():
    #             slog.warning("Worker didn't stop gracefully, terminating...")
    #             self.worker_process.terminate()
    #             self.worker_process.join(timeout=2)

    #         if self.worker_process.is_alive():
    #             slog.error("Worker still alive, killing...")
    #             self.worker_process.kill()
    #             self.worker_process.join()


    # def worker_alive(self):
    #     return self.worker_process.is_alive() if self.worker_process else False


    # def send_task_to_worker(self, task_name, params):
    #     """Send task to worker process"""
    #     self.worker_queue.put({
    #         "task": task_name,
    #         "params": params
    #     })


    # def cancel_worker_task(self):
    #     """Cancel current worker task"""
    #     self.stop_event.set()


    # async def monitor_worker_results(self):
    #     """Monitor results from worker process"""
    #     slog.info("Starting worker result monitor")
    #     while self.running:
    #         try:
    #             # Check for results from worker (non-blocking)
    #             if not self.result_queue.empty():
    #                 result = self.result_queue.get_nowait()

    #                 # Broadcast result to all clients
    #                 await self.broadcast(result)

    #                 # Reset stop event after task completes
    #                 if result.get("type") in ["result", "error"]:
    #                     self.stop_event.clear()

    #             await asyncio.sleep(0.05)  # Check frequently for responsiveness
    #         except Exception as e:
    #             slog.error(f"Error monitoring worker: {e}")
    #             await asyncio.sleep(1)

    #     slog.info("Worker result monitor stopped")







