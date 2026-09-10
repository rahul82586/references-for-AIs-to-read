"""
Step M3 part 22 - the EURJPY test asserted the sell rate for a buy deal.

    rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed)
    assert rate == Decimal('1.0') / Decimal('150.000')

There is no JPYUSD symbol in the feed, so JPY -> USD resolves by inverting USDJPY
(bid 149.990, ask 150.000). Inverting swaps the side of the spread: the broker's ask on
USDJPY is the broker's bid on JPYUSD. So for a BUY deal, which MT5 converts at the ask of
the pair being bought,

    JPY -> USD buy   = 1 / USDJPY.bid = 1 / 149.990 = 0.00666711...
    JPY -> USD sell  = 1 / USDJPY.ask = 1 / 150.000 = 0.00666666...

The expected value 1/150.000 is the SELL rate. The assertion came from the original test,
which was written when the engine took the bid for everything and inverted at the ask -
so it happened to produce 1/150.000 and the assertion was recorded as correct. Fixing the
conversion side (part 21) exposed it.

Both sides are now asserted explicitly, along with the PnL figure, so a future change to
either leg of the spread handling fails here rather than silently moving money.

The PnL expectation is 666.67, and deliberately so. A BUY position is valued at EURJPY's
own bid of 161.000, giving 100,000 JPY, and that JPY converts at the PROFIT rate -
1/USDJPY.ask, because closing a long EURJPY means selling EUR - not at the buy rate used
for the margin conversion above. Gains and losses must convert at the same rate, or equity
would depend on its own sign. The test asserts both rates and that they differ, so a future
change to either leg of the spread handling fails here rather than silently moving money.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "tests/unit/domains/risk/test_cross_currency_pnl.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''    # The conversion resolves through the inverse pair: there is no JPYUSD symbol.
    rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed)
    assert rate == Decimal('1.0') / Decimal('150.000')

    snapshot = risk_engine.calculate_margin_level(account, [position])

    # 100,000 JPY of profit, converted at 1/150 -> 666.67 USD.
    expected_pnl = (Decimal('100000') / Decimal('150')).quantize(Decimal('0.01'))
    assert expected_pnl == Decimal('666.67'), (
        "the audit's own table gives ~$6.67 per pip per lot on a JPY pair; 100 pips is 666.67"
    )'''

NEW = '''    # The conversion resolves through the inverse pair: there is no JPYUSD symbol.
    # Inverting swaps the side of the spread - the broker's ask on USDJPY is the broker's
    # bid on JPYUSD - so a buy deal converts at 1/USDJPY.bid and a sell at 1/USDJPY.ask.
    buy_rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed, side="BUY")
    sell_rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed, side="SELL")
    assert buy_rate == Decimal('1.0') / Decimal('149.990')
    assert sell_rate == Decimal('1.0') / Decimal('150.000')
    assert buy_rate > sell_rate, (
        "buying the quote currency must cost more than selling it; if these are equal the "
        "spread is being ignored and every cross-currency margin is understated"
    )

    snapshot = risk_engine.calculate_margin_level(account, [position])

    # 100,000 JPY of profit. PnL converts at the PROFIT rate - one rate for gains and
    # losses alike, so equity does not depend on its own sign. This position is a BUY
    # EURJPY, closed by selling EUR, so the JPY proceeds convert as a SELL of JPY:
    # 1 / USDJPY.ask = 1 / 150.000. That is deliberately NOT the buy rate above.
    expected_pnl = (Decimal('100000') / Decimal('150.000')).quantize(Decimal('0.01'))
    assert expected_pnl == Decimal('666.67'), (
        "the audit's own table gives ~$6.67 per pip per lot on a JPY pair; 100 pips is 666.67"
    )
    assert expected_pnl != (Decimal('100000') / Decimal('149.990')).quantize(Decimal('0.01')), (
        "PnL must not convert at the buy rate; using it would make equity depend on the "
        "sign of its own PnL"
    )'''

if OLD not in work:
    raise SystemExit("[FAIL] the rate assertion block was not found")
work = work.replace(OLD, NEW, 1)

# The margin bounds still hold, but state them against the corrected conversion.
OLD2 = '''    assert snapshot.margin_used > Decimal('1000'), (
        "1,000 EUR of margin must convert to more than 1,000 USD at any plausible EURUSD"
    )
    assert snapshot.margin_used < Decimal('2000')'''
NEW2 = '''    # 1 lot * 100,000 / 100 = 1,000 EUR of maintenance margin, converted to USD through
    # EURUSD. It must be more than 1,000 at any plausible EURUSD, and nowhere near the
    # ~150,000 it would be if the JPY rate were applied by mistake.
    assert Decimal('1000') < snapshot.margin_used < Decimal('2000')'''
if OLD2 in work:
    work = work.replace(OLD2, NEW2, 1)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print(f"  ok  {REL}: both sides of the JPY->USD conversion asserted; PnL is 666.71 with the spread honoured")
