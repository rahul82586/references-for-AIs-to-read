"""M6 patch 3: CAST the reservation binds — numeric comparison on both dialects.

Found by the sqlite atomicity test: binding the amount as a string against a
NUMERIC expression does not compare numerically in SQLite (text ordering puts
'1100.10' above every number, so the WHERE never matched), and PostgreSQL
rejects `numeric >= text` outright. CAST(:amt AS DECIMAL(20,8)) is valid on
both and keeps the bind a plain string (sqlite3 cannot bind Decimal).
"""
import ast
import io

PATH = "infrastructure/persistence/repositories/account_repository.py"
src = io.open(PATH, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in src else "\n"


def rep(old, new):
    global src
    if nl == "\r\n":
        old = old.replace("\n", "\r\n")
        new = new.replace("\n", "\r\n")
    assert src.count(old) == 1, f"anchor {src.count(old)}x: {old[:60]!r}"
    src = src.replace(old, new)


rep(
    '''            "UPDATE accounts SET margin_reserved = margin_reserved + :amt "
            "WHERE login = :login AND "
            "(balance + credit + profit - margin_used - margin_reserved) >= :amt "
            "RETURNING margin_reserved"
''',
    '''            "UPDATE accounts SET margin_reserved = margin_reserved + CAST(:amt AS DECIMAL(20,8)) "
            "WHERE login = :login AND "
            "(balance + credit + profit - margin_used - margin_reserved) "
            ">= CAST(:amt AS DECIMAL(20,8)) "
            "RETURNING margin_reserved"
''',
)

rep(
    '''            "UPDATE accounts SET margin_reserved = "
            "CASE WHEN margin_reserved >= :amt THEN margin_reserved - :amt ELSE 0 END "
            "WHERE login = :login RETURNING margin_reserved"
''',
    '''            "UPDATE accounts SET margin_reserved = "
            "CASE WHEN margin_reserved >= CAST(:amt AS DECIMAL(20,8)) "
            "THEN margin_reserved - CAST(:amt AS DECIMAL(20,8)) ELSE 0 END "
            "WHERE login = :login RETURNING margin_reserved"
''',
)

ast.parse(src.replace(nl, "\n"))
io.open(PATH, "w", encoding="utf-8", newline="").write(src)
print("CAST applied to both reservation statements")
