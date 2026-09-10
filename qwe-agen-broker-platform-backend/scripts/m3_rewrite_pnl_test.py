"""
Step M3 part 14 - the cross-currency PnL test asserted the wrong thing.

`test_cross_currency_pnl_calculation_eurjpy_on_usd_account` wanted to verify that a EURJPY
position on a USD account has its PnL converted from JPY. To do that it called
`select_positions_for_liquidation` and asserted the position came back:

    assert len(positions_with_pnl) == 1

But the position it built is PROFITABLE - opened at 160.000 with a bid of 161.000, a gain
of 100,000 JPY - on an account with 5,000 USD and no margin used. That account is nowhere
near stop-out, so MT5's rule ("close worst-loss positions first until margin level
recovers") selects NOTHING. The assertion could only ever pass on an engine that
liquidated positions regardless of whether liquidation was warranted, which is the
opposite of correct.

It was also the test the original audit called out as having a `pass` body - it never
measured a PnL figure at all, so the cross-currency conversion it claims to verify was
never actually checked.

Rewritten to assert the conversion directly, using the public margin snapshot:

    BUY 1 lot EURJPY @ 160.000, bid 161.000, contract 100,000
    PnL in JPY   = (161.000 - 160.000) * 1 * 100,000 = 100,000 JPY
    JPY -> USD   = 1 / 150.000 (the feed's USDJPY ask, via the inverse pair)
    PnL in USD   = 666.67
    equity       = 5,000 + 666.67 = 5,666.67

666.67 is the figure the original audit's own table gives for a 1-lot JPY pair, and it is
the number that was unreachable while the engine assumed quote == deposit.

The companion test asserted the exact legacy error STRING ("Missing exchange rate for
JPY -> USD"). The new message names every route that was tried - direct, inverse, and each
triangulation currency - because an operator diagnosing a halted account needs to know
which pairs are missing, not just that one is. The assertion is relaxed to the part that
carries the information: the currency pair.
"""

from __future__ import annotations

import pathlib
import re
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

# ---------------------------------------------------------------------------
# 1. Replace the EURJPY PnL test
# ---------------------------------------------------------------------------

start = work.find("def test_cross_currency_pnl_calculation_eurjpy_on_usd_account")
if start == -1:
    raise SystemExit("[FAIL] the EURJPY test was not found")
end_marker = work.find("def test_cross_currency_pnl_missing_rate_raises_error", start)
if end_marker == -1:
    raise SystemExit("[FAIL] the following test was not found; cannot bound the replacement")

NEW = '''def test_cross_currency_pnl_calculation_eurjpy_on_usd_account():
    """A EURJPY position on a USD account must have its PnL converted from JPY.

    This is the case the original audit flagged and the reason CurrencyProfit /
    CurrencyMargin had to be modelled: the position's profit is denominated in JPY, the
    account is in USD, and neither EURUSD nor a direct JPYUSD symbol exists in the feed.
    The rate has to be resolved through the inverse USDJPY pair.

        BUY 1 lot EURJPY @ 160.000, bid 161.000, contract size 100,000
        PnL in JPY = (161.000 - 160.000) * 1 * 100,000 = 100,000 JPY
        JPY -> USD = 1 / 150.000   (from the feed's USDJPY ask, via the inverse pair)
        PnL in USD = 666.67
        equity     = 5,000.00 + 666.67 = 5,666.67

    A BUY position is valued at the BID, because the bid is what the broker transacts at
    to close it. Valuing at the ask would hand the spread to the client on every position.

    Note what this test does NOT do: it no longer calls
    select_positions_for_liquidation and asserts the position comes back. This position is
    profitable and the account has no margin used, so MT5's rule - "close worst-loss
    positions first until margin level recovers" - selects nothing. The previous assertion
    could only pass on an engine that liquidated positions regardless of whether
    liquidation was warranted.
    """
    eurjpy = Symbol(
        name="EURJPY",
        path="Forex" + chr(92) + "EURJPY",
        tick_size=Decimal('0.001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=3,
        # MT5's own values. CurrencyProfit is what PnL is denominated in - JPY here - and
        # CurrencyMargin is what the requirement is computed in. Neither is derivable from
        # the name for a cross pair, which is why the name heuristic is only a fallback.
        base_currency="EUR",
        quote_currency="JPY",
        margin_currency="EUR",
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
    )
    account = Account(
        login=200001,
        group=Group(name="REAL_STANDARD", margin=MarginProfile(leverage_default=100)),
        account_type=AccountType.REAL,
        currency="USD",
        balance=Money(Decimal('5000.00'), "USD"),
    )
    position = Position(
        position_id="POS_EURJPY_1",
        account_login="200001",
        symbol="EURJPY",
        volume=Volume(Decimal('1.0')),
        action=PositionAction.BUY,
        price_open=Price(Decimal('160.000')),
        contract_size=Decimal('100000'),
        time_create=datetime.now(timezone.utc),
    )

    market_feed = MockMarketFeedWithCrossRates({
        "EURJPY": {"bid": "161.000", "ask": "161.005"},
        "USDJPY": {"bid": "149.990", "ask": "150.000"},
    })
    symbol_repo = MockSymbolRepository([eurjpy])
    risk_engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=market_feed)

    # The conversion resolves through the inverse pair: there is no JPYUSD symbol.
    rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed)
    assert rate == Decimal('1.0') / Decimal('150.000')

    snapshot = risk_engine.calculate_margin_level(account, [position])

    # 100,000 JPY of profit, converted at 1/150 -> 666.67 USD.
    expected_pnl = (Decimal('100000') / Decimal('150')).quantize(Decimal('0.01'))
    assert expected_pnl == Decimal('666.67'), (
        "the audit's own table gives ~$6.67 per pip per lot on a JPY pair; 100 pips is 666.67"
    )
    assert snapshot.equity.quantize(Decimal('0.01')) == Decimal('5000.00') + expected_pnl

    # The margin requirement is in EUR and must also be converted, not assumed to be USD.
    # 1 lot * 100,000 / 100 = 1,000 EUR, converted via EURUSD triangulated from USDJPY.
    assert snapshot.margin_used > Decimal('1000'), (
        "1,000 EUR of margin must convert to more than 1,000 USD at any plausible EURUSD"
    )
    assert snapshot.margin_used < Decimal('2000')

    # Nothing should be liquidated: the account is profitable and far from stop-out.
    to_close = risk_engine.select_positions_for_liquidation(
        account=account,
        positions=[position],
        symbol_repo=symbol_repo,
        market_feed=market_feed,
    )
    assert to_close == [], (
        "a profitable position on an account with no margin pressure must not be selected "
        "for liquidation"
    )


'''

work = work[:start] + NEW + work[end_marker:]

# ---------------------------------------------------------------------------
# 2. Relax the legacy error-string assertion
# ---------------------------------------------------------------------------

OLD_ASSERT = '''    assert "Missing exchange rate for JPY -> USD" in str(exc_info.value)'''
NEW_ASSERT = '''    # The message names the pair and every route tried - direct, inverse, and each
    # triangulation currency - because an operator diagnosing a halted account needs to
    # know which pairs are missing, not merely that one is. The legacy wording
    # ("Missing exchange rate for JPY -> USD") carried less information.
    message = str(exc_info.value)
    assert "JPY -> USD" in message or ("JPY" in message and "USD" in message), (
        f"the error must name the unresolvable pair, got: {message}"
    )'''
if OLD_ASSERT in work:
    work = work.replace(OLD_ASSERT, NEW_ASSERT, 1)
    print("  ok  missing-rate test: assertion relaxed to the informative part of the message")
else:
    print("  skip missing-rate test: the legacy string assertion was not found")

# MarginProfile must be imported.
if "MarginProfile(" in work and not re.search(r"^from .*import .*MarginProfile", work, flags=re.M):
    work = re.sub(
        r"^(from core\.domains\.accounts\.models import [^\n]+)$",
        lambda m: m.group(1) if "MarginProfile" in m.group(1)
        else m.group(1).rstrip() + (", MarginProfile" if not m.group(1).endswith("(") else "MarginProfile, "),
        work,
        count=1,
        flags=re.M,
    )
    if "MarginProfile" not in work.split("def ")[0]:
        work = "from core.domains.accounts.models import MarginProfile\n" + work
    print("  ok  MarginProfile imported")

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print(f"  ok  {REL}: EURJPY test now asserts the converted PnL (666.67 USD), not a liquidation selection")
