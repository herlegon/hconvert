from .pynnlib_api import SizeConstraint


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
