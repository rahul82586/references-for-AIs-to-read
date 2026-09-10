"""
Step M3 part 18 - the last two attribute-name sites.

1. `tests/unit/api/test_api.py` mocked the account with `account_mock.login_id = "10001"`.
   The handler now correctly reads `account.login`, so the mock returned an un-stubbed
   MagicMock instead of the string. The mock is what was wrong: it modelled the same
   non-existent attribute the production code had. `Account` has `login`.

   The response KEY stays `login_id`, because that is the API's published field name and
   changing it would break clients. The test still asserts on the key.

2. `tests/unit/concurrency/test_execution_concurrency.py` builds `Position(id=...)`.
   The field is `position_id` - the same stale vocabulary from the deleted duplicate
   PositionModel that made RiskEngine read `.id` and get nothing.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


# ---------------------------------------------------------------------------
# 1. the account mock must model the real attribute
# ---------------------------------------------------------------------------

REL = "tests/unit/api/test_api.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")
before = work

# The mock sets login_id; Account has `login`. Keep the query DTO's login_id (a real
# field of GetAccountInfoQuery) and the response key assertion untouched.
work = re.sub(r"\baccount_mock\.login_id\b", "account_mock.login", work)
work = re.sub(r"\bmock_account\.login_id\b", "mock_account.login", work)
work = re.sub(r"\baccount\.login_id = ", "account.login = ", work)

if work != before:
    save(REL, work, crlf)
    print(f"  ok  {REL}: the account mock models `login`, the attribute Account actually has")
else:
    print(f"  --  {REL}: nothing to change")

# ---------------------------------------------------------------------------
# 2. Position(id=...) -> position_id
# ---------------------------------------------------------------------------

for REL in (
    "tests/unit/concurrency/test_execution_concurrency.py",
    "tests/integration/test_e2e_flow.py",
    "tests/unit/domains/risk/test_audit3_hardening.py",
    "tests/unit/domains/risk/test_cross_currency_pnl.py",
):
    path = ROOT / REL
    if not path.is_file():
        continue
    text = load(REL)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    before = work

    def _balanced(source: str, name: str):
        spans = []
        for match in re.finditer(re.escape(name) + r"\(", source):
            i = match.end()
            depth = 1
            while i < len(source) and depth:
                if source[i] == "(":
                    depth += 1
                elif source[i] == ")":
                    depth -= 1
                i += 1
            spans.append((match.start(), i))
        return spans

    for start, end in reversed(_balanced(work, "Position")):
        call = work[start:end]
        fixed = re.sub(r"\bid=", "position_id=", call)
        work = work[:start] + fixed + work[end:]

    if work != before:
        save(REL, work, crlf)
        print(f"  ok  {REL}: Position(id=) -> Position(position_id=)")
    else:
        print(f"  --  {REL}: nothing to change")

# ---------------------------------------------------------------------------
# 3. The test's mock repositories read position.id too
# ---------------------------------------------------------------------------
#
# MockPositionRepository keyed its dict on `position.id`, the same non-existent attribute
# the production code used. A mock that mirrors a production bug is the worst kind: it
# lets the bug pass, and then fails the moment the production code is corrected - which is
# exactly what happened here. Both sides now use `position_id`.

for REL in (
    "tests/unit/concurrency/test_execution_concurrency.py",
    "tests/integration/test_e2e_flow.py",
):
    path = ROOT / REL
    if not path.is_file():
        continue
    text = load(REL)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    before = work

    work = re.sub(r"\bposition\.id\b", "position.position_id", work)
    work = re.sub(r"\bpos\.id\b", "pos.position_id", work)
    work = re.sub(r"\bp\.id\b", "p.position_id", work)
    work = re.sub(r"\bnew_position\.id\b", "new_position.position_id", work)

    if work != before:
        save(REL, work, crlf)
        print(f"  ok  {REL}: mock repositories key on position_id")
    else:
        print(f"  --  {REL}: nothing to change")
