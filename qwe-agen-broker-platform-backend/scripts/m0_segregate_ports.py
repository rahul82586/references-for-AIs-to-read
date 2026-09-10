"""
Step M0 part 4 - interface segregation on the merged repository ports.

Merging the two duplicate definitions of IOrderRepository / IDealRepository /
IPositionRepository produced the union of their methods. That union is the right
*contract*, but marking all of it @abstractmethod means every implementation and
every test mock must provide ten methods before it can be instantiated at all -
which is what broke the margin-loop integration test:

    TypeError: Can't instantiate abstract class MockPositionRepository
               with abstract methods close, get_positions_by_account

So: the methods the application actually calls stay @abstractmethod, and the
extended MT5 query surface becomes a default implementation that raises
NotImplementedError naming itself. An implementation can then adopt the full MT5
query set incrementally, and a failure says exactly which method is missing instead
of failing at construction time.
"""

from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
IFACE = ROOT / "core" / "ports" / "interfaces.py"
if not IFACE.is_file():
    raise SystemExit(f"not found: {IFACE}")

# Methods that must be implemented. Everything else in these ports gets a default.
CORE: dict[str, set[str]] = {
    "IOrderRepository": {"save", "find_by_id", "find_by_account"},
    "IDealRepository": {"save", "find_by_id", "find_by_account"},
    "IPositionRepository": {"save", "find_by_id", "get_by_symbol", "get_by_account"},
    "IGroupRepository": {"save", "find_by_name", "get_all"},
}

STUB_BODY = '''        raise NotImplementedError(
            "{cls}.{name} is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )'''

raw = IFACE.read_text(encoding="utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n") if crlf else raw
lines = text.split("\n")

tree = ast.parse(text)
# Collect (decorator_line_index, body_span) for every non-core method in the ports.
edits: list[tuple[int, int, int, str, str]] = []  # (dec_idx, body_start, body_end, cls, name)

for node in tree.body:
    if not isinstance(node, ast.ClassDef) or node.name not in CORE:
        continue
    core = CORE[node.name]
    for item in node.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if item.name in core:
            continue
        has_abstractmethod = any(
            (isinstance(d, ast.Name) and d.id == "abstractmethod")
            or (isinstance(d, ast.Attribute) and d.attr == "abstractmethod")
            for d in item.decorator_list
        )
        if not has_abstractmethod:
            continue
        dec_idx = min(d.lineno for d in item.decorator_list) - 1
        # Body span excludes the docstring if present.
        body = item.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]
        if not body:
            continue
        edits.append((dec_idx, body[0].lineno - 1, body[-1].end_lineno, node.name, item.name))

if not edits:
    raise SystemExit("[FAIL] found no non-core abstract methods to relax")

# Apply from the bottom up so earlier line numbers stay valid.
for dec_idx, body_start, body_end, cls, name in sorted(edits, reverse=True):
    # STUB_BODY is already written at the correct 8-space method-body indent; do not
    # re-indent it or the result will not parse.
    stub = STUB_BODY.format(cls=cls, name=name)
    lines[body_start:body_end] = stub.split("\n")
    del lines[dec_idx]

text = "\n".join(lines)
IFACE.write_text(text.replace("\n", "\r\n") if crlf else text, encoding="utf-8")

print(f"  ok  relaxed {len(edits)} extended methods to default-raise implementations")
for _, _, _, cls, name in sorted(edits, key=lambda e: (e[3], e[4])):
    print(f"        {cls}.{name}")
