"""Import-scan helper: counts how many modules in a tree import cleanly."""
import importlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()
# `alembic/` holds migration scripts that Alembic loads through its own runner;
# `alembic.versions.001_initial_schema` is not a valid module path (it starts with a
# digit), so scanning it as an import is a false negative. Same for tests.
skip = {"__pycache__", ".hypothesis", "tests", "alembic"}
mods, bad = [], []
for p in sorted(root.rglob("*.py")):
    if skip & set(p.parts):
        continue
    rel = p.relative_to(root).with_suffix("")
    name = ".".join(rel.parts)
    if name.endswith(".__init__"):
        name = name[: -len(".__init__")]
    mods.append(name)
for name in mods:
    try:
        importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001
        bad.append(f"{name}: {type(exc).__name__}: {exc}")
print(f"{root.name}: {len(mods) - len(bad)}/{len(mods)} import")
for b in bad[:10]:
    print("   FAIL", b)
sys.exit(1 if bad else 0)
