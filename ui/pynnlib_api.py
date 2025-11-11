from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Set, TypeAlias


ShapeStrategyType = Literal[
    'static',
    'fixed',
    'dynamic'
]

Hdtype = Literal['fp32', 'fp16', 'bf16', 'int8']

Hdtype = Literal['fp32', 'fp16', 'bf16', 'int8']

NnArchitectureType: TypeAlias = str

class NnFrameworkType(Enum):
    ONNX = 'ONNX'
    PYTORCH = 'PyTorch'
    TENSORRT = 'TensorRT'


@dataclass
class NnFramework:
    type: NnFrameworkType = None
    architectures: OrderedDict[str, NnArchitecture] = None


@dataclass
class SizeConstraint:
    min: tuple[int, int] = None
    max: tuple[int, int] = None
    modulo: int = 1

    def is_size_valid(self, size_or_shape: tuple[int, int, int] | tuple[int, int], is_shape: bool=True) -> bool:
        """Return True if the size is valid.
            The size can be provided as a np.shape (h,w,c) or as a tuple of dims (w, h)
            TODO: verify modulo
            """
        if is_shape:
            h, w = size_or_shape[:2]
        else:
            w, h = size_or_shape[:2]
        if self.min is not None:
            if w < self.min[0] or h < self.min[1]:
                return False
        if self.max is not None:
            if w > self.max[0] or h > self.max[1]:
                return False
        return True


@dataclass
class ShapeStrategy:
    type: ShapeStrategyType = 'dynamic'
    min_size: tuple[int, int] = (0, 0)
    opt_size: tuple[int, int] = (0, 0)
    max_size: tuple[int, int] = (0, 0)

    def __post_init__(self):
        self._modulo: int = 1
    def is_valid(self) -> bool:
        if self.type == 'static':
            if any((x == 0 for x in self.opt_size)):
                return False
        else:
            for d in range(2):
                values = [x[d] for x in (self.min_size, self.opt_size, self.max_size)]
                if min([values[i + 1] - values[i] for i in range(len(values) - 1)]) < 0:
                    return False
        return True
    def is_fixed(self):
        if self.type != 'dynamic':
            return True
        w, h = self.opt_size
        for size in (self.min_size, self.max_size):
            if size[0] != w or size[1] != h:
                return False
        return True


@dataclass
class OnnxConv:
    dtypes: Set[Hdtype] = field(default_factory=set)
    shape_strategy_types: Set[ShapeStrategyType] = field(default_factory=set)


@dataclass
class TensorRTConv:
    dtypes: Set[Hdtype] = field(default_factory=set)
    weak_typing: bool = False
    shape_strategy_types: Set[ShapeStrategyType] = field(default_factory=lambda: {'dynamic', 'fixed', 'static'})


@dataclass
class NnGenericArchitecture:
    name: str = 'unknown'
    type: NnArchitectureType = NnArchitectureType()
    category: str = 'unknown'
    dtypes: list[Hdtype] = field(default_factory=list)
    size_constraint: SizeConstraint = None


@dataclass
class NnPytorchArchitecture(NnGenericArchitecture):
    to_onnx: OnnxConv = None
    to_tensorrt: TensorRTConv = None


@dataclass
class NnOnnxArchitecture(NnGenericArchitecture):
    scale: int | None = None
    to_tensorrt: TensorRTConv = None


@dataclass
class NnTensorrtArchitecture(NnGenericArchitecture):
    version: str = ''


@dataclass
class GenericModel:
    framework: NnFramework = None
    arch: NnArchitecture = None
    alt_arch_name: str = ''
    scale: int = 0
    in_nc: int = 0
    out_nc: int = 0
    io_dtypes: dict[Literal['input', 'output'], Hdtype] = field(default_factory=dict)
    filepath: str = None
    device: str = 'cpu'
    dtypes: list[Hdtype] = field(default_factory=list)
    force_weak_typing: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
    shape_strategy: ShapeStrategy = field(default_factory=ShapeStrategy)
    _arch_name: str = None
    _size_constraint: SizeConstraint | None = None


@dataclass
class OnnxModel(GenericModel):
    opset: int = 21
    alt_arch_name: str = ''
    in_shape_order: str = 'NCHW'
    torch_arch: NnPytorchArchitecture = None


@dataclass
class PyTorchModel(GenericModel):
    num_feat: int = 0
    num_conv: int = 0


@dataclass
class TrtModel(GenericModel):
    engine_version: int = 0
    opset: int = 21
    device: str = ''
    torch_arch: NnPytorchArchitecture = None
    typing: Literal['', 'weak', 'strong'] = ''


NnArchitecture = (
    NnGenericArchitecture
    | NnOnnxArchitecture
    | NnPytorchArchitecture
    | NnTensorrtArchitecture
)

NnModel = OnnxModel | PyTorchModel | TrtModel
