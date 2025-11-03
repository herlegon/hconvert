
from dataclasses import is_dataclass, fields
import enum
from pprint import pprint
from pynnlib import (
    NnModel,
)


EXCLUDED_KEYS: tuple[str] = (
    "state_dict",
    "engine",
    "model_proto",
    "executor",
    "module_class",
    "architectures",
    "detection_keys",
    "module",
)



def to_serializable(value, _visited=None):
    """Convert a value to a serializable form."""
    if value is None:
        return None

    # Scalars (never circular)
    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, enum.Enum):
        return str(value.value)

    if callable(value):
        return None

    if isinstance(value, tuple):
        return [to_serializable(v, _visited) for v in value]


    # Prevent infinite recursion
    if _visited is None:
        _visited = set()

    obj_id = id(value)
    if obj_id in _visited:
        return f"<circular_ref:{type(value).__name__}>"
    _visited.add(obj_id)


    if isinstance(value, (list, set)):
        return [to_serializable(v, _visited) for v in value]

    if isinstance(value, dict):
        return {
            k: to_serializable(v, _visited)
            for k, v in value.items()
            if k not in EXCLUDED_KEYS
        }

    # --- Dataclasses (slots or not) ---
    if is_dataclass(value):
        data = {}
        data["_class"] = type(value).__name__
        for f in fields(value):
            if f.name in EXCLUDED_KEYS:
                continue
            v = getattr(value, f.name)
            if callable(v):
                continue
            data[f.name] = to_serializable(v, _visited)
        return data

    # --- Generic objects ---
    if hasattr(value, "__dict__"):
        data = {}
        for k, v in vars(value).items():
            if k in EXCLUDED_KEYS or callable(v):
                continue
            data[k] = to_serializable(v, _visited)
        return data

    # Fallback
    return str(value)



def serialize_model(nn_model: NnModel) -> dict:
    if hasattr(nn_model, "__dataclass_fields__"):
        fields = nn_model.__dataclass_fields__.keys()
    else:
        fields = nn_model.__dict__.keys()

    base = {
        key: to_serializable(getattr(nn_model, key))
        for key in fields
        if key not in EXCLUDED_KEYS
    }
    base["_class"] = type(nn_model).__name__




    return base

