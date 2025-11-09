from __future__ import annotations

import asyncio
import json
import multiprocessing as mp
import os
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
        server_connection: ServerConnection,
        client_id: str,
        server: BackendServer,
    ):
        """
        websocket: the connected websocket object
        client_id: unique id for this client
        server: reference to the backend server (optional, for broadcasts, etc.)
        """
        # Control flags
        self.closing = False

        # List of asyncio tasks for send/recv loops
        self.tasks = []

        # websocket
        self.server_connection = server_connection
        self.client_id = client_id
        self.server = server

        # Async queues for websocket I/O
        self.to_client = asyncio.Queue()
        self.from_client = asyncio.Queue()

        # Worker management
        self.workers: dict[str, dict[str, Worker]] = {}
        self.stop_event: mp.Event = mp.Event()

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
            async for msg in self.server_connection:
                await self.route_message(msg)

        except asyncio.CancelledError:
            slog.debug(f"[Handler {self.client_id}] Reception task cancelled")
            raise

        except websockets.ConnectionClosedOK:
            slog.info(f"[Handler {self.client_id}] connection closed")

        except websockets.ConnectionClosedError as e:
            slog.warning(f"[Handler {self.client_id}] disconnected with error {e}")

        except Exception as e:
            slog.warning(f"[Handler {self.client_id}] exception while running reception handler {e}")

        finally:
            slog.info(f"[Handler {self.client_id}] Reception task ended")


    async def send_task(self):
        while not self.closing:
            try:
                event: WorkerResponse = await asyncio.wait_for(
                    self.to_client.get(),
                    timeout=0.5
                )
                msg: dict = {
                    "type": event.type,
                    "payload": event.payload
                }
                await self.server_connection.send(json.dumps(msg))

            except asyncio.TimeoutError:
                continue

            except asyncio.CancelledError:
                slog.debug(f"[Handler {self.client_id}] Sending task cancelled")
                raise

            except websockets.ConnectionClosed:
                slog.info(f"[Handler {self.client_id}] Connection closed while sending")
                self.running = False
                break

            except Exception as e:
                slog.error(f"[Handler {self.client_id}] Failed to send message: {e}")

        slog.info(f"[Handler {self.client_id}] Send task ended")


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
            await self.close()

        slog.info(f"[Handler {self.client_id}] Handler ended")



    async def shutdown_websocket(self):
        """Stop all tasks and workers for this client."""
        if self.closing:
            slog.info(f"[Handler {self.client_id}] Already closing")
            return

        self.closing = True

        # Optional: notify client of shutdown
        # try:
        #     shutdown_msg = WorkerResponse(
        #         type="shutdown",
        #         payload="Server is shutting down"
        #     )
        #     await asyncio.wait_for(
        #         self.server_connection.send(json.dumps({
        #             "type": shutdown_msg.type,
        #             "payload": shutdown_msg.payload
        #         })),
        #         timeout=1.0
        #     )
        #     slog.info(f"[Handler {self.client_id}] Sent shutdown notification to client")
        # except (websockets.ConnectionClosed, asyncio.TimeoutError):
        #     slog.info(f"[Handler {self.client_id}] Client already disconnected")
        # except Exception as e:
        #     slog.warning(f"[Handler {self.client_id}] Failed to send shutdown message: {e}")

        # Close the websocket connection
        try:
            await asyncio.wait_for(
                self.server_connection.close(code=1000, reason="Server shutting down"),
                timeout=1.0
            )
            slog.info(f"[Handler {self.client_id}] WebSocket closed")

        except asyncio.TimeoutError:
            slog.warning(f"[Handler {self.client_id}] WebSocket close timed out")

        except Exception as e:
            slog.warning(f"[Handler {self.client_id}] Error closing WebSocket: {e}")

        await asyncio.sleep(0.05)

        # Cancel all running tasks
        if self.tasks:
            for t in self.tasks:
                if not t.done():
                    t.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()

        # Cancel async tasks individually with error handling
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
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                slog.warning(f"[Handler {self.client_id}] Task cancellation timed out")
            except Exception as e:
                slog.warning(f"[Handler {self.client_id}] Error gathering tasks: {e}")

            slog.info(f"[Handler {self.client_id}] All async tasks stopped")


        # Step 5: Stop all workers gracefully
        await self.stop_workers()

        slog.info(f"[Handler {self.client_id}] Stop sequence complete")



    def start_worker(self, name: str):
        """
        Create and start a worker process.
        """
        if name in self.workers and self.workers[name]['worker'].is_alive():
            print(f"Worker {name} already running")
            return

        task_queue = mp.Queue()
        result_queues = mp.Queue()
        try:
            worker = Worker(
                task_queue=task_queue,
                result_queue=result_queues,
                stop_event=self.stop_event
            )
            worker.start()
        except Exception as e:
            slog.error(f"Failed to start worker \'{name}\'")
            return

        self.workers[name] = {
            'worker': worker,
            'task_queue': task_queue,
            'result_queues': result_queues,
        }

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



    def stop_worker(self, name: str, timeout: float = 2.0):
        """
        Attempt to gracefully stop a single worker process.
        Blocks for up to `timeout` seconds.
        """
        slog.info(f"Stopping worker {name}...")

        w = self.workers.get(name)
        if not w:
            return f"{name}: no such worker"

        worker: Worker = w['worker']
        worker.join(timeout=timeout)

        # If it's still alive, kill it hard
        if worker.is_alive():
            slog.warning(f"Force killing worker {name}")
            worker.terminate()
            worker.join(timeout=timeout + 1)

            if worker.is_alive():
                import signal
                slog.warning(f"SIGKILLing stubborn worker {name}")
                os.kill(worker.pid, signal.SIGKILL)

        del self.workers[name]

        # Cleanup
        try:
            worker.close()
        except Exception:
            pass


    async def stop_workers(self):
        """Stop all worker processes gracefully"""
        if self.closing or not self.workers:
            return

        slog.info(f"[Handler {self.client_id}] Stopping {len(self.workers)} worker(s)")
        # Immediately set the shared event
        self.stop_event.set()

        # Send shutdown to all queues quickly (non-blocking)
        for w in self.workers.values():
            try:
                w['task_queue'].put_nowait({'cmd': 'shutdown'})
            except Exception:
                pass

        # Stop each worker in parallel (force kill if needed)
        timeout: float = 1.
        loop = asyncio.get_running_loop()
        worker_names = list(self.workers.items())
        tasks = [
            loop.run_in_executor(None, self.stop_worker, name, timeout)
            for name in worker_names
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                print(f"Worker stop error: {res}")
            else:
                print(res)

        print("All workers stopped.")


    async def close(self):
        # Run websocket shutdown and worker stop in parallel
        print(yellow(f"Close handler: {self.client_id}"))
        await asyncio.gather(
            self.shutdown_websocket(),
            self.stop_workers(),
            return_exceptions=True
        )

        slog.info(f"[Handler {self.client_id}] Handler fully closed")
















