from hutils import lightgreen, red, yellow
import json
import os
from pprint import pprint
import sys

if not os.path.exists("ui"):
    root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    if os.path.exists(os.path.join(root_path, "ui")):
        sys.path.append(root_path)

from backend.serialize import serialize_model
from ui.deserialize import deserialize_model
from ui.pynnlib_api import (
    SizeConstraint,
    NnFrameworkType,
    NnModel,
)

from pynnlib import nnlib


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
    model_obj = deserialize_model(dto_json)

    # Access attributes dynamically
    # print(model_obj._class)            # "PyTorchModel"
    print(model_obj.arch.name)        # "RealESRGAN (Compact)"
    print(model_obj.shape_strategy.min_size)  # [0, 0]

    print(model_obj.framework.type)
    fwk_type: NnFrameworkType = model_obj.framework.type
    if fwk_type.value == NnFrameworkType.PYTORCH.value:
        print(yellow("ok"))
    else:
        print(red("failed"))

    if fwk_type == NnFrameworkType.PYTORCH:
        print(lightgreen("oh YEAAAAAHHHHH"))
    else:
        print(red("failed"))

    # Debug
    pprint(model_obj)

    # Access known-class attributes
    size_constraint: SizeConstraint = model_obj.arch.size_constraint
    print(size_constraint.min)  # Should be a tuple, e.g. [64, 64]

    print(str(model.framework.type.value))


if __name__ == "__main__":
    main()

