from typing import Type

from hutils import swap_keys_values
from .pynnlib_api import (
    NnFrameworkType,
    SizeConstraint,
    NnModel,
)


def get_arch_name(model: NnModel) -> str:
    if model.alt_arch_name:
        return model.alt_arch_name
    if model.arch is None and not model._arch_name:
        return "unknown"
    elif model._arch_name:
        return model._arch_name
    return model.arch.name


def get_size_constraint(model: NnModel) -> SizeConstraint:
    return (
        model.arch.size_constraint
        if model._size_constraint is None
        else model._size_constraint
    )


framework_to_extensions: dict[NnFrameworkType, list[str]] = {
    NnFrameworkType.ONNX : ['.onnx'],
    NnFrameworkType.PYTORCH : ['.pt', '.pth', '.ckpt', '.safetensors'],
    NnFrameworkType.TENSORRT : ['.engine', '.trtzip'],
}
extensions_to_framework: dict[str, NnFrameworkType] = swap_keys_values(framework_to_extensions)

def get_supported_model_extensions(framework: NnFrameworkType | None = None) -> tuple[str, ...]:
    if framework is None:
        return tuple(extensions_to_framework.keys())
    return tuple(framework_to_extensions[framework])
