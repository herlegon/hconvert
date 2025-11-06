from dataclasses import dataclass, field
from .pynnlib_api import *


@dataclass
class NnPytorchArchitecture:
    detection_keys: tuple[str | tuple[str]] | dict = field(default_factory=tuple)
    to_onnx: OnnxConv = None
    to_tensorrt: TensorRTConv = None
    _caller_dir: str = ''


@dataclass
class NnOnnxArchitecture:
    scale: int | None = None
    to_tensorrt: TensorRTConv = None


@dataclass
class NnTensorrtArchitecture:
    version: str = ''

