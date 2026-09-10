"""
Step M1 part 2 - one schema for the configuration plane.

  * GroupModel and SymbolModel move out of db_models.py into config_models.py, aligned
    field-for-field with MT5 ConfigGroups / ConfigSymbols. The stale versions are
    deleted rather than kept alongside: two definitions of the same __tablename__ is
    what produced the DealModel/PositionModel shadowing bug in M0.
  * mappers.py stops defining group_to_db / db_to_group / symbol_to_db / db_to_symbol
    and re-exports them from config_mappers, so existing imports keep working while
    there is exactly one implementation.
  * ops/docker/init.sql is deleted and its compose mount removed. It created a `groups`
    table with a UUID primary key and DECIMAL(5,4) fraction thresholds while SQLAlchemy
    expected a name primary key and Numeric(6,2) percent thresholds, so every read and
    write failed. Alembic now owns schema creation.
  * alembic/versions/migration.py is deleted: it had no `revision` / `down_revision`
    variables (only prose in the docstring), so Alembic could not build a revision
    graph and `alembic upgrade head` could never run.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "infrastructure" / "persistence" / "db_models.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str) -> None:
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def cut_class(rel: str, class_name: str, next_marker: str) -> None:
    """Delete `class <name>(Base):` up to (not including) the next marker."""
    text = load(rel)
    work = text.replace("\r\n", "\n")
    start = work.find(f"class {class_name}(Base):")
    if start == -1:
        raise SystemExit(f"[FAIL] {rel}: class {class_name} not found")
    end = work.find(next_marker, start)
    if end == -1:
        raise SystemExit(f"[FAIL] {rel}: marker after {class_name} not found: {next_marker!r}")
    removed = work[start:end]
    if f'__tablename__ = "' not in removed:
        raise SystemExit(f"[FAIL] {rel}: the region for {class_name} has no __tablename__")
    work = work[:start] + work[end:]
    crlf = "\r\n" in text
    save(rel, work.replace("\n", "\r\n") if crlf else work)
    print(f"  ok  {rel}: removed stale {class_name} ({len(removed)} chars)")


# ---------------------------------------------------------------------------
# 1. New MT5-aligned config models
# ---------------------------------------------------------------------------

shutil.copyfile(HERE / "m1pkg" / "config_models.py", ROOT / "infrastructure" / "persistence" / "config_models.py")
shutil.copyfile(HERE / "m1pkg" / "config_mappers.py", ROOT / "infrastructure" / "persistence" / "config_mappers.py")
print("  ok  infrastructure/persistence/config_models.py: MT5-aligned GroupModel + SymbolModel")
print("  ok  infrastructure/persistence/config_mappers.py: codec-routed mappers")

# ---------------------------------------------------------------------------
# 2. Delete the stale models from db_models.py
#    GroupModel is followed by SymbolModel; SymbolModel is followed by OrderModel.
# ---------------------------------------------------------------------------

DBM = "infrastructure/persistence/db_models.py"
cut_class(DBM, "GroupModel", "class SymbolModel(Base):")
cut_class(DBM, "SymbolModel", "class OrderModel(Base):")

# db_models must re-export the relocated models: alembic/env.py and Base.metadata
# discovery walk this module, and several repositories import GroupModel from here.
text = load(DBM)
work = text.replace("\r\n", "\n")
if "from .config_models import" not in work:
    header_end = work.find("class Base(DeclarativeBase):")
    if header_end == -1:
        raise SystemExit("[FAIL] db_models.py: Base declaration not found")
    reexport = (
        "# GroupModel and SymbolModel live in config_models.py, aligned field-for-field\n"
        "# with MT5 ConfigGroups / ConfigSymbols. Re-exported here so that\n"
        "# Base.metadata sees every table and existing imports keep resolving.\n"
        "from .config_models import GroupModel, SymbolModel  # noqa: E402,F401\n"
        "\n"
        "\n"
    )
    work = work[:header_end] + reexport + work[header_end:]
    save(DBM, work.replace("\n", "\r\n") if "\r\n" in text else work)
    print("  ok  db_models.py: re-exports GroupModel/SymbolModel so Base.metadata is complete")

# The re-export must come AFTER Base is defined, since config_models imports Base
# from this module. Move it to the bottom instead.
text = load(DBM)
work = text.replace("\r\n", "\n")
marker = (
    "# GroupModel and SymbolModel live in config_models.py, aligned field-for-field\n"
    "# with MT5 ConfigGroups / ConfigSymbols. Re-exported here so that\n"
    "# Base.metadata sees every table and existing imports keep resolving.\n"
    "from .config_models import GroupModel, SymbolModel  # noqa: E402,F401\n"
)
if marker in work:
    work = work.replace(marker + "\n\n", "").replace(marker, "")
    work = work.rstrip("\n") + "\n\n\n" + marker.rstrip("\n") + "\n"
    save(DBM, work.replace("\n", "\r\n") if "\r\n" in text else work)
    print("  ok  db_models.py: moved the re-export below Base to avoid a circular import")

# ---------------------------------------------------------------------------
# 3. mappers.py delegates to config_mappers
# ---------------------------------------------------------------------------

MAP = "infrastructure/persistence/mappers.py"
text = load(MAP)
work = text.replace("\r\n", "\n")


def cut_function(source: str, name: str) -> str:
    start = source.find(f"def {name}(")
    if start == -1:
        return source
    # Back up over any immediately preceding comment banner.
    line_start = source.rfind("\n\n", 0, start)
    if line_start != -1 and "#" in source[line_start:start]:
        start = line_start + 2
    end = source.find("\ndef ", start + 1)
    if end == -1:
        end = source.find("\n# ====", start + 1)
    if end == -1:
        end = len(source)
    return source[:start] + source[end:]


before = len(work)
for fn in ("group_to_db", "db_to_group", "symbol_to_db", "db_to_symbol"):
    work = cut_function(work, fn)
if len(work) == before:
    raise SystemExit("[FAIL] mappers.py: none of the config mappers were found")

delegate = '''

# ============================================================================
# CONFIGURATION PLANE MAPPERS (Group, Symbol)
# ============================================================================
# Implemented in config_mappers.py, where every conversion is routed through the MT5
# wire codec so the database row and an MT5 export are the same shape by construction.
# Re-exported here because repositories and tests import them from this module.
# ============================================================================

from .config_mappers import (  # noqa: E402,F401
    db_to_group,
    db_to_symbol,
    group_to_db,
    symbol_to_db,
)
'''
work = work.rstrip("\n") + "\n" + delegate
save(MAP, work.replace("\n", "\r\n") if "\r\n" in text else work)
print(f"  ok  mappers.py: removed {before - len(work)} chars of stale config mappers, now delegates")

# ---------------------------------------------------------------------------
# 4. Delete the competing schema sources
# ---------------------------------------------------------------------------

init_sql = ROOT / "ops" / "docker" / "init.sql"
if init_sql.is_file():
    init_sql.unlink()
    print("  ok  ops/docker/init.sql: deleted (UUID PK + DECIMAL(5,4) fractions vs SQLAlchemy's name PK + percent)")

migration = ROOT / "alembic" / "versions" / "migration.py"
if migration.is_file():
    migration.unlink()
    print("  ok  alembic/versions/migration.py: deleted (no revision/down_revision variables)")

compose = ROOT / "ops" / "docker" / "docker-compose.dev.yml"
if compose.is_file():
    text = load("ops/docker/docker-compose.dev.yml")
    work = text.replace("\r\n", "\n")
    for line in (
        '      - ./ops/docker/init.sql:/docker-entrypoint-initdb.d/init.sql\n',
        '      - ./init.sql:/docker-entrypoint-initdb.d/init.sql\n',
    ):
        if line in work:
            work = work.replace(line, "")
            print("  ok  docker-compose.dev.yml: removed the init.sql mount")
            break
    else:
        print("  note docker-compose.dev.yml: no init.sql mount found (already absent)")
    save("ops/docker/docker-compose.dev.yml", work.replace("\n", "\r\n") if "\r\n" in text else work)
