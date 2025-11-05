import json
import multiprocessing
import time
from serialize import serialize_model
from hutils import get_extension, lightgreen, yellow
from messages import WorkerCommand, WorkerEvent
import multiprocessing
from logger import slog

from pynnlib import (
    generate_out_model_fp,
    get_supported_model_extensions,
    Idtype,
    NnModel,
    nnlib,
    NnFrameworkType,
    save_as,
    ShapeStrategy,
    ShapeStrategyType,
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
        try:
            cmd: WorkerCommand = cmd_queue.get()
            if cmd.cmd == "shutdown":
                break

            elif cmd.cmd == "parse":
                try:
                    model_fp = cmd.payload.get("path")
                    ext = get_extension(model_fp)
                    trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)

                    device = 'cuda' if ext in trt_extensions else 'cpu'
                    start_time = time.time()

                    slog.info(f"parse: {model_fp}")
                    try:
                        in_model: NnModel = nnlib.open(model_fp, device=device)
                        elapsed = time.time() - start_time
                        slog.debug(lightgreen(f"parsed in {1000*elapsed:.03f}ms"))
                    except Exception as e:
                        exception = str(e)
                        print(exception)
                        slog.exception(exception)
                        event_queue.put(WorkerEvent(type="error", data=exception))

                    model_dto = serialize_model(nn_model=in_model)
                    dto_json = json.dumps(
                        model_dto,
                        separators=(',', ':'),
                        default=lambda o: o.__dict__,
                        # indent=2
                    )

                    # Send back to the asyncio loop
                    event_queue.put(WorkerEvent(
                        type="parsed",
                        data={
                            "model": dto_json
                        }
                    ))

                except Exception as e:
                    event_queue.put(WorkerEvent(type="error", data=str(e)))

        except Exception as e:
            print(f"uncaught exception: {str(e)}")
    print(yellow(f"Terminated nnlib_worker"))


nn_worker = multiprocessing.Process(
    target=nnlib_worker,
    name="nnlib_worker",
    args=(nn_cmd_queue, nn_event_queue),
)
nn_worker.start()


