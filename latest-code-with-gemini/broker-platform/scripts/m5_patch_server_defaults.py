"""M5 patch: quote bare-word server_default literals for real PostgreSQL.

Found by running migration 001 against Neon (PostgreSQL 18.6): it fails with
`FeatureNotSupportedError: cannot use column reference in DEFAULT expression`.

Cause: the migration was generated and only ever proven against SQLite, which
accepts bare words in DEFAULT. PostgreSQL parses `DEFAULT USD` / `DEFAULT real`
as a column reference / type name and refuses. `sa.text('')` is worse - it
emits `DEFAULT` followed by nothing at all.

Fix: every string-literal server default becomes a quoted SQL literal:
    sa.text('USD')      -> sa.text("'USD'")
    sa.text('')         -> sa.text("''")
    sa.text('23:59:59') -> sa.text("'23:59:59'")
Numeric literals, now(), true/false are already valid SQL and stay untouched.

Applied to alembic/versions/*.py and infrastructure/persistence/*.py so models
and migrations cannot drift apart again.
"""
import ast
import io
import pathlib
import re

SAFE = {"now()", "true", "false"}
PATTERN = re.compile(r"server_default=sa\.text\('([^']*)'\)")


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def patch_file(path: pathlib.Path) -> int:
    src = io.open(path, encoding="utf-8", newline="").read()
    count = 0

    def repl(match: re.Match) -> str:
        nonlocal count
        value = match.group(1)
        if value in SAFE or _is_numeric(value):
            return match.group(0)
        count += 1
        return 'server_default=sa.text("\'%s\'")' % value

    patched = PATTERN.sub(repl, src)
    if count:
        ast.parse(patched)  # never write a file that does not parse
        io.open(path, "w", encoding="utf-8", newline="").write(patched)
    return count


total = 0
for directory in ("alembic/versions", "infrastructure/persistence"):
    for path in sorted(pathlib.Path(directory).glob("*.py")):
        n = patch_file(path)
        if n:
            print(f"{path}: quoted {n} server_default literal(s)")
            total += n
print(f"total: {total}")
assert total > 0, "nothing patched - anchors changed?"
