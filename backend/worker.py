from pprint import pprint
import queue
import signal
from hutils import red, yellow
from logger import slog
from messages import WorkerCommand, WorkerResponse
import multiprocessing as mp
import os
from typing import Any, Literal

from pynnlib import (
    NnModel,
    nnlib,
    save_as,
)
from nnlib_helpers import (
    get_kwargs,
    get_out_model_fp,
    inject_metadata,
    parse_model,
)


WorkerTask = Literal[
    'shutdown',
    'parse',
    'inject',
    'convert',
]
worker_task_list = list(WorkerTask.__args__)

class Worker(mp.Process):
    """Worker process that executes long-running tasks"""
    def __init__(
        self,
        task_queue: mp.Queue,
        result_queue: mp.Queue,
        stop_event: mp.Event
    ):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.stop_event = stop_event

        self.model: NnModel = None


    def run(self):
        # Ignore KeyboardInterrupt inside the worker
        # signal.signal(signal.SIGINT, signal.SIG_IGN)

        print("Worker process started", flush = True)
        slog.info("Worker process started")

        while not self.stop_event.is_set():
            try:
                msg: dict = self.task_queue.get(timeout=1)
                print(f"received: {msg}")
                task_name: WorkerTask = msg['cmd']
                payload: dict | None = msg.get('payload', {})

                # Route to appropriate task handler
                if task_name == 'shutdown':
                    print(yellow("received shutdown"))
                    break

                elif task_name == 'parse':
                    self.handle_parse(payload)

                elif task_name == 'inject':
                    self.handle_inject(payload)

                elif task_name == 'convert':
                    self.handle_convert(payload)

                else:
                    self.send_result(
                        WorkerResponse(
                            type="error",
                            payload=f"Unknown task: {task_name}"
                        )
                    )

            except queue.Empty:
                continue

            except Exception as e:
                print(red(f"nnlib_worker: uncaught exception: {str(e)}"))
                # WorkerResponse(
                #     type="error",
                #     payload=f"system: {str(e)}"
                # )

        print(yellow(f"Terminated nnlib_worker"))



    def send_result(self, response: WorkerResponse):
        """Send result back to server"""
        print("worker: send result:", type(response))
        self.result_queue.put(response)


    def should_stop(self) -> bool:
        """Check if task should stop"""
        return self.stop_event.is_set()


    def handle_parse(self, payload: dict) -> None:
        response, model = parse_model(payload=payload)
        self.model = model
        print(yellow("add to queue:"), response)
        self.send_result(response)


    def handle_inject(self, payload: dict) -> None:
        # Load the model if not the current one
        in_model_fp = payload.get("in_model_fp")
        if self.model is None or in_model_fp != self.model.filepath:
            slog.warning("reopen:")
            device = payload.get("device", "cpu")
            self.model: NnModel = nnlib.open(
                in_model_fp,
                device=device
            )

        # Inject metadata, get the updated model
        response, self.model = inject_metadata(
            payload=payload, model=self.model
        )
        self.send_result(response)


    def handle_convert(self, payload: dict) -> None:
        settings: dict[str, str | dict[str, Any]] = payload.get("settings")

        # Load the model if not the current one
        in_model_fp = payload.get("in_model_fp")
        if self.model is None or in_model_fp != self.model.filepath:
            slog.warning("reopen:")
            self.model: NnModel = nnlib.open(
                in_model_fp,
                device=settings.get('device')
            )

        # Generate a dict used as arguments for the generation of the filepath
        # and the conversion
        common_kwargs = get_kwargs(model=self.model, settings=settings)

        # Generate the filepath of the converted model
        out_model_fp, exception = get_out_model_fp(payload, model=self.model)
        if exception:
            self.send_result(
                WorkerResponse(type="error", payload=exception)
            )
            return

        self.send_result(
            WorkerResponse(
                type="progress",
                payload={
                    'state': "started",
                    'model_fp': out_model_fp
                }
            )
        )

        to: str = settings['to']
        try:
            if to == 'safetensors':
                os.makedirs(settings['out_dir'], exist_ok=True)
                save_as(model_fp=out_model_fp, model=self.model)

            elif to == 'onnx':
                nnlib.convert_to_onnx(**common_kwargs)

            elif to == 'tensorrt':
                nnlib.convert_to_tensorrt(**common_kwargs)

        except Exception as e:
            exception = str(e)
            slog.error(exception)
            self.send_result(WorkerResponse(type="error", payload=exception))
            return

        self.send_result(
            WorkerResponse(
                type="progress",
                payload={
                    'state': "ended",
                    'model_fp': out_model_fp
                }
            )
        )

