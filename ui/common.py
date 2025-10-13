from typing import Literal

DEFAULT_SIZE: tuple[int, int] = (720, 540)

PREDEFINED_SIZE: dict[str, tuple[int, int]] = {
    "480p 16:9 (DVD)": (854, 480),
    "480p 4:3": (640, 480),
    "480p NTSC": (720, 480),
    "540p NTSC 4:3 sq": (720, 540),
    "576p 4:3 sq": (768, 576),
    "720p 4:3": (960, 720),
    "720p (HD ready)": (1280, 720),
    "1080p (Full HD)": (1920, 1080),
    "2160p (4K UHDTV)": (3840, 2160)
}

predefined_shapes_inv: dict[str, str] = {
    "x".join(map(str, v)): k for k, v in PREDEFINED_SIZE.items()
}

ShapeStrategyName = Literal['static', 'dynamic', 'fixed']


ONNX_DEFAULT_CONVERSION_SETTINGS: dict[str, str | bool | int | tuple[int, int]] = {
    'version': 20,
    'dtype': 'fp32',
    'shape_strategy': 'static',
    'shape': (720, 540)
}


SUPPORTED_MODEL_EXTENSIONS: tuple[str] = (
    ".engine",
    ".trtzip",
    ".onnx",
    ".pt",
    ".pth",
    ".safetensors",
    ".param",
    ".ncnn",
)
