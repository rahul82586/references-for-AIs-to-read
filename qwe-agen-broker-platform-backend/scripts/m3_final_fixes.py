"""
Step M3 part 10 - close out the last defects.

1. symbol_to_db READS A KEY MT5 NEVER EMITS. It resolved quote_currency from
   `extra.get("CurrencyQuote")`, but the MT5 wire field is `CurrencyProfit` - there is no
   CurrencyQuote in the export. So the lookup always missed and fell through to
   `symbol.quote_currency or "USD"`, silently making every symbol USD-quoted. That is the
   persistence half of the cross-currency bug: even with the fieldmap fixed, the value was
   discarded on the way into the database. margin_currency was not written at all.

2. `CommissionTier(volume_from=, volume_to=, value=)` - the test used names from a
   different model. The real fields are volume_min / volume_max / rate.

3. `group.margin_call_level` - the test reads it off Group; it lives on Group.margin, the
   MarginProfile. And the values it sets, `0.8` and `0.5`, are FRACTIONS: MT5's
   MarginCall / MarginStopOut are PERCENT (the live export carries "50.00" and "30.00").
   The assertion `isinstance(group.margin_call_level, Decimal)` was checking a type on an
   attribute that does not exist, so it could never have caught the unit error it sits
   next to. Rewritten to assert the real fields AND that the values are percentages, which
   is the check M1's margin-unit guard exists to enforce.

4. `Position(id=...)` - the field is position_id.

5. test_group_serialization_stress asserts `to_dict()["symbol_overrides_count"]`, a key
   Group.to_dict does not produce. The count is a useful thing to expose - it is how an
   operator sees whether a group's 60-odd per-symbol overrides actually loaded - so the key
   is added rather than the assertion removed.
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


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:300]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. symbol_to_db: read the field MT5 actually emits
# ---------------------------------------------------------------------------

sub(
    "infrastructure/persistence/config_mappers.py",
    '''        base_currency=col("CurrencyBase", "USD") or "USD",
        quote_currency=extra.get("CurrencyQuote") or symbol.quote_currency or "USD",''',
    '''        # MT5's wire fields are CurrencyBase / CurrencyProfit / CurrencyMargin. There is
        # no CurrencyQuote in the export, so the previous `extra.get("CurrencyQuote")`
        # lookup always missed and fell through to "USD" - silently making every imported
        # symbol USD-quoted, which is the persistence half of the cross-currency bug.
        # The domain symbol's own value wins when it is set, because that is what the
        # codec populated from the wire record.
        base_currency=symbol.base_currency or col("CurrencyBase", "USD") or "USD",
        quote_currency=(
            symbol.quote_currency
            or extra.get("CurrencyProfit")
            or col("CurrencyProfit", "")
            or "USD"
        ),
        margin_currency=(
            symbol.margin_currency
            or extra.get("CurrencyMargin")
            or col("CurrencyMargin", "")
            or ""
        ),''',
    "symbol_to_db reads CurrencyProfit/CurrencyMargin (it read a CurrencyQuote key MT5 never emits)",
)

# And read them back out.
text = load("infrastructure/persistence/config_mappers.py")
work = text.replace("\r\n", "\n")
if "def db_to_symbol" in work and "margin_currency=row" not in work:
    match = re.search(
        r"(def db_to_symbol\(row[^\n]*\n(?:.*\n)*?)\s*(base_currency=row\.base_currency[^\n]*\n)"
        r"(\s*)(quote_currency=row\.quote_currency[^\n]*\n)",
        work,
    )
    if match:
        work = work[: match.end(4)] + f"{match.group(3)}margin_currency=row.margin_currency or \"\",\n" + work[match.end(4):]
        save("infrastructure/persistence/config_mappers.py", work, crlf="\r\n" in text)
        print("  ok  config_mappers.py: db_to_symbol returns margin_currency")
    else:
        # Fall back: append after the quote_currency line wherever it appears in db_to_symbol.
        idx = work.find("def db_to_symbol")
        tail = work[idx:]
        q = re.search(r"^(\s*)quote_currency=row\.quote_currency,\s*$", tail, flags=re.M)
        if q:
            insert_at = idx + q.end()
            work = work[:insert_at] + f"\n{q.group(1)}margin_currency=row.margin_currency or \"\"," + work[insert_at:]
            save("infrastructure/persistence/config_mappers.py", work, crlf="\r\n" in text)
            print("  ok  config_mappers.py: db_to_symbol returns margin_currency (fallback anchor)")
        else:
            print("  skip config_mappers.py: could not locate db_to_symbol's quote_currency line")

# ---------------------------------------------------------------------------
# 2. Group.to_dict exposes the override count
# ---------------------------------------------------------------------------

text = load("core/domains/accounts/group.py")
work = text.replace("\r\n", "\n")
if '"symbol_overrides_count"' not in work:
    match = re.search(r"(def to_dict\(self\)[^\n]*\n(?:.*\n)*?)\s*return \{", work)
    if match:
        anchor = match.end()
        # Find the matching dict's closing brace and inject before it.
        depth = 0
        i = anchor
        injected = False
        while i < len(work):
            if work[i] == "{":
                depth += 1
            elif work[i] == "}":
                depth -= 1
                if depth == 0:
                    insertion = (
                        '            # How many per-symbol overrides this group carries. An\n'
                        '            # operator needs this to see whether a group\'s 60-odd MT5\n'
                        '            # group-symbol settings actually loaded.\n'
                        '            "symbol_overrides_count": len(self.symbol_overrides),\n'
                    )
                    # Walk back to the start of the line holding '}'.
                    line_start = work.rfind("\n", 0, i) + 1
                    indent = work[line_start:i]
                    work = work[:i] + insertion.replace("            ", indent) + work[i:]
                    injected = True
                    break
            i += 1
        if injected:
            save("core/domains/accounts/group.py", work, crlf="\r\n" in text)
            print("  ok  group.py: to_dict exposes symbol_overrides_count")
        else:
            print("  skip group.py: could not find to_dict's closing brace")
    else:
        print("  skip group.py: to_dict not found")

# ---------------------------------------------------------------------------
# 3. test_account_models_stress: CommissionTier field names
# ---------------------------------------------------------------------------

REL = "tests/unit/domains/accounts/test_account_models_stress.py"
text = load(REL)
work = text.replace("\r\n", "\n")
before = work
work = work.replace("volume_from=", "volume_min=").replace("volume_to=", "volume_max=")
work = re.sub(
    r"CommissionTier\(([^()]*?)\bvalue=",
    r"CommissionTier(\1rate=",
    work,
)
if work != before:
    save(REL, work, crlf="\r\n" in text)
    print(f"  ok  {REL}: CommissionTier uses volume_min/volume_max/rate")

# ---------------------------------------------------------------------------
# 4. test_audit3_hardening: Group.margin.*, Position.position_id, and the unit check
# ---------------------------------------------------------------------------

REL = "tests/unit/domains/risk/test_audit3_hardening.py"
text = load(REL)
work = text.replace("\r\n", "\n")

OLD = '''        margin=MarginProfile(margin_call_level=Decimal('0.8'), stop_out_level=Decimal('0.5'))
    )
    assert isinstance(group.margin_call_level, Decimal)'''
NEW = '''        margin=MarginProfile(margin_call_level=Decimal('80'), stop_out_level=Decimal('50'))
    )
    # These live on Group.margin (a MarginProfile), not on Group itself - reading
    # group.margin_call_level raised AttributeError, so the original assertion never ran.
    assert isinstance(group.margin.margin_call_level, Decimal)
    assert isinstance(group.margin.stop_out_level, Decimal)
    # And they are PERCENT. MT5's MarginCall / MarginStopOut are percentages - the live
    # export carries "50.00" and "30.00" - and the values this test originally used, 0.8
    # and 0.5, are fractions. A fraction here reads as "stop out at 0.5%", which liquidates
    # every account on the first tick. Asserting the unit is the point of the test; the
    # original only asserted a type, on an attribute that did not exist.
    assert group.margin.margin_call_level > Decimal('1'), (
        "margin_call_level must be a PERCENT (MT5 MarginCall), not a fraction"
    )
    assert group.margin.stop_out_level > Decimal('1'), (
        "stop_out_level must be a PERCENT (MT5 MarginStopOut), not a fraction"
    )'''
if OLD in work:
    work = work.replace(OLD, NEW, 1)
    print(f"  ok  {REL}: decimal-precision test reads Group.margin.* and asserts PERCENT")
else:
    print(f"  skip {REL}: the margin_call_level assertion block was not found")

work = re.sub(r"^(\s*)id=\"POS_", r'\1position_id="POS_', work, flags=re.M)
work = re.sub(r"Position\(([^()]*?)\bid=", r"Position(\1position_id=", work)
save(REL, work, crlf="\r\n" in text)
print(f"  ok  {REL}: Position(id=...) -> Position(position_id=...)")

# ---------------------------------------------------------------------------
# 5. test_cross_currency_pnl: Position(id=...)
# ---------------------------------------------------------------------------

REL = "tests/unit/domains/risk/test_cross_currency_pnl.py"
text = load(REL)
work = text.replace("\r\n", "\n")
before = work
work = re.sub(r"^(\s*)id=\"POS_", r'\1position_id="POS_', work, flags=re.M)
work = re.sub(r"Position\(([^()]*?)\bid=", r"Position(\1position_id=", work)
if work != before:
    save(REL, work, crlf="\r\n" in text)
    print(f"  ok  {REL}: Position(id=...) -> Position(position_id=...)")
