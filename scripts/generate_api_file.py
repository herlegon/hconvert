from collections.abc import Set
import inspect
import os
from pathlib import Path
import re
import pynnlib
import ast
from typing import Type

from hutils import absolute_path, lightgreen

import pynnlib
from pynnlib import (
    SizeConstraint,
    ShapeStrategy,
    ShapeStrategyType,
    NnFrameworkType,
    Idtype,
    OnnxModel,
    PyTorchModel,
    TrtModel,
)
from pynnlib.framework import (
    NnFramework,
)
from pynnlib.architecture import (
    NnPytorchArchitecture,
    NnOnnxArchitecture,
    NnTensorrtArchitecture,
    NnGenericArchitecture,
)
from pynnlib.architecture import (
    NnArchitectureType,
    OnnxConv,
    TensorRTConv,
)
from pynnlib.model import GenericModel


TARGET_CLASSES: tuple[tuple[Type, bool]] = (
    (NnFrameworkType, False),
    (NnFramework, False),
    (SizeConstraint, True),
    (ShapeStrategy, True),

    (OnnxConv, False),
    (TensorRTConv, False),

    (NnPytorchArchitecture, False),
    (NnOnnxArchitecture, False),
    (NnTensorrtArchitecture, False),
    (NnGenericArchitecture, True),

    (GenericModel, False),
    (OnnxModel, False),
    (PyTorchModel, False),
    (TrtModel, False),

)

TYPE_ALIASES = (
    "ShapeStrategyType",
    "Idtype",
    "NnModelDtype",
    "NnArchitectureType",
    "NnArchitecture",
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
    "_locked",
    "executor",
    "detect_arch",
    "Session",
)


def get_alias_source(name: str) -> str:
    """Extract the full definition of a type alias, including multi-line Literals."""

    # Find the find
    base_path = Path(pynnlib.__file__).parent
    for py_file in base_path.rglob("*.py"):
        with open(py_file, "r") as f:
            content = f.read()
            # Look for "Name" appearing before an equals sign (possibly across lines)
            if re.search(rf"^\s*{re.escape(name)}\s*(?::[^\n]*)?=", content, re.MULTILINE):
                file_path = py_file
                break
    if not file_path:
        raise FileNotFoundError(f"Alias {name} not found in pynnlib sources")


    with file_path.open("r") as f:
        lines = f.readlines()

        start = None
        # supports both 'Name =' and 'Name: TypeAlias ='
        pattern = re.compile(rf"^\s*{re.escape(name)}\s*(?::\s*\w+\s*)?=")
        for i, line in enumerate(lines):
            if pattern.match(line):
                start = i
                break

        if start is None:
            raise RuntimeError(f"Alias {name} not found in {file_path}")

    # Collect full alias definition
    collected = []
    depth_paren = depth_bracket = 0
    seen_eq = False

    for line in lines[start:]:
        code = line.split("#", 1)[0].rstrip()
        if not code:
            continue

        collected.append(code + "\n")
        if "=" in code:
            seen_eq = True
        depth_paren += code.count("(") - code.count(")")
        depth_bracket += code.count("[") - code.count("]")

        if seen_eq and depth_paren <= 0 and depth_bracket <= 0:
            break

    return "".join(collected).rstrip()



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

        # Check if this line should trigger skip mode
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

        # We're inside a skipped field (multi-line)
        bracket_depth += line.count("[") - line.count("]")
        paren_depth += line.count("(") - line.count(")")

        # Stop skipping once both are balanced and the line ends the field
        if bracket_depth <= 0 and paren_depth <= 0 and re.search(r"=\s*None|field\(", line):
            skip_mode = False
        continue

    return "\n".join(cleaned)



def generate_class_source(
    cls: Type,
    exclude: list[str] | None = None,
    include_methods: bool = False,
) -> str:
    """
    Generate a clean source definition for a class, handling both dataclasses and Enums.

    - If the class is an Enum, preserve it as Enum.
    - If not, generate as @dataclass.
    - Excludes fields and Callables, and optionally includes methods.
    """
    exclude_set: Set[str] = set(exclude or [])
    class_name = cls.__name__

    # Get the source file path
    try:
        filepath = inspect.getfile(cls)
    except (TypeError, OSError) as e:
        raise RuntimeError(f"Cannot find source file for class {class_name}: {e}")

    # Read and parse the source file
    try:
        with open(filepath, "r") as f:
            source = f.read()
    except IOError as e:
        raise RuntimeError(f"Cannot read source file {filepath}: {e}")

    # Parse all classes in the file
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise RuntimeError(f"Cannot parse source file {filepath}: {e}")

    # Find the target class and node
    class_map: dict[str, ast.ClassDef] = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    class_name = cls.__name__
    if class_name not in class_map:
        raise ValueError(f"Class '{class_name}' not found in source file.")
    class_node = class_map[class_name]

    # Detect if this is an Enum class
    is_enum = any(
        (
            isinstance(base, ast.Name) and base.id == "Enum"
        )
        or (
            isinstance(base, ast.Attribute)
            and base.attr == "Enum"
        )
        for base in class_node.bases
    )

    # Extract field definitions
    fields = []
    methods = []
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign):
            # Annotated assignment: e.g., x: int = 0
            target = stmt.target.id if isinstance(stmt.target, ast.Name) else None
            if not target:
                continue

            # Check if field should be excluded
            if target in exclude_set:
                continue

            # Get annotation
            ann = ast.unparse(stmt.annotation).strip()

            # Skip Callable fields
            if re.search(r'Callable\s*\[', ann):
                continue

            # Build field definition
            if stmt.value:
                val = ast.unparse(stmt.value).strip()
                fields.append(f"    {target}: {ann} = {val}")
            else:
                fields.append(f"    {target}: {ann}")

        elif isinstance(stmt, ast.Assign):
            # Plain assignment: e.g., x = 0
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if not targets:
                continue

            val = ast.unparse(stmt.value).strip() if stmt.value else "None"

            for target in targets:
                # Check if field should be excluded
                if target in exclude_set:
                    continue

                fields.append(f"    {target} = {val}")

        elif isinstance(stmt, ast.FunctionDef) and include_methods:
            # Handle methods
            method_name = stmt.name
            if method_name in (
                '__str__',
                'update',
                '__setattr__',
                'lock',
            ):
                continue

            method_lines = ast.unparse(stmt).split('\n')
            indented_method = (
                '\n'.join(f"    {line}" if line else line for line in method_lines)
            )
            methods.append(indented_method)

    lines = []

    if is_enum:
        lines.append(f"class {class_name}(Enum):")
    else:
        lines.append("@dataclass")
        lines.append(f"class {class_name}:")

    if fields:
        lines.extend(fields)
        if methods:
            lines.append("")
    elif methods:
        lines.append("")

    if methods:
        lines.extend(methods)
    elif not fields:
        lines.append("    pass")

    return "\n".join(lines) + "\n"



def main():
    imports = """from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Set, TypeAlias
"""

    sources: list[str] = []

    # Aliases
    seen_aliases = set()
    simple_aliases = []
    class_aliases = []

    # Collect class names to detect dependency
    class_names = {cls.__name__ for cls, _ in TARGET_CLASSES}

    for name in TYPE_ALIASES:
        alias_src = get_alias_source(name).strip()
        if alias_src in seen_aliases:
            continue
        seen_aliases.add(alias_src)

        # If alias references one of the class names, postpone it
        if any(
            re.search(rf"\b{re.escape(cls_name)}\b", alias_src)
            for cls_name in class_names
        ):
            class_aliases.append(alias_src)
        else:
            simple_aliases.append(alias_src)

    # Add simple aliases first
    sources.extend(simple_aliases)

    # Classes
    for cls, keep_methods in TARGET_CLASSES:
        sources.append(
            generate_class_source(
                cls,
                exclude=list(EXCLUDE_FIELDS),
                include_methods=keep_methods,
            )
        )

    # Add class-dependent aliases last
    sources.extend(class_aliases)

    # Write API file
    api_content = imports + "\n\n" + "\n\n".join(sources) + "\n"
    api_file_path = absolute_path(
        os.path.join(__file__, os.pardir, os.pardir, "ui", "pynnlib_api.py")
    )
    with open(api_file_path, "w") as f:
        f.write(api_content)

    print(f"API file '{api_file_path}' created successfully!")


if __name__ == "__main__":
    main()
