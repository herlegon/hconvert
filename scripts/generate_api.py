import inspect
import os
from pathlib import Path
from typing import List, Type
from hutils import absolute_path
import pynnlib

# --- Dataclasses / classes to extract ---
from pynnlib import (
    SizeConstraint,
    ShapeStrategy,
    ShapeStrategyType,
    NnFrameworkType,
    Idtype,
)
from pynnlib.architecture import TensorRTConv


TARGET_CLASSES: tuple[Type] = (
    SizeConstraint,
    ShapeStrategy,
    NnFrameworkType,
    TensorRTConv,
)
TYPE_ALIASES = (
    "ShapeStrategyType",
    "Idtype",
)


# --- Helper functions ---
def get_class_source(cls: Type) -> str:
    """Return the source code for a class/dataclass."""
    try:
        return inspect.getsource(cls)
    except OSError:
        raise RuntimeError(f"Cannot extract source for class {cls.__name__}")



def find_literal_alias_file(alias_name: str, base_path=None):
    """Scan pynnlib source files for the alias definition."""
    if base_path is None:
        base_path = Path(pynnlib.__file__).parent

    for py_file in base_path.rglob("*.py"):
        with open(py_file, "r") as f:
            for line in f:
                if line.strip().startswith(alias_name):
                    return py_file
    return None


def get_alias_source(name: str, file_path: str) -> str:
    """Extract the full definition of a type alias (supports multi-line Literals with comments)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File for alias {name} not found: {file_path}")

    with path.open("r") as f:
        lines = f.readlines()

    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(name):
            start = i
            break
    if start is None:
        raise RuntimeError(f"Alias {name} not found in {file_path}")

    # Capture lines until brackets are balanced
    alias_lines = []
    bracket_depth = 0
    capturing = False
    for line in lines[start:]:
        alias_lines.append(line)
        if "[" in line:
            bracket_depth += line.count("[")
            capturing = True
        if "]" in line:
            bracket_depth -= line.count("]")
        if capturing and bracket_depth == 0:
            break

    return "".join(alias_lines)



# --- Generate API content ---
imports = """from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Set
"""

sources: List[str] = []

# Extract type aliases
for name in TYPE_ALIASES:
    file_path = find_literal_alias_file(name)
    sources.append(get_alias_source(name, file_path))

# Extract classes
for cls in TARGET_CLASSES:
    sources.append(get_class_source(cls))


api_content = imports + "\n\n" + "\n\n".join(sources)

# --- Write API file ---
api_file_path = absolute_path(os.path.join("ui", "pynnlib_api.py"))
with open(api_file_path, "w") as f:
    f.write(api_content)

print(f"API file '{api_file_path}' created successfully!")
