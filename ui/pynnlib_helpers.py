from typing import Type
from .pynnlib_api import (
    NnFrameworkType,
    SizeConstraint,
)


def get_arch_name(model: object) -> str:
    if model.alt_arch_name:
        return model.alt_arch_name
    if model.arch is None and not model._arch_name:
        return "unknown"
    elif model._arch_name:
        return model._arch_name
    return model.arch.name


def get_size_constraint(model: object) -> SizeConstraint:
    return (
        model.arch.size_constraint
        if model._size_constraint is None
        else model._size_constraint
    )


def swap_keys_values(d: Type[dict]) -> Type[dict]:
    """Swap keys/value of a dict.
    Warning, it owerwrites a key, value pair if already exists"""
    swapped: Type[dict] = type(d)()
    for k, v in d.items():
        if isinstance(v, list):
            swapped.update({x: k for x in v})
        else:
            swapped[v] = k
    return swapped



framework_to_extensions: dict[NnFrameworkType, list[str]] = {
    NnFrameworkType.ONNX : ['.onnx'],
    NnFrameworkType.PYTORCH : ['.pt', '.pth', '.ckpt', '.safetensors'],
    NnFrameworkType.TENSORRT : ['.engine', '.trtzip'],
}
extensions_to_framework: dict[str, NnFrameworkType] = swap_keys_values(framework_to_extensions)

def get_supported_model_extensions(framework: NnFrameworkType | None = None) -> tuple[int]:
    if framework is None:
        return tuple(extensions_to_framework.keys())
    return tuple(framework_to_extensions[framework])

