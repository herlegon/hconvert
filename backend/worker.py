
import multiprocessing
import os
from typing import Any
from hutils import yellow
from messages import WorkerCommand, WorkerResponse
import multiprocessing
from logger import slog

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


nn_cmd_queue = multiprocessing.Queue()
nn_event_queue = multiprocessing.Queue()


def nnlib_worker(
    cmd_queue: multiprocessing.Queue,
    event_queue: multiprocessing.Queue
):
    """
    Persistent worker for short tasks (<5s).
    """
    in_model: NnModel = None

    while True:
        if True:
        # try:
            cmd: WorkerCommand = cmd_queue.get()
            payload: dict | None = cmd.payload

            if cmd.cmd == "shutdown":
                break


            elif cmd.cmd == "parse":
                response, in_model = parse_model(payload=payload)
                print(yellow("add to queue:"), response)
                event_queue.put(response)


            elif cmd.cmd == "inject":
                # Load the model if not the current one
                in_model_fp = payload.get("in_model_fp")
                if in_model is None or in_model_fp != in_model.filepath:
                    slog.warning("reopen:")
                    device = payload.get("device", "cpu")
                    in_model: NnModel = nnlib.open(
                        in_model_fp,
                        device=device
                    )

                # Inject metadata, get the updated model
                response, in_model = inject_metadata(
                    payload=payload, model=in_model
                )
                event_queue.put(response)


            elif cmd.cmd == "convert":
                settings: dict[str, str | dict[str, Any]] = cmd.payload.get("settings")

                # Load the model if not the current one
                in_model_fp = payload.get("in_model_fp")
                if in_model is None or in_model_fp != in_model.filepath:
                    slog.warning("reopen:")
                    in_model: NnModel = nnlib.open(
                        in_model_fp,
                        device=settings.get('device')
                    )

                # Generate a dict used as arguments for the generation of the filepath
                # and the conversion
                common_kwargs = get_kwargs(model=in_model, settings=settings)

                # Generate the filepath of the converted model
                out_model_fp, exception = get_out_model_fp(payload, model=in_model)
                if exception:
                    event_queue.put(
                        WorkerResponse(type="error", payload=exception)
                    )
                    continue

                event_queue.put(
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
                        save_as(model_fp=out_model_fp, model=in_model)

                    elif to == 'onnx':
                        nnlib.convert_to_onnx(**common_kwargs)

                    elif to == 'tensorrt':
                        nnlib.convert_to_tensorrt(**common_kwargs)

                except Exception as e:
                    exception = str(e)
                    slog.error(exception)
                    response = WorkerResponse(type="error", payload=exception)
                    continue


                event_queue.put(
                    WorkerResponse(
                        type="progress",
                        payload={
                            'state': "ended",
                            'model_fp': out_model_fp
                        }
                    )
                )


        # except Exception as e:
        #     print(f"nnlib_worker: uncaught exception: {str(e)}")
        #     WorkerResponse(
        #         type="error",
        #         payload=f"system: {str(e)}"
        #     )

    print(yellow(f"Terminated nnlib_worker"))


nn_worker = multiprocessing.Process(
    target=nnlib_worker,
    name="nnlib_worker",
    args=(nn_cmd_queue, nn_event_queue),
)
nn_worker.start()

