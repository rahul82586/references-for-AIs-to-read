"""
Step M3 part 11 - carry the two newly-modelled currencies through the export path.

`symbol_mt5_record` rebuilds the MT5 wire record for a stored symbol. It listed
`CurrencyBase` among the domain-owned fields but not `CurrencyProfit` or `CurrencyMargin`,
because until M3 neither was stored. They were surviving the round trip only by accident,
inside the `mt5_source` baseline blob - which is why M1's 362/362 proof passed while the
domain still could not see them.

That accident is fragile in a specific way: any code path that constructs a SymbolModel
WITHOUT a baseline (a symbol created through the admin API rather than imported) would
export `CurrencyProfit` as absent, and MT5 would read it as empty. Listing them as owned
fields makes the export correct for both paths, and keeps the baseline as the source of
the exact original string when there is one.

Losslessness is preserved: when the column is empty the value is omitted from `owned`
rather than written as "", so the baseline's original string still wins.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "infrastructure/persistence/config_mappers.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''        "CurrencyBase": row.base_currency or "USD",'''
NEW = '''        "CurrencyBase": row.base_currency or "USD",
        # MT5 keeps three symbol currencies and they are not interchangeable. These two
        # were modelled as of M3; before that they survived the round trip only inside the
        # mt5_source baseline, so a symbol created through the admin API - which has no
        # baseline - would have exported them as absent and MT5 would read them as empty.
        # Only overlaid when the column actually holds a value, so an empty column leaves
        # the baseline's original string untouched and the export stays byte-identical.
        **({"CurrencyProfit": row.quote_currency} if row.quote_currency else {}),
        **({"CurrencyMargin": row.margin_currency} if row.margin_currency else {}),'''

if OLD not in work:
    raise SystemExit("[FAIL] config_mappers.py: the CurrencyBase line in symbol_mt5_record was not found")
work = work.replace(OLD, NEW, 1)

# db_to_symbol: take margin_currency from the rebuilt record, and stop defaulting the
# other two to "USD" - an empty value should stay empty so the domain's own fallback
# (margin -> base) applies rather than being pre-empted by a wrong guess.
OLD2 = '''        base_currency=domain.get("base_currency") or "USD",
        quote_currency=domain.get("quote_currency") or "USD",'''
NEW2 = '''        base_currency=domain.get("base_currency") or "USD",
        quote_currency=domain.get("quote_currency") or "USD",
        # MT5 CurrencyMargin. Empty means "same as the base currency", which Symbol's own
        # __post_init__ resolves - so it is passed through rather than defaulted here.
        margin_currency=domain.get("margin_currency") or "",'''
if OLD2 in work:
    work = work.replace(OLD2, NEW2, 1)
    print("  ok  config_mappers.py: db_to_symbol returns margin_currency")
else:
    raise SystemExit("[FAIL] config_mappers.py: db_to_symbol's currency lines were not found")

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print("  ok  config_mappers.py: symbol_mt5_record exports CurrencyProfit/CurrencyMargin")
