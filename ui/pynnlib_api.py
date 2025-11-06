from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Set, TypeAlias


ShapeStrategyType = Literal[
    # Conversion to:
    #   ONNX: static, opt size must be specified
    #   TensorRT: Static or dynamic Onnx, depends on ONNX strategy, fixed TensorRT shapes
    'static',

    # Only for TensorRT: static or dynamic Onnx, fixed TensorRT shapes
    #   (if used with conversion to ONNX -> static ONNX strategy)
    'fixed',

    # Use dynamic shapes for both ONNX and tensorRT
    'dynamic'
]

Idtype = Literal['fp32', 'fp16', 'bf16', 'int8']

NnModelDtype = Literal['fp32', 'fp16', 'bf16', 'int8']

NnArchitectureType: TypeAlias = str

@dataclass(slots=True)
class SizeConstraint:
    min: tuple[int, int] = None
    max: tuple[int, int] = None
    modulo: int = 1

    def is_size_valid(
        self,
        size_or_shape: tuple[int, int, int] | tuple[int, int],
        is_shape: bool = True
    ) -> bool:
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
    """Shapes: (width, height)
    """
    type: ShapeStrategyType = 'dynamic'
    min_size: tuple[int, int] = (0, 0)
    opt_size: tuple[int, int] = (0, 0)
    max_size: tuple[int, int] = (0, 0)


    def __post_init__(self):
        self._modulo: int = 1


    def is_valid(self) -> bool:
        if self.type == 'static':
            if any(x == 0 for x in self.opt_size):
                return False
        else:
            for d in range(2):
                values = [x[d] for x in (self.min_size, self.opt_size, self.max_size)]
                if min([values[i+1] - values[i] for i in range(len(values)-1)]) < 0:
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


    def __str__(self) -> str:
        class_str = "{\n"
        indent: str = "    "
        for k, v in self.__dict__.items():
            v_str = f"\'{v}\'" if isinstance(v, str) else f"{v}"
            class_str += f"{indent}{indent}{k}: {type(v).__name__} = {v_str}\n"
        class_str += f"{indent}{'}'}\n"
        return class_str

class NnFrameworkType(Enum):
    ONNX = 'ONNX'
    PYTORCH = 'PyTorch'
    TENSORRT = 'TensorRT'

@dataclass(slots=True)
class TensorRTConv:
    # Some archs don't support strong typing,
    #   caution: conversion might fail or slower inference
    dtypes: Set[Idtype] = field(
        # default_factory=lambda: {'fp32', 'fp16', 'bf16'}
        default_factory=set
    )
    weak_typing: bool = False
    shape_strategy_types: Set[ShapeStrategyType] = field(
        default_factory=lambda: {'dynamic', 'fixed', 'static'}
        # default_factory=set
    )

@dataclass(slots=True)
class OnnxConv:
    dtypes: Set[Idtype] = field(
        # default_factory=lambda: {'fp32', 'fp16', 'bf16'}
        default_factory=set
    )
    shape_strategy_types: Set[ShapeStrategyType] = field(
        # default_factory=lambda: {'dynamic', 'static'}
        default_factory=set
    )