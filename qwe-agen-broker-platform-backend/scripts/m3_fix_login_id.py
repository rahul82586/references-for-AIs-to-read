"""
Step M3 part 17 - RecordDealHandler read a field that does not exist, on every deal.

`Account` has `login`. It has never had `login_id`. But RecordDealHandler - the command
that records a deal, updates the balance, and opens or closes the resulting position -
reads `account.login_id` at NINE sites:

    line 142  logger.debug(f"Account {account.login_id} balance updated ...")
    line 200  position_id = f"{account.login_id}_{deal.symbol}_{uuid...}"
    line 204  account_login=account.login_id          <- the new Position
    line 224  "account_login": account.login_id       <- the event payload
    line 242  pos_repo.get_positions_by_account(account.login_id)
    line 285  position_id = f"{account.login_id}_..."  <- the close path
    line 289  account_login=account.login_id
    line 303  position_id = f"{account.login_id}_..."  <- the reverse path
    line 306  account_login=account.login_id

Every one of them raises AttributeError. So no deal could ever be recorded: not opened,
not closed, not reversed. This is the single most load-bearing handler in the execution
path and it was unreachable, which is consistent with the M0 finding that the CLI and
admin API were stubs - the system had never actually executed a trade end to end.

`application/queries/get_account_info.py:55` has the same defect in its response dict, so
the account-info endpoint 500s.

Both are corrected to `account.login`. The query's RESPONSE KEY stays `login_id`, because
that is the API's published field name and changing it would break clients; only the
attribute read is wrong.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "application").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

TARGETS = [
    "application/commands/record_deal.py",
    "application/queries/get_account_info.py",
]

total = 0
for rel in TARGETS:
    path = ROOT / rel
    if not path.is_file():
        print(f"  skip {rel}: not found")
        continue
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")

    # Only the ATTRIBUTE READ is wrong. `query.login_id` (a query DTO field) and
    # `"login_id":` (a published response key) are correct and must not change.
    count = len(re.findall(r"\baccount\.login_id\b", work))
    work = re.sub(r"\baccount\.login_id\b", "account.login", work)

    if count:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(work.replace("\n", "\r\n") if crlf else work)
        print(f"  ok  {rel}: {count} read(s) of account.login_id -> account.login")
        total += count
    else:
        print(f"  --  {rel}: no account.login_id reads")

if total == 0:
    raise SystemExit("[FAIL] no account.login_id reads were found; the pattern has changed")
print(f"  ==  {total} broken attribute reads fixed across the deal-recording path")

# ---------------------------------------------------------------------------
# Position(id=...) -> position_id, in the same handler
# ---------------------------------------------------------------------------
#
# The field is `position_id`. `id` was the deleted duplicate PositionModel's name, and
# these three constructions sit in _apply_deal_to_positions - the code that opens a
# position when a deal is recorded. Together with the nine login_id reads above, every
# path through RecordDealHandler raised AttributeError, so no position could be opened,
# closed or reversed. The handler was unreachable in its entirety.

REL = "application/commands/record_deal.py"
path = ROOT / REL
with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

count = len(re.findall(r"^\s*id=position_id,$", work, flags=re.M))
work = re.sub(r"^(\s*)id=position_id,$", r"\1position_id=position_id,", work, flags=re.M)

if count:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(work.replace("\n", "\r\n") if crlf else work)
    print(f"  ok  {REL}: {count} Position(id=position_id) -> position_id=position_id")
else:
    print(f"  --  {REL}: no Position(id=...) constructions left")

# ---------------------------------------------------------------------------
# The remaining stale field names in the same Position constructions
# ---------------------------------------------------------------------------
#
#   side=           -> action=         (Position has `action`, a PositionAction)
#   average_price=  -> price_open=     (`average_price` was the deleted duplicate model's)
#   opened_at=      -> time_create=    (MT5's own name; the entity uses time_create)
#
# These are the same three names that made RiskEngine read `.side`, `.average_price` and
# `.id` and get zero for every position's PnL and margin. They appear here in the code
# that CREATES positions, so the two halves of the system disagreed about the shape of its
# central entity - and because both were wrapped in exception handling, neither ever
# surfaced as an error.

REL = "application/commands/record_deal.py"
path = ROOT / REL
with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

renames = [
    ("side", "action", r"^(\s*)side=", r"\1action="),
    ("average_price", "price_open", r"^(\s*)average_price=", r"\1price_open="),
    ("opened_at", "time_create", r"^(\s*)opened_at=", r"\1time_create="),
    ("closed_at", "time_done", r"^(\s*)closed_at=", r"\1time_done="),
]
applied = []
for old_name, new_name, pattern, replacement in renames:
    hits = len(re.findall(pattern, work, flags=re.M))
    if hits:
        work = re.sub(pattern, replacement, work, flags=re.M)
        applied.append("%dx %s->%s" % (hits, old_name, new_name))

if applied:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(work.replace("\n", "\r\n") if crlf else work)
    print(f"  ok  {REL}: Position field names aligned to the entity ({', '.join(applied)})")
else:
    print(f"  --  {REL}: no stale Position field names left")

# ---------------------------------------------------------------------------
# The same stale names on the READ side, across netting and hedging
# ---------------------------------------------------------------------------
#
#   position.side            -> position.action
#   position.average_price   -> position.price_open
#   position.id              -> position.position_id
#
# These sit in _apply_deal_netting_mode, which is the logic that aggregates a new deal
# into an existing position: it matches on direction, computes the weighted average open
# price, and deletes the opposite position when it is fully closed. That is exactly MT5's
# netting rule ("Their volumes are summed up and the weighted average open price is
# calculated for them"), and every line of it raised AttributeError.
#
# Only attribute accesses on Position objects are renamed. `deal.deal_type`, the event
# payload's "side" KEY and any local named deal_side are left alone - those are correct.

REL = "application/commands/record_deal.py"
path = ROOT / REL
with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

READS = [
    # <receiver>.side -> .action  (Position receivers only)
    (r"\b(new_position|matching_position|opp_pos|position|pos|p)\.side\b", r"\1.action"),
    (r"\b(new_position|matching_position|opp_pos|position|pos|p)\.average_price\b", r"\1.price_open"),
    (r"\b(new_position|matching_position|opp_pos|position|pos|p)\.id\b", r"\1.position_id"),
]
applied = []
for pattern, replacement in READS:
    hits = len(re.findall(pattern, work))
    if hits:
        work = re.sub(pattern, replacement, work)
        applied.append("%dx %s" % (hits, pattern.split("(")[1].split(")")[0]))

if applied:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(work.replace("\n", "\r\n") if crlf else work)
    print("  ok  %s: Position attribute reads aligned (%s)" % (REL, ", ".join(applied)))
else:
    print("  --  %s: no stale Position attribute reads left" % REL)
