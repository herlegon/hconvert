import json
from pprint import pprint
import time
from typing import Any
from serialize import serialize_model
from hutils import get_extension, lightgreen, red
from messages import WorkerResponse
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
)


def parse_model(
    payload: dict[str, str],
) -> tuple[WorkerResponse, NnModel]:
    try:
        model_fp = payload.get("path")
        ext = get_extension(model_fp)
        trt_extensions: tuple[int] = get_supported_model_extensions(NnFrameworkType.TENSORRT)

        device = 'cuda' if ext in trt_extensions else 'cpu'
        start_time = time.time()

        slog.info(f"parse: {model_fp}")
        try:
            model: NnModel = nnlib.open(model_fp, device=device)
            elapsed = time.time() - start_time
            slog.debug(lightgreen(f"parsed in {1000*elapsed:.03f}ms"))
        except Exception as e:
            exception = str(e)
            print(exception)
            slog.exception(exception)
            response = WorkerResponse(type="error", payload=exception)

        model_dto = serialize_model(nn_model=model)
        dto_json = json.dumps(
            model_dto,
            separators=(',', ':'),
            default=lambda o: o.__dict__,
            # indent=2
        )

        response = WorkerResponse(
            type="parsed",
            payload={
                "model": dto_json
            }
        )

    except Exception as e:
        print(red(f"Eception: {str(e)}"))
        response = WorkerResponse(type="error", payload=str(e))

    return response, model



def inject_metadata(
    payload: dict[str, str],
    model: NnModel,
) -> tuple[WorkerResponse, NnModel]:
    """Inject metadat in the model and reload it
    """
    print(red("inject metadata"))
    pprint(payload)
    response: WorkerResponse = None

    metadata = payload.get("metadata", None)
    if metadata is not None and metadata:
        try:
            out_model_fp = payload.get("out_model_fp")
            device = payload.get("device")

            slog.warning(f"save as: {out_model_fp}")
            model.metadata = metadata
            save_as(
                model_fp=out_model_fp,
                model=model,
                autonaming=False
            )

            # Reload model
            slog.warning(f"parse generated model: {out_model_fp}")
            out_model: NnModel = nnlib.open(out_model_fp, device=device)
            model_dto = serialize_model(nn_model=out_model)
            dto_json = json.dumps(
                model_dto,
                separators=(',', ':'),
                default=lambda o: o.__dict__,
                # indent=2
            )
            response = WorkerResponse(
                type="injected",
                payload={
                    "model": dto_json
                }
            )

        except Exception as e:
            response = WorkerResponse(type="error", payload=str(e))
            slog.error(f"exception while injecting metadata\'{str(e)}\'")

    else:
        slog.error(f"No metadata provided")

    return response, out_model



def get_kwargs(
    model: NnModel,
    settings: dict[str, Any]
) -> dict:
    common_kwargs: dict = {}
    args: dict[str, str | dict[str, Any]]

    to: str = settings['to']
    if to == 'onnx':
        args = settings['values']
        device: str = 'cpu'
        if args['dtype'] != 'fp32':
            device = 'cuda:0'

        common_kwargs = dict(
            model=model,
            opset=args['opset'],
            dtype=args['dtype'],
            device=device,
            shape_strategy=ShapeStrategy(
                type=args['shape_strategy'],
                opt_size=args['shape']
            ),
            out_dir=settings['out_dir'],
        )

    elif to == 'tensorrt':
        args = settings['values']

        shape_strategy: ShapeStrategy = ShapeStrategy(
            type=args['shape_strategy'],
            min_size=args['shape_min'],
            opt_size=args['shape_min'],
            max_size=args['shape_min'],
        )

        device = args['gpu']
        device = device if device else "cuda"
        dtype: Idtype = 'fp32'
        if 'fp16' in args['dtypes']:
            dtype = 'fp16'
        elif 'bf16' in args['dtypes']:
            dtype = 'bf16'

        common_kwargs = dict(
            model=model,
            shape_strategy=shape_strategy,
            dtype=dtype,
            force_weak_typing=bool(args['typing'] == 'weak'),
            # optimization_level=,
            opset=args['opset'],
            device=device,
            out_dir=settings['out_dir'],
        )
    return common_kwargs



def get_out_model_fp(
    payload: dict[str, Any],
    model: NnModel,
) -> tuple[str, str]:
    out_model_fp = ""
    exception: str = ""

    try:
        settings: dict[str, Any] = payload.get('settings')

        to: str = settings['to']
        if to == 'safetensors':
            out_model_fp = payload.get("out_model_fp", "")

        elif to == 'onnx':
            common_kwargs = get_kwargs(model=model, settings=settings)
            out_model_fp = generate_out_model_fp(
                to=NnFrameworkType.ONNX, **common_kwargs
            )

        elif to == 'tensorrt':
            common_kwargs = get_kwargs(model=model, settings=settings)
            out_model_fp = generate_out_model_fp(
                to=NnFrameworkType.TENSORRT, **common_kwargs
            )

        else:
            slog.error(f"\'{to}\' is not a supported framework")

    except Exception as e:
        exception = str(e)
        slog.critical(exception)

    return out_model_fp, exception

