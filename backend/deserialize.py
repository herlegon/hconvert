from types import SimpleNamespace

from pynnlib import (
    SizeConstraint,
    nnlib,
    NnModel
)



# Mapping of JSON "class" field to actual Python classes
CLASS_MAP = {
    "SizeConstraint": SizeConstraint,
    # Add others if available
    # "ShapeStrategy": ShapeStrategy,
    # "TensorRTConv": TensorRTConv,
}


class GenericObject(SimpleNamespace):
    """Generic object for unknown classes."""
    def __repr__(self):
        cls_name = getattr(self, '_class', 'GenericObject')
        return f"<{cls_name} {dict(self.__dict__)}>"


def from_serializable(obj):
    """
    Convert JSON-loaded dicts/lists into Python objects.
    Uses 'class' to instantiate known classes.
    """
    if isinstance(obj, dict):
        cls_name = obj.get('_class')

        # Determine the target class
        cls = CLASS_MAP.get(cls_name, None)

        if cls is not None:
            # Prepare kwargs for dataclass or class constructor
            kwargs = {
                k: from_serializable(v)
                for k, v in obj.items()
                if k != '_class'
            }
            return cls(**kwargs)
        else:
            # Unknown class -> use GenericObject
            o = GenericObject()
            for k, v in obj.items():
                setattr(o, k, from_serializable(v))
            return o

    elif isinstance(obj, list):
        return [from_serializable(v) for v in obj]

    else:
        return obj
