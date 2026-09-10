"""
Step M2 part 0 - Group gains currency_digits, and the config models follow.

MT5 ConfigGroups has a CurrencyDigits field (2 in the reference export, i.e. cents for
a USD account). The GroupModel column was added in M1 but the domain Group had no field
for it, so the loader could not populate it and the mapper could not read it back.

Also: Group.server_id defaulted to 0 while MT5 numbers servers from 1, so a group
created natively would export Server "0" and not match any real cluster member.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
GROUP = ROOT / "core" / "domains" / "accounts" / "group.py"
if not GROUP.is_file():
    raise SystemExit(f"not found: {GROUP}")

with open(GROUP, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = """    account_type: AccountType = AccountType.REAL
    currency: str = \"USD\"
    """
NEW = """    account_type: AccountType = AccountType.REAL
    currency: str = \"USD\"
    # MT5 ConfigGroups.CurrencyDigits: how many decimal places the account currency
    # displays, i.e. 2 for a USD account denominated in cents. Distinct from a
    # symbol's Digits, which is price precision.
    currency_digits: int = 2
    """
if OLD not in work:
    raise SystemExit("[FAIL] group.py: the currency declaration was not found")
work = work.replace(OLD, NEW, 1)

OLD_SERVER = "    server_id: int = 0"
NEW_SERVER = (
    "    # MT5 numbers cluster servers from 1 (1=main trade, 2=access, 3=history,\n"
    "    # 4=backup). A group that exports Server \"0\" matches no real cluster member.\n"
    "    server_id: int = 1"
)
if OLD_SERVER in work:
    work = work.replace(OLD_SERVER, NEW_SERVER, 1)

with open(GROUP, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print("  ok  core/domains/accounts/group.py: added currency_digits, server_id defaults to 1")
