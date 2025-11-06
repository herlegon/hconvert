from dataclasses import dataclass, field

from .pynnlib_api import *

@dataclass
class NnPytorchArchitecture:
    name: str = 'unknown'
    type: NnArchitectureType = NnArchitectureType()
    category: str = 'unknown'
    dtypes: list[Idtype] = field(default_factory=list)
    size_constraint: SizeConstraint = None
    _locked: bool = field(default=False, init=False, repr=False)
    detection_keys: tuple[str | tuple[str]] | dict = field(default_factory=tuple)
    to_onnx: OnnxConv = None
    to_tensorrt: TensorRTConv = None
    _caller_dir: str = ''