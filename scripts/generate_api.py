import inspect
import os
from pathlib import Path
import re
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
from pynnlib.architecture import (
    NnArchitectureType,
    OnnxConv,
    TensorRTConv,
)


TARGET_CLASSES: tuple[Type] = (
    SizeConstraint,
    ShapeStrategy,
    NnFrameworkType,
    TensorRTConv,
    OnnxConv,
)
TYPE_ALIASES = (
    "ShapeStrategyType",
    "Idtype",
    "NnModelDtype",
    "NnArchitecture",
    "NnArchitectureType",
)

import re

def get_class_source(cls: Type, exclude: list[str] | None = None) -> str:
    """
    Return the source code for a class/dataclass, skipping:
      - fields typed as Callable[…]
      - fields whose names appear in the exclude list
    """
    exclude = exclude or []
    try:
        src = inspect.getsource(cls)
    except OSError:
        raise RuntimeError(f"Cannot extract source for class {cls.__name__}")

    lines = src.splitlines()
    cleaned = []
    skip_mode = False
    bracket_depth = 0
    paren_depth = 0

    for line in lines:
        stripped = line.strip()

        # --- Check if this line should trigger skip mode ---
        if not skip_mode:
            # Skip if field name matches one in exclude list
            for name in exclude:
                # matches e.g. "fct:" or "fct ="
                if re.match(rf"^{name}\s*[:=]", stripped):
                    skip_mode = True
                    bracket_depth = line.count("[") - line.count("]")
                    paren_depth = line.count("(") - line.count(")")
                    break

            # Skip if this line declares a Callable[…]
            if not skip_mode and re.search(r":\s*Callable\[", line):
                skip_mode = True
                bracket_depth = line.count("[") - line.count("]")
                paren_depth = line.count("(") - line.count(")")
                continue

            if skip_mode:
                continue  # already entering skip mode, don't append this line
            else:
                cleaned.append(line)
                continue

        # --- We're inside a skipped field (multi-line) ---
        bracket_depth += line.count("[") - line.count("]")
        paren_depth += line.count("(") - line.count(")")

        # Stop skipping once both are balanced and the line ends the field
        if bracket_depth <= 0 and paren_depth <= 0 and re.search(r"=\s*None|field\(", line):
            skip_mode = False
        continue

    return "\n".join(cleaned)




def find_literal_alias_file(alias_name: str, base_path=None):
    """Scan pynnlib source files for the alias definition (Literal[...] or TypeAlias)."""
    if base_path is None:
        base_path = Path(pynnlib.__file__).parent

    for py_file in base_path.rglob("*.py"):
        with open(py_file, "r") as f:
            for line in f:
                stripped = line.strip()
                # Must start with the alias name
                if not stripped.startswith(alias_name):
                    continue
                # Ignore comments and imports
                if stripped.startswith("#") or stripped.startswith("from ") or stripped.startswith("import "):
                    continue
                # Match typical alias definition patterns
                if any(tok in stripped for tok in ("TypeAlias", "Literal", "=")):
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

    alias_lines = []
    line = lines[start]

    # Case 1: one-line alias like "NnArchitectureType: TypeAlias = str"
    if "[" not in line and "]" not in line:
        return line.strip()

    # Case 2: multi-line Literal[...]
    bracket_depth = 0
    for line in lines[start:]:
        alias_lines.append(line)
        bracket_depth += line.count("[")
        bracket_depth -= line.count("]")
        if bracket_depth == 0 and alias_lines:
            break

    return "".join(alias_lines).rstrip()


# --- Generate API content ---
imports = """from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Set, TypeAlias
"""

sources: List[str] = []

# Extract type aliases
seen_aliases = set()
for name in TYPE_ALIASES:
    file_path = find_literal_alias_file(name)
    if not file_path:
        print(f"[W] Alias {name} not found.")
        continue
    alias_src = get_alias_source(name, file_path).strip()
    if alias_src not in seen_aliases:
        sources.append(alias_src)
        seen_aliases.add(alias_src)

# Extract classes
exclude = (
    "_caller_dir",
    "detection_keys",
)
for cls in TARGET_CLASSES:
    sources.append(get_class_source(cls, exclude=exclude))


api_content = imports + "\n\n" + "\n\n".join(sources)

# --- Write API file ---
api_file_path = absolute_path(
    os.path.join(__file__, os.pardir, os.pardir, "ui", "pynnlib_api.py")
)
with open(api_file_path, "w") as f:
    f.write(api_content)

print(f"API file '{api_file_path}' created successfully!")
