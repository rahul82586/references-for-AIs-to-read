"""M5 patch: create `groups` before `accounts` in migration 001.

Autogenerate emitted tables in alphabetical order. `accounts` carries
`sa.ForeignKeyConstraint(['group_name'], ['groups.name'])`, but `groups` was
created eighth. SQLite never enforced the FK so this passed; PostgreSQL
validates the reference at CREATE TABLE time:
    UndefinedTableError: relation "groups" does not exist

Fix: move the `groups` create_table statement and its create_index statements
ahead of `accounts`. balance_operations -> accounts is the only other FK and
is already in order (accounts is created before it).
"""
import ast
import io
import re

PATH = "alembic/versions/001_initial_schema.py"
src = io.open(PATH, encoding="utf-8", newline="").read()
lines = src.split("\n")

# Group the upgrade() body into statements: a statement starts at a line
# matching ^    op\. and runs until the next such line (exclusive).
starts = [i for i, ln in enumerate(lines) if re.match(r"    op\.", ln)]
assert starts, "no op.* statements found"

statements = []  # (start_idx, end_idx_exclusive, text_lines)
for idx, start in enumerate(starts):
    end = starts[idx + 1] if idx + 1 < len(starts) else None
    if end is None:
        # last statement: ends at the dedent (next line starting with 'def ' or a
        # non-indented, non-blank line)
        end = start + 1
        while end < len(lines) and not re.match(r"(def |\S)", lines[end]):
            end += 1
    statements.append((start, end, lines[start:end]))


def stmt_text(s):
    return "\n".join(s[2])


groups_stmts = [
    s for s in statements
    if re.search(r"op\.create_table\(\s*\n\s*'groups'", stmt_text(s))
    or re.match(r"    op\.create_index\([^)]*'groups'", stmt_text(s))
]
accounts_stmt = next(
    s for s in statements
    if re.search(r"op\.create_table\(\s*\n\s*'accounts'", stmt_text(s))
)
assert groups_stmts, "groups statements not found"
print(f"moving {len(groups_stmts)} groups statement(s) before accounts")

# Rebuild the file: take everything, drop the groups statements from their old
# positions, and insert them immediately before the accounts statement.
groups_starts = {s[0] for s in groups_stmts}
accounts_start = accounts_stmt[0]

out = []
i = 0
inserted = False
while i < len(lines):
    if i == accounts_start and not inserted:
        for gs in groups_stmts:
            out.extend(gs[2])
        inserted = True
    if i in groups_starts:
        # skip this whole statement (it is being moved)
        stmt = next(s for s in groups_stmts if s[0] == i)
        i = stmt[1]
        continue
    out.append(lines[i])
    i += 1

assert inserted, "accounts anchor never reached"
patched = "\n".join(out)
ast.parse(patched)

# verify new order
names = re.findall(r"op\.create_table\(\s*\n?\s*'([^']+)'", patched)
assert names.index("groups") < names.index("accounts"), f"bad order: {names}"
print("new creation order:", names)

io.open(PATH, "w", encoding="utf-8", newline="").write(patched)
print("migration 001 reordered")
