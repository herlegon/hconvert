#!/usr/bin/env python3
"""
Extract dataclass field definitions (variables only) from a Python file,
including inherited fields from parent dataclasses.

Example:
    python extract_dataclass_fields_recursive.py models.py PyTorchModel
"""

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


def find_class_source(cls):
    """Import a class from pynnlib and return its file path."""
    if isinstance(cls, str):
        class_name = cls
        try:
            import pynnlib
        except ImportError as e:
            sys.exit(f"❌ Could not import pynnlib package. Make sure it's in PYTHONPATH.\nError: {e}")

        print(f"🔍 Searching for class '{class_name}' in pynnlib...")
        print(f"📦 Package path: {pynnlib.__path__}")

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


# --- Helper functions ---
def get_class_source(cls: Type) -> str:
    """Return the source code for a class/dataclass."""
    try:
        return inspect.getsource(cls)
    except OSError:
        raise RuntimeError(f"Cannot extract source for class {cls.__name__}")



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


def extract_imports(source: str) -> List[str]:
    """Keep top-level import statements."""
    lines = []
    for line in source.splitlines():
        if line.strip().startswith(("import ", "from ")):
            lines.append(line)
    return lines


def resolve_inheritance(
    class_name: str, class_map: Dict[str, ast.ClassDef], visited=None
) -> List[str]:
    """Recursively collect all field definitions from a dataclass and its bases."""
    if visited is None:
        visited = set()
    if class_name in visited:
        return []  # prevent circular references
    visited.add(class_name)

    if class_name not in class_map:
        return []

    node = class_map[class_name]
    fields = []

    # Resolve base classes recursively
    for base in node.bases:
        if isinstance(base, ast.Name):
            base_name = base.id
        elif isinstance(base, ast.Attribute):
            base_name = base.attr
        else:
            continue

        if base_name in class_map:
            fields.extend(resolve_inheritance(base_name, class_map, visited))

    # Add this class's own fields last (to allow override)
    fields.extend(extract_field_defs(node))

    return fields


def generate_clean_class(source: str, class_name: str, exclude_fields=None) -> str:
    """Generate a clean dataclass definition including inherited fields."""
    exclude_fields = set(exclude_fields or [])
    class_map = parse_classes(source)
    if class_name not in class_map:
        raise ValueError(f"Class '{class_name}' not found in source file.")

    # imports = extract_imports(source)
    all_fields = resolve_inheritance(class_name, class_map)

    # Filter out excluded fields
    filtered_fields = [
        line for line in all_fields
        if not any(line.strip().startswith(f"{name}:") for name in exclude_fields)
    ]

    lines = []
    # if imports:
    #     lines.extend(imports)
    #     lines.append("")

    lines.append("from dataclasses import dataclass, field\n")
    lines.append("from .pynnlib_api import *\n")



    lines.append(f"@dataclass")
    lines.append(f"class {class_name}:")
    if filtered_fields:
        lines.extend(filtered_fields)
    else:
        lines.append("    pass")

    return "\n".join(lines)


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

def main():
    # if len(sys.argv) < 3:
    #     print("Usage: extract_dataclass_fields_recursive.py <source.py> <ClassName>")
    #     sys.exit(1)

    # path = sys.argv[1]
    # class_name = sys.argv[2]
    exclude_fields = (
        'state_dict',
        'model_proto',
        'engine',
        'ModuleClass',
        'executor',
        'module',
        'infer_type',
        'parse',
        'detect',
        'create_session',
    )

    TARGET_CLASSES: tuple[Type] = (
        NnPytorchArchitecture,
        # NnArchitecture,
        # NnFramework,
        # PyTorchModel,
    )

    api_classes_file_path = absolute_path(
        os.path.join(__file__, os.pardir, os.pardir, "ui", "pynnlib_classes.py")
    )
    print(api_classes_file_path)

    api_contents: list[str] = []
    for cls in TARGET_CLASSES:
        filepath = find_class_source(cls)

        with open(filepath, "r") as f:
            source = f.read()
        api_contents.append(generate_clean_class(source, cls.__name__, exclude_fields))

    with open(api_classes_file_path, "w") as f:
        f.write("\n".join(api_contents))

    print(f"API file '{api_classes_file_path}' created successfully!")




if __name__ == "__main__":
    main()
