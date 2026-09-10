"""
Step M3 part 12 - precise fixes for the five leftovers.

Each of these is a narrow miss from a regex that was too general, plus one real product
bug it exposed:

1. `Group.to_dict` - the previous step's brace-matching injected `symbol_overrides_count`
   into the NESTED "margin" dict (it found the first `{` after `return`, which is the
   margin sub-dict's opening brace two lines down). The key must sit at the top level, and
   the misplaced injection has to come back out.

2. `CommissionTier(value=...)` - the rename regex only matched `value=` as the FIRST
   argument inside the parentheses. Here it is third, after volume_min/volume_max.

3. `Position(side=OrderType.BUY)` - the field is `action` and it takes a PositionAction,
   not an OrderType. `side` never existed on Position.

4. `group.stop_out_level` - the sibling of the margin_call_level line already fixed; it
   lives on Group.margin.

5. `test_group_serialization_stress` will pass once (1) is correct.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


# ---------------------------------------------------------------------------
# 1. Group.to_dict - remove the misplaced injection, add it at top level
# ---------------------------------------------------------------------------

REL = "core/domains/accounts/group.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

# Strip the misplaced block wherever it landed.
work = re.sub(
    r"[ \t]*# How many per-symbol overrides this group carry\.[^\n]*\n"
    r"[ \t]*# operator needs this[^\n]*\n"
    r"[ \t]*# group-symbol settings actually loaded\.\n"
    r'[ \t]*"symbol_overrides_count": len\(self\.symbol_overrides\),\n',
    "",
    work,
)

# Add it at the top level of the returned dict, right after "currency".
OLD = '''            "currency": self.currency,
            "margin": {'''
NEW = '''            "currency": self.currency,
            # How many per-symbol overrides this group carries. An operator needs this to
            # see whether a group's 60-odd MT5 group-symbol settings actually loaded; a
            # group that imported with zero overrides looks identical to one that failed.
            "symbol_overrides_count": len(self.symbol_overrides),
            "commissions_count": len(self.commissions),
            "margin": {'''
if OLD not in work:
    raise SystemExit("[FAIL] group.py: to_dict's top-level anchor was not found")
work = work.replace(OLD, NEW, 1)
save(REL, work, crlf)
print("  ok  group.py: symbol_overrides_count at the TOP level of to_dict (was injected into the nested margin dict)")

# ---------------------------------------------------------------------------
# 2. CommissionTier(value=...) anywhere in the call, not just first
# ---------------------------------------------------------------------------

REL = "tests/unit/domains/accounts/test_account_models_stress.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")
before = work
# Inside a CommissionTier(...) call only, rename value= to rate=. Done by locating each
# call and rewriting its argument list, so unrelated value= kwargs are untouched.
def _fix_tier(match: re.Match) -> str:
    inner = match.group(1)
    return "CommissionTier(" + re.sub(r"\bvalue=", "rate=", inner) + ")"

work = re.sub(r"CommissionTier\(([^()]*)\)", _fix_tier, work)
if work != before:
    save(REL, work, crlf)
    print(f"  ok  {REL}: CommissionTier(value=) -> rate= in any argument position")
else:
    print(f"  --  {REL}: no CommissionTier(value=) left")

# ---------------------------------------------------------------------------
# 3/4. Position(side=OrderType.X) -> action=PositionAction.X; group.stop_out_level
# ---------------------------------------------------------------------------

for REL in (
    "tests/unit/domains/risk/test_cross_currency_pnl.py",
    "tests/unit/domains/risk/test_audit3_hardening.py",
    "tests/unit/concurrency/test_execution_concurrency.py",
    "tests/unit/api/test_api.py",
    "tests/integration/test_e2e_flow.py",
):
    path = ROOT / REL
    if not path.is_file():
        continue
    text = load(REL)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    before = work

    # side=OrderType.BUY -> action=PositionAction.BUY
    work = re.sub(
        r"\bside=OrderType\.(BUY|SELL)\b", r"action=PositionAction.\1", work
    )
    # group.stop_out_level / group.margin_call_level -> group.margin.*
    work = re.sub(
        r"\bgroup\.stop_out_level\b", "group.margin.stop_out_level", work
    )
    work = re.sub(
        r"\bgroup\.margin_call_level\b", "group.margin.margin_call_level", work
    )
    # Guard against a double prefix from the previous step's rewrite.
    work = work.replace("group.margin.margin.margin", "group.margin.margin")
    work = work.replace("group.margin.stop_out_level", "group.margin.stop_out_level")

    # PositionAction must be imported where we just used it.
    if "PositionAction" in work and not re.search(
        r"^from .*import .*PositionAction", work, flags=re.M
    ):
        work = re.sub(
            r"^(from core\.domains\.oms\.entities\.position import [^\n]+)$",
            r"\1\nfrom core.domains.oms.enums import PositionAction",
            work,
            count=1,
            flags=re.M,
        )
        if "from core.domains.oms.enums import PositionAction" not in work:
            work = "from core.domains.oms.enums import PositionAction\n" + work

    # Group(leverage_default=N) -> Group(margin=MarginProfile(leverage_default=N)).
    # Leverage lives on the nested MarginProfile; Group has no such field.
    work = re.sub(
        r"Group\(([^()]*?)leverage_default=(\d+)([^()]*?)\)",
        r"Group(\1margin=MarginProfile(leverage_default=\2)\3)",
        work,
    )
    if "MarginProfile(" in work and not re.search(
        r"^from .*import .*MarginProfile", work, flags=re.M
    ):
        work = re.sub(
            r"^(from core\.domains\.accounts\.models import [^\n]+)$",
            lambda m: m.group(1) if "MarginProfile" in m.group(1)
            else m.group(1).rstrip() + ", MarginProfile",
            work,
            count=1,
            flags=re.M,
        )
        if "MarginProfile" not in work.split("\n\n")[0]:
            work = "from core.domains.accounts.models import MarginProfile\n" + work

    # WebSocketEventBridge takes an event_bus, not a connection_manager. It resolves its
    # subscription manager internally via get_manager_subscription_manager().
    work = re.sub(
        r"WebSocketEventBridge\(connection_manager=([^,)]+)(,?)\s*\)",
        r"WebSocketEventBridge(event_bus=\1\2)",
        work,
    )

    if work != before:
        save(REL, work, crlf)
        print(f"  ok  {REL}: entity vocabulary resynced")
    else:
        print(f"  --  {REL}: nothing to change")
