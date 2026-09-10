"""
Step M1 part 3 - one DeclarativeBase, and a resolvable Alembic revision graph.

TWO BUGS FIXED HERE

1. There were two separate DeclarativeBase classes:
       infrastructure/persistence/database.py:7   class Base(DeclarativeBase)
       infrastructure/persistence/db_models.py    class Base(DeclarativeBase)
   Each DeclarativeBase owns its own MetaData registry, so tables registered on one
   are invisible to the other. `DatabaseManager.create_tables()` uses database.Base
   while `alembic/env.py` uses db_models.Base, meaning the dev shortcut and the
   migration path were creating DIFFERENT schemas. database.Base is now the single
   declarative base and db_models re-exports it.

2. alembic/env.py set target_metadata from db_models.Base but never imported
   config_models, so groups/symbols would not have been autogenerate-visible.

Also: alembic/versions/001_initial_schema.py is replaced. The old one created
`symbols.margin_initial_percent` / `margin_maintenance_percent` - fields the Symbol
entity no longer has - and `groups.margin_call_level DECIMAL(5,4) DEFAULT 0.8000` in
init.sql versus `Numeric(6,2) DEFAULT 60` in the model. Both are gone; the schema is
now generated from the models, which are aligned to MT5.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "alembic" / "env.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, *, crlf: bool = True) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:200]!r}")
    save(rel, work.replace(old, new, 1), crlf=crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. db_models.py: use the single Base from database.py
# ---------------------------------------------------------------------------

sub(
    "infrastructure/persistence/db_models.py",
    """from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from decimal import Decimal
import enum


class Base(DeclarativeBase):
    pass
""",
    """from sqlalchemy.sql import func
from decimal import Decimal
import enum

# One DeclarativeBase for the whole persistence layer. database.py owns it, so that
# DatabaseManager.create_tables() and Alembic's target_metadata see the SAME registry.
# A second DeclarativeBase here would silently create a second, disjoint schema.
from .database import Base  # noqa: F401
""",
    "db_models now shares the single DeclarativeBase from database.py",
)

# ---------------------------------------------------------------------------
# 2. config_models.py: import Base from database.py, not db_models.py
# ---------------------------------------------------------------------------

sub(
    "infrastructure/persistence/config_models.py",
    "from .db_models import Base",
    "from .database import Base",
    "config_models imports Base directly, breaking the circular import",
)

# ---------------------------------------------------------------------------
# 3. alembic/env.py: import every model module before autogenerate
# ---------------------------------------------------------------------------

sub(
    "alembic/env.py",
    "from infrastructure.persistence.db_models import Base",
    """from infrastructure.persistence.database import Base
# Import every model module so that all tables are registered on Base.metadata
# before Alembic compares it against the database. Missing an import here means
# autogenerate silently drops that table from the migration.
import infrastructure.persistence.db_models  # noqa: F401,E402
import infrastructure.persistence.config_models  # noqa: F401,E402""",
    "alembic/env.py imports all model modules and the single Base",
)

# ---------------------------------------------------------------------------
# 4. Replace the stale initial migration with one generated from the models
# ---------------------------------------------------------------------------

old_migration = ROOT / "alembic" / "versions" / "001_initial_schema.py"
if old_migration.is_file():
    old_migration.unlink()
    print("  ok  alembic/versions/001_initial_schema.py: deleted (stale symbol/group columns)")

shutil.copyfile(
    HERE / "m1pkg" / "alembic_001.py",
    ROOT / "alembic" / "versions" / "001_initial_schema.py",
)
print("  ok  alembic/versions/001_initial_schema.py: replaced with a graph-valid revision")
