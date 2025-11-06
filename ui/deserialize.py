import json
from pprint import pprint
from types import SimpleNamespace

from .pynnlib_api import *



# Mapping of JSON "class" field to actual Python classes
CLASS_MAP = {
    "NnFrameworkType": NnFrameworkType,
    "NnFramework": NnFramework,

    "SizeConstraint": SizeConstraint,
    "ShapeStrategy": ShapeStrategy,
    "OnnxConv": OnnxConv,
    "TensorRTConv": TensorRTConv,

    "PyTorchModel": PyTorchModel,
    "OnnxModel": OnnxModel,
    "TrtModel": TrtModel,
    "NnModel": NnModel,
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
        # Handle enum
        if "_enum" in obj:
            enum_cls = CLASS_MAP[obj["_enum"]]
            return enum_cls(obj["value"])

        cls_name = obj.get('_class', None)
        if cls_name is not None:
            # Determine the target class
            cls = CLASS_MAP.get(cls_name, None)

            if cls is not None:
                # Prepare kwargs for dataclass or class constructor
                kwargs = {
                    k: from_serializable(v)
                    for k, v in obj.items()
                    if k != '_class'
                }
                pprint(kwargs)
                return cls(**kwargs)

        else:
            # If there's no '_class', treat the obj as a simple dict
            return {k: from_serializable(v) for k, v in obj.items()}


        # Unknown class -> use GenericObject
        o = GenericObject()
        for k, v in obj.items():
            setattr(o, k, from_serializable(v))
        return o

    elif isinstance(obj, list):
        return [from_serializable(v) for v in obj]

    else:
        return obj



def deserialize_model(dto_json: str):
    data = json.loads(dto_json)
    return from_serializable(data)

