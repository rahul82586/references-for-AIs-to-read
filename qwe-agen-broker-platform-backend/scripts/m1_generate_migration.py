"""
Generate alembic/versions/001_initial_schema.py from Base.metadata.

Hand-writing this migration is how the previous one drifted: it created
`symbols.margin_initial_percent` (a field the Symbol entity no longer has) and a
`groups` table whose margin thresholds were DECIMAL(5,4) fractions in init.sql but
Numeric(6,2) percents in the model. Generating from the models removes the
possibility of drift, because the models ARE the schema.

Column definitions come from SQLAlchemy's own PostgreSQL DDL compiler - the same
machinery create_all() uses - so types, precision and nullability are authoritative
rather than transcribed.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path("alembic_001.py")
sys.path.insert(0, str(ROOT))

from sqlalchemy.schema import CreateTable, CreateIndex  # noqa: E402
from sqlalchemy.dialects import postgresql  # noqa: E402

from infrastructure.persistence.database import Base  # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402
import infrastructure.persistence.config_models  # noqa: F401,E402

DIALECT = postgresql.dialect()

HEADER = '''"""Initial schema, generated from the SQLAlchemy models.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-09-10

DO NOT EDIT BY HAND. This file is generated from Base.metadata by
scripts/m1_generate_migration.py, because the models are the single source of truth
for the schema. The revision it replaces had drifted: it created
symbols.margin_initial_percent (a field the Symbol entity no longer has) and a groups
table whose margin thresholds were DECIMAL(5,4) fractions here but Numeric(6,2)
percents in the model, while ops/docker/init.sql used a UUID primary key and the model
used the group name. Four competing definitions of the same table.

Units worth restating because they were the source of that drift:
  groups.margin_call / groups.margin_stop_out are PERCENT (MT5 MarginCall "50.00",
  MarginStopOut "30.00"). There is no 0.8 / 0.5 anywhere in this schema.
  symbols.point and symbols.tick_size are SEPARATE columns. MT5's Point is the
  price-precision step; TickSize is a different, frequently-zero field.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Alembic revision graph. Both identifiers are required: without down_revision Alembic
# cannot build the graph and `alembic upgrade head` fails outright, which is what the
# deleted migration.py did (it had prose in the docstring instead of variables).
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

'''


# DDL type text -> a Python expression that reconstructs it. The compiler emits raw
# SQL ("TIMESTAMP WITH TIME ZONE"), which is not valid inside a sa.Column() call, so
# every type the models actually use is mapped explicitly. Anything unmapped raises
# rather than emitting a migration that will not parse.
TYPE_EXPR = {
    "JSONB": "postgresql.JSONB()",
    "TEXT": "sa.Text()",
    "BOOLEAN": "sa.Boolean()",
    "INTEGER": "sa.Integer()",
    "BIGINT": "sa.BigInteger()",
    "TIMESTAMP WITH TIME ZONE": "sa.DateTime(timezone=True)",
    "TIMESTAMP": "sa.DateTime()",
    "DATE": "sa.Date()",
    "VARCHAR": "sa.String()",
}


def type_expr(column) -> str:
    sql = column.type.compile(dialect=DIALECT).upper().strip()

    if sql in TYPE_EXPR:
        return TYPE_EXPR[sql]

    match = re.fullmatch(r"VARCHAR\((\d+)\)", sql)
    if match:
        return f"sa.String(length={match.group(1)})"

    match = re.fullmatch(r"NUMERIC\((\d+),\s*(\d+)\)", sql)
    if match:
        return f"sa.Numeric(precision={match.group(1)}, scale={match.group(2)})"

    match = re.fullmatch(r"NUMERIC\((\d+)\)", sql)
    if match:
        return f"sa.Numeric(precision={match.group(1)})"

    if sql == "NUMERIC":
        return "sa.Numeric()"

    raise SystemExit(f"[FAIL] unmapped column type {sql!r} on {column.name}; extend TYPE_EXPR")


def col_expr(column) -> str:
    """Render one column as a sa.Column(...) literal."""
    parts = [f"sa.Column({column.name!r}, {type_expr(column)}"]

    if not column.nullable:
        parts.append("nullable=False")
    else:
        parts.append("nullable=True")

    if column.primary_key:
        # Primary keys are emitted via PrimaryKeyConstraint below, so the column
        # itself does not repeat it.
        pass

    # JSONB columns are nullable=False with a Python-side default only, so a raw SQL
    # insert (a seeder, a psql session, a migration backfill) would violate NOT NULL.
    # Give them a real server default matching the Python one.
    if column.server_default is None and type_expr(column) == "postgresql.JSONB()":
        py_default = column.default.arg if column.default is not None else None
        # Column(JSONB, default=list) yields a callable default whose .arg is the
        # builtin itself, so compare by identity against the builtins. Do NOT use
        # `py_default == []`: for a function that dispatches to list.__eq__ and
        # returns NotImplemented, and isinstance(list, list) is False.
        # SQLAlchemy wraps a callable column default in a closure, so `arg is list`
        # is False even for Column(JSONB, default=list). Match on the wrapped
        # function's __name__, and fall back to identity/type for literal defaults.
        name = getattr(py_default, "__name__", None)
        if name in ("list", "tuple", "set") or isinstance(py_default, (list, tuple, set)):
            literal = "'[]'::jsonb"
        else:
            literal = "'{}'::jsonb"
        parts.append(f"server_default=sa.text({literal!r})")

    if column.server_default is not None:
        arg = column.server_default.arg
        text = getattr(arg, "text", None)
        if text is not None:
            parts.append(f"server_default=sa.text({str(text)!r})")
        else:
            parts.append(f"server_default=sa.text({str(arg)!r})")
    elif column.default is not None and getattr(column.default, "is_scalar", False):
        value = column.default.arg
        if isinstance(value, bool):
            parts.append(f"server_default=sa.text({str(value).lower()!r})")
        else:
            parts.append(f"server_default=sa.text({str(value)!r})")

    if column.comment:
        parts.append(f"comment={column.comment!r}")

    return ", ".join(parts) + ")"


def table_block(table) -> str:
    lines = [f"    op.create_table(\n        {table.name!r},"]
    for column in table.columns:
        lines.append(f"        {col_expr(column)},")
    pk = [c.name for c in table.primary_key.columns]
    if pk:
        lines.append(f"        sa.PrimaryKeyConstraint({', '.join(repr(p) for p in pk)}),")
    for fk in table.foreign_keys:
        lines.append(
            f"        sa.ForeignKeyConstraint([{fk.parent.name!r}], "
            f"[{fk.target_fullname!r}]),"
        )
    for uc in table.constraints:
        if uc.__class__.__name__ == "UniqueConstraint" and uc.columns:
            names = ", ".join(repr(c.name) for c in uc.columns)
            label = repr(uc.name) if uc.name else "None"
            lines.append(f"        sa.UniqueConstraint({names}, name={label}),")
    lines.append("    )")

    for index in table.indexes:
        cols = ", ".join(repr(c.name) for c in index.columns)
        unique = "True" if index.unique else "False"
        lines.append(
            f"    op.create_index({index.name!r}, {table.name!r}, [{cols}], unique={unique})"
        )
    return "\n".join(lines)


def drop_block(table) -> str:
    lines = []
    for index in sorted(table.indexes, key=lambda i: i.name or ""):
        lines.append(f"    op.drop_index({index.name!r}, table_name={table.name!r})")
    lines.append(f"    op.drop_table({table.name!r})")
    return "\n".join(lines)


def main() -> int:
    tables = [Base.metadata.tables[name] for name in sorted(Base.metadata.tables)]
    if not tables:
        print("no tables registered on Base.metadata - model imports are broken", file=sys.stderr)
        return 1

    out = [HEADER]
    out.append("\ndef upgrade() -> None:\n")
    for table in tables:
        out.append(table_block(table))
        out.append("")
    out.append("\ndef downgrade() -> None:\n")
    # Drop in reverse so foreign keys resolve.
    for table in reversed(tables):
        out.append(drop_block(table))
        out.append("")

    text = "\n".join(out).rstrip() + "\n"
    # Sanity check: the generated file must parse.
    compile(text, str(OUT), "exec")
    OUT.write_text(text, encoding="utf-8")

    columns = sum(len(t.columns) for t in tables)
    print(f"  ok  wrote {OUT}")
    print(f"      {len(tables)} tables, {columns} columns")
    for table in tables:
        print(f"        {table.name:22s} {len(table.columns):3d} columns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
