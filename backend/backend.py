import json
from pprint import pprint
from deserialize import from_serializable
from serializers import serialize_model
from pynnlib import (
    SizeConstraint,
    nnlib,
    NnModel
)


# -------------------------------
# Main program
# -------------------------------
import sys


# Mapping of JSON "class" field to actual Python classes
CLASS_MAP = {
    "SizeConstraint": SizeConstraint,
    # Add others if available
    # "ShapeStrategy": ShapeStrategy,
    # "TensorRTConv": TensorRTConv,
}


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <model_file>")
        sys.exit(1)

    model_fp = sys.argv[1]
    model: NnModel = nnlib.open(model_fp)

    model_dto = serialize_model(nn_model=model)
    pprint(model_dto)
    print("-" * 60)

    # Convert dataclass to JSON
    dto_json = json.dumps(
        model_dto,
        separators=(',', ':'),
        default=lambda o: o.__dict__,
        # indent=2
    )
    print(dto_json)
    print("-" * 60)


    # Load JSON
    data = json.loads(dto_json)

    # Convert to objects
    model_obj = from_serializable(data)

    # Access attributes dynamically
    print(model_obj._class)            # "PyTorchModel"
    print(model_obj.arch.name)        # "RealESRGAN (Compact)"
    print(model_obj.shape_strategy.min_size)  # [0, 0]

    print(model_obj.framework.type)

    # Debug
    print(model_obj)

    # Access known-class attributes
    print(model_obj.arch.size_constraint.min)  # Should be a tuple, e.g. [64, 64]
    print(type(model_obj.arch.size_constraint))  # <class '__main__.SizeConstraint'>


if __name__ == "__main__":
    main()

