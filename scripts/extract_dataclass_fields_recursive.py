#!/usr/bin/env python3
"""
Extract dataclass field definitions (variables only) from a Python file,
including inherited fields from parent dataclasses.

Example:
    python extract_dataclass_fields_recursive.py models.py PyTorchModel
"""

import ast
import sys
from typing import Optional, Dict, List


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
    lines.append(f"@dataclass")
    lines.append(f"class {class_name}:")
    if filtered_fields:
        lines.extend(filtered_fields)
    else:
        lines.append("    pass")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_dataclass_fields_recursive.py <source.py> <ClassName>")
        sys.exit(1)

    path = sys.argv[1]
    class_name = sys.argv[2]
    exclude_fields = (
        'state_dict',
        'model_proto',
        'engine',
        'ModuleClass',
        'executor',
        'module',
    )

    with open(path, "r") as f:
        source = f.read()

    print(generate_clean_class(source, class_name, exclude_fields))


if __name__ == "__main__":
    main()
