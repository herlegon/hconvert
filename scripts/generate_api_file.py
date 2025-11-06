import inspect
import os
from pathlib import Path
import re
from typing import List, Type
from hutils import absolute_path
import pynnlib
import ast
import importlib
import inspect
import os
from pathlib import Path
import pkgutil
import sys
from typing import Optional, Dict, List, Type

from hutils import absolute_path, lightgreen
from pynnlib import (
    PyTorchModel,
)
import pynnlib
from pynnlib.framework import NnFramework
from pynnlib.architecture import (
    NnPytorchArchitecture,
    NnOnnxArchitecture,
    NnTensorrtArchitecture,
)


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
    OnnxConv,
)

TARGET_CLASSES_2: tuple[Type] = (
    NnPytorchArchitecture,
    NnOnnxArchitecture,
    NnTensorrtArchitecture,
    TensorRTConv,

)
TYPE_ALIASES = (
    "ShapeStrategyType",
    "Idtype",
    "NnModelDtype",
    "NnArchitecture",
    "NnArchitectureType",
)

EXCLUDE_FIELDS = (
    "_caller_dir",
    "detection_keys",
    "fct",
    "build_fn",
    "convert_fn",
    "state_dict",
    "model_proto",
    "engine",
    "ModuleClass",
    "executor",
    "module",
    "infer_type",
    "parse",
    "detect",
    "create_session",
)



def find_class_source_path(cls):
    """Import a class from pynnlib and return its file path."""
    if isinstance(cls, str):
        class_name = cls

        # First, try to get it directly from pynnlib (if it's in __init__.py or __all__)
        try:
            cls = getattr(pynnlib, class_name, None)
            if cls and inspect.isclass(cls):
                filepath = inspect.getfile(cls)
                print(f"✅ Found '{class_name}' directly in pynnlib")
                return filepath
        except Exception as e:
            print(f"⚠️  Could not check pynnlib directly: {e}")

        # Recursively search all submodules
        for importer, modname, ispkg in pkgutil.walk_packages(
            pynnlib.__path__,
            pynnlib.__name__ + "."
        ):
            print(f"  Checking module: {modname}")
            try:
                mod = importlib.import_module(modname)
                cls = getattr(mod, class_name, None)

                if cls and inspect.isclass(cls):
                    filepath = inspect.getfile(cls)
                    print(f"✅ Found '{class_name}' in {modname}")
                    return filepath

            except ImportError as e:
                print(f"  ⚠️  Could not import {modname}: {e}")
                continue
            except Exception as e:
                print(f"  ⚠️  Error checking {modname}: {e}")
                continue

        sys.exit(f"❌ Could not find class '{class_name}' in the pynnlib package (searched recursively).")

    # If it's already a class object, just get its file directly
    else:
        if not inspect.isclass(cls):
            raise TypeError(f"Expected a class or string, got {type(cls)}")
        return inspect.getfile(cls)





def find_literal_alias_file(alias_name: str, base_path=None):
    """Scan pynnlib source files for the alias definition (Literal or TypeAlias)."""
    if base_path is None:
        base_path = Path(pynnlib.__file__).parent

    for py_file in base_path.rglob("*.py"):
        with open(py_file, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped.startswith(alias_name):
                    continue
                if stripped.startswith("#") or stripped.startswith("from ") or stripped.startswith("import "):
                    continue
                if any(tok in stripped for tok in ("TypeAlias", "Literal", "=")):
                    return py_file
    return None



def get_alias_source(name: str, file_path: str) -> str:
    """Extract the full definition of a type alias, including multi-line Literals."""
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

    line = lines[start]

    # One-line alias
    if "[" not in line and "]" not in line:
        return line.strip()

    # Multi-line Literal
    alias_lines = []
    bracket_depth = 0
    for line in lines[start:]:
        alias_lines.append(line)
        bracket_depth += line.count("[")
        bracket_depth -= line.count("]")
        if bracket_depth == 0 and alias_lines:
            break
    return "".join(alias_lines).rstrip()



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



def parse_classes(source: str) -> Dict[str, ast.ClassDef]:
    """Return a mapping of all class names to their AST definitions."""
    tree = ast.parse(source)
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = node
    return classes


def extract_field_defs(class_node: ast.ClassDef) -> List[str]:
    """Return a list of dataclass field definitions from a class AST node."""
    fields = []
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign):
            # annotated assignment: e.g., x: int = 0
            target = stmt.target.id if isinstance(stmt.target, ast.Name) else None
            if target:
                ann = ast.unparse(stmt.annotation).strip()
                if stmt.value:
                    val = ast.unparse(stmt.value).strip()
                    fields.append(f"    {target}: {ann} = {val}")
                else:
                    fields.append(f"    {target}: {ann}")
        elif isinstance(stmt, ast.Assign):
            # plain assignment: e.g., x = 0
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if not targets:
                continue
            val = ast.unparse(stmt.value).strip() if stmt.value else "None"
            for t in targets:
                fields.append(f"    {t}: Any = {val}")
    return fields


def generate_clean_class(source: str, class_name: str, exclude=None) -> str:
    """Generate a clean dataclass definition including inherited fields."""
    exclude = set(exclude or [])
    class_map = parse_classes(source)
    if class_name not in class_map:
        raise ValueError(f"Class '{class_name}' not found in source file.")


    # Extract only *this* class's own fields (no recursion)
    node = class_map[class_name]
    class_fields = extract_field_defs(node)

    # inherance
    # class_fields = resolve_inheritance(class_name, class_map)

    filtered_fields = [
        line for line in class_fields
        if not any(line.strip().startswith(f"{name}:") for name in exclude)
    ]

    lines = []
    lines.append(f"@dataclass")
    lines.append(f"class {class_name}:")
    if filtered_fields:
        lines.extend(filtered_fields)
    else:
        lines.append("    pass")

    return "\n".join(lines) + "\n\n"




def main():
    imports = """from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Set, TypeAlias
"""

    sources: List[str] = []

    # --- Extract type aliases ---
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


    # --- Extract classes ---
    for cls in TARGET_CLASSES:
        sources.append(get_class_source(cls, exclude=list(EXCLUDE_FIELDS)))


    for cls in TARGET_CLASSES_2:
        filepath = find_class_source_path(cls)
        print(f" Get filepath for {cls}: {filepath}")

        with open(filepath, "r") as f:
            source = f.read()
        sources.append(
            generate_clean_class(
                source,
                class_name=cls.__name__,
                exclude=list(EXCLUDE_FIELDS)
            )
        )


    # --- Generate API content ---
    api_content = imports + "\n\n" + "\n\n".join(sources) + "\n"


    # --- Write API file ---
    api_file_path = absolute_path(
        os.path.join(__file__, os.pardir, os.pardir, "ui", "pynnlib_api.py")
    )
    with open(api_file_path, "w") as f:
        f.write(api_content)

    print(f"API file '{api_file_path}' created successfully!")

if __name__ == "__main__":
    main()
