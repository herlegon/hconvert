#!/usr/bin/env python3
"""
Extract only the dataclass field definitions (variables) from a Python source file.

Example:
    python extract_dataclass_fields.py models.py PyTorchModel
"""

import ast
import sys
from typing import Optional

def get_dataclass_fields(source: str, class_name: str) -> Optional[ast.ClassDef]:
    """Parse source and return the AST node for the given dataclass."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def extract_field_defs(class_node: ast.ClassDef) -> list[str]:
    """Return lines for dataclass field definitions."""
    fields = []
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign):
            # annotated assignment, e.g. `x: int = 0`
            target = stmt.target.id if isinstance(stmt.target, ast.Name) else None
            if target:
                ann = ast.unparse(stmt.annotation).strip()
                if stmt.value:
                    val = ast.unparse(stmt.value).strip()
                    fields.append(f"    {target}: {ann} = {val}")
                else:
                    fields.append(f"    {target}: {ann}")
        elif isinstance(stmt, ast.Assign):
            # unannotated assignment (rare in dataclasses)
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if not targets:
                continue
            val = ast.unparse(stmt.value).strip() if stmt.value else "None"
            for t in targets:
                fields.append(f"    {t}: Any = {val}")
    return fields


def extract_imports(source: str) -> list[str]:
    """Keep top-level imports so datatypes resolve."""
    lines = []
    for line in source.splitlines():
        if line.strip().startswith(("import ", "from ")):
            lines.append(line)
    return lines


def generate_clean_class(source: str, class_name: str) -> str:
    """Return a cleaned-up dataclass string for the given class."""
    node = get_dataclass_fields(source, class_name)
    if not node:
        raise ValueError(f"Class '{class_name}' not found.")

    imports = extract_imports(source)
    fields = extract_field_defs(node)

    result = []
    if imports:
        result.extend(imports)
        result.append("")  # newline

    result.append("from dataclasses import dataclass, field\n")
    result.append("@dataclass")
    result.append(f"class {class_name}:")
    if fields:
        result.extend(fields)
    else:
        result.append("    pass")

    return "\n".join(result)


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_dataclass_fields.py <source.py> <ClassName>")
        sys.exit(1)

    path = sys.argv[1]
    class_name = sys.argv[2]

    with open(path, "r") as f:
        source = f.read()

    print(generate_clean_class(source, class_name))


if __name__ == "__main__":
    main()
