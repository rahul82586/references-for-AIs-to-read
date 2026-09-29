"""
M3 proof: the risk maths, checked against figures that come from outside this codebase.

The acceptance criterion for M3 was set at M0, in `opencode_summery.md`'s validation
table, and has not changed since:

    EURUSD / USD account, 1 lot, 1 pip -> $10.00
    USDJPY / USD account, 1 lot, 1 pip -> ~$6.67
    EURJPY / USD account, 1 lot, 1 pip -> ~$6.67
    GBPAUD / USD account, 1 lot, 1 pip -> ~$6.50

Those four numbers are reproduced here from first principles, alongside MT5's own published
worked examples from Platform-Setup.md, and a full stop-out cycle on a real imported group.
Every expected value is quoted from a source that is not this codebase, so the proof cannot
pass by agreeing with itself - which is exactly how five different margin formulas coexisted
for so long.

Run:
    PYTHONPATH=work/bp BROKER_MT5_FIXTURES=decoded/mt5-format-structure \\
        python3 scripts/m3_proof_margin.py work/bp
"""

from __future__ import annotations

import pathlib
import sys
from decimal import Decimal

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))

from core.domains.market_data.margin import (  # noqa: E402
    Leg,
    SymbolMarginSpec,
    apply_rate,
    basic_margin,
    calculate_account_margin,
    convert_to_deposit,
    margin_level,
    position_pnl,
)

FAILURES: list = []


def check(label: str, got: Decimal, want: Decimal, source: str) -> None:
    ok = got == want
    print(f"    [{'PASS' if ok else 'FAIL'}] {label:<46} {got}")
    if not ok:
        print(f"           expected {want}   ({source})")
        FAILURES.append(f"{label}: got {got}, expected {want}")


def cents(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


LOT = Decimal("1")
FX_CONTRACT = Decimal("100000")


def audit_validation_rows() -> None:
    """The four rows from opencode_summery.md, the acceptance criterion since M0."""
    print("\n[1] The audit's validation table (PnL per 1 pip, 1 lot, USD account)")

    # EURUSD: quote currency IS the deposit currency, so no conversion.
    eurusd = position_pnl(
        side="BUY", volume_lots=LOT, open_price=Decimal("1.10000"),
        bid=Decimal("1.10010"), ask=Decimal("1.10020"), contract_size=FX_CONTRACT,
        quote_currency="USD", deposit_currency="USD", rate_lookup=None,
    )
    check("EURUSD 1 pip, quote=USD", cents(eurusd), Decimal("10.00"),
          "audit table: $10.00")

    # USDJPY: PnL is in JPY, converted at 150 JPY/USD.
    jpy = lambda src, dst, side: Decimal("1") / Decimal("150")
    usdjpy = position_pnl(
        side="BUY", volume_lots=LOT, open_price=Decimal("150.000"),
        bid=Decimal("150.010"), ask=Decimal("150.020"), contract_size=FX_CONTRACT,
        quote_currency="JPY", deposit_currency="USD", rate_lookup=jpy,
    )
    check("USDJPY 1 pip, 1000 JPY / 150", cents(usdjpy), Decimal("6.67"),
          "audit table: ~$6.67")

    # EURJPY: a CROSS pair. The PnL is still in JPY, so the same conversion applies - but
    # neither leg is USD, which is why the old two-try lookup could not resolve it.
    eurjpy = position_pnl(
        side="BUY", volume_lots=LOT, open_price=Decimal("160.000"),
        bid=Decimal("160.010"), ask=Decimal("160.020"), contract_size=FX_CONTRACT,
        quote_currency="JPY", deposit_currency="USD", rate_lookup=jpy,
    )
    check("EURJPY 1 pip, cross pair via JPY", cents(eurjpy), Decimal("6.67"),
          "audit table: ~$6.67")

    # GBPAUD: PnL in AUD, converted at 1.54 AUD/USD.
    aud = lambda src, dst, side: Decimal("1") / Decimal("1.54")
    gbaud = position_pnl(
        side="BUY", volume_lots=LOT, open_price=Decimal("1.54000"),
        bid=Decimal("1.54010"), ask=Decimal("1.54020"), contract_size=FX_CONTRACT,
        quote_currency="AUD", deposit_currency="USD", rate_lookup=aud,
    )
    check("GBPAUD 1 pip, 10 AUD / 1.54", cents(gbaud), Decimal("6.49"),
          "audit table: ~$6.50 (6.49 at 1.54, 6.50 at 1.538)")


def mt5_published_examples() -> None:
    """MT5's own worked examples, quoted from Platform-Setup.md."""
    print("\n[2] MT5's published worked examples (Platform-Setup.md)")

    # "1 * 100000 / 100 = EUR 1000"  (Margin-Calculation/Basic, #forex)
    fx = SymbolMarginSpec(name="EURUSD", contract_size=FX_CONTRACT, calc_mode=0,
                          margin_currency="EUR")
    check("Forex basic: 1 lot, 100k contract, 1:100",
          basic_margin(fx, LOT, Decimal("1.2790"), leverage=100), Decimal("1000"),
          "Basic.md: '1 * 100000 / 100 = EUR 1000'")

    # "if the current rate is 1.2790, the total margin size is 1279 USD" (#conversion)
    converted = convert_to_deposit(
        Decimal("1000"), margin_currency="EUR", deposit_currency="USD",
        side="BUY", rate_lookup=lambda *a: Decimal("1.2790"),
    )
    check("Conversion: 1000 EUR at 1.2790", cents(converted), Decimal("1279.00"),
          "Hedging.md #conversion: 'the total margin size is 1279 USD'")

    # "multiplied by long margin rate ... 1.15, the final margin is 1279 * 1.15 = 1470.85"
    rated_spec = SymbolMarginSpec(name="EURUSD", contract_size=FX_CONTRACT, calc_mode=0,
                                  rates={"initial_buy": Decimal("1.15")})
    check("Rate multiplier: 1279 * 1.15",
          apply_rate(Decimal("1279"), rated_spec, "BUY", maintenance=False),
          Decimal("1470.85"), "Hedging.md #rate: '1279 * 1.15 = 1470.85 USD'")

    # The hedging example: Buy 1 @15.436, Buy 2 @15.432, Buy Limit 1 @15.412,
    # contract 5,000, leverage 1:100 -> 2315.00 + 770.60 = 3085.60
    cfd = SymbolMarginSpec(name="CFDX", contract_size=Decimal("5000"), calc_mode=4)
    legs = [
        Leg(symbol="CFDX", operation="BUY", volume=Decimal("1"), price=Decimal("15.436")),
        Leg(symbol="CFDX", operation="BUY", volume=Decimal("2"), price=Decimal("15.432")),
        Leg(symbol="CFDX", operation="BUY_LIMIT", volume=Decimal("1"),
            price=Decimal("15.412"), is_pending=True),
    ]
    result = calculate_account_margin(
        legs, specs={"CFDX": cfd}, deposit_currency="USD", rate_lookup=None, leverage=100
    )
    check("Hedging example: positions (weighted avg)",
          cents(result.uncovered["CFDX"]), Decimal("2315.00"),
          "Hedging.md: '3 * 5 000 * 15.433333333 / 100 = 2 315.00'")
    check("Hedging example: pending order",
          cents(result.pending["CFDX"]), Decimal("770.60"),
          "Hedging.md: '1 * 5 000 * 15.412 / 100 = 770.60'")
    check("Hedging example: total", cents(result.total), Decimal("3085.60"),
          "Hedging.md: '2 315.00 + 770.60 = 3 085.60'")

    # The hedged-volume example: Buy 1 + Sell 1, contract 100,000, Hedged 100,000
    # -> "the margin for the two positions will be calculated as per 1 lot"
    hedged = SymbolMarginSpec(name="EURUSD", contract_size=FX_CONTRACT, calc_mode=0,
                              margin_hedged=FX_CONTRACT)
    hedge_legs = [
        Leg(symbol="EURUSD", operation="BUY", volume=LOT, price=Decimal("1.1")),
        Leg(symbol="EURUSD", operation="SELL", volume=LOT, price=Decimal("1.1")),
    ]
    hedge_result = calculate_account_margin(
        hedge_legs, specs={"EURUSD": hedged}, deposit_currency="USD",
        rate_lookup=None, leverage=100,
    )
    check("Hedged volume charged as 1 lot", hedge_result.total, Decimal("1000"),
          "Hedging.md: 'the margin for the two positions will be calculated as per 1 lot'")

    free_hedge = SymbolMarginSpec(name="EURUSD", contract_size=FX_CONTRACT, calc_mode=0,
                                  margin_hedged=Decimal("0"))
    free_result = calculate_account_margin(
        hedge_legs, specs={"EURUSD": free_hedge}, deposit_currency="USD",
        rate_lookup=None, leverage=100,
    )
    check("Hedged volume free when Hedged=0", free_result.total, Decimal("0"),
          "Hedging.md: 'If you specify 0, no margin is charged for the hedged volume'")

    # "22 * 100,000 / 100 = 22,000 USD" before the leverage-tier rule applies.
    usdchf = SymbolMarginSpec(name="USDCHF", contract_size=FX_CONTRACT, calc_mode=0)
    check("Leverage example: 22 lots pre-tier",
          basic_margin(usdchf, Decimal("22"), Decimal("0"), leverage=100),
          Decimal("22000"), "Leverages.md: '22 * 100,000 / 100 = 22,000 USD'")


def bid_ask_asymmetry() -> None:
    """The two spread rules that were both being violated."""
    print("\n[3] Spread handling (the two rules that were violated)")

    common = dict(volume_lots=LOT, open_price=Decimal("1.10000"),
                  bid=Decimal("1.10010"), ask=Decimal("1.10030"),
                  contract_size=FX_CONTRACT, quote_currency="USD",
                  deposit_currency="USD", rate_lookup=None)
    buy = cents(position_pnl(side="BUY", **common))
    sell = cents(position_pnl(side="SELL", **common))
    check("BUY valued at BID (+1 pip)", buy, Decimal("10.00"),
          "a long closes at the bid")
    check("SELL valued at ASK (-3 pip)", sell, Decimal("-30.00"),
          "a short closes at the ask")
    if buy == sell:
        FAILURES.append("buy and sell valued at the same price: the spread is being given away")
        print("    [FAIL] buy and sell must differ by the spread")
    else:
        print("    [PASS] buy and sell differ by the spread")

    seen = []

    def lookup(src, dst, side):
        seen.append(side)
        return Decimal("1.3000") if side == "BUY" else Decimal("1.2000")

    b = convert_to_deposit(Decimal("1000"), margin_currency="EUR",
                           deposit_currency="USD", side="BUY", rate_lookup=lookup)
    s = convert_to_deposit(Decimal("1000"), margin_currency="EUR",
                           deposit_currency="USD", side="SELL", rate_lookup=lookup)
    check("Margin conversion, BUY at ASK", b, Decimal("1300.0000"),
          "Hedging.md #conversion: 'The Ask price is used for buy deals'")
    check("Margin conversion, SELL at BID", s, Decimal("1200.0000"),
          "Hedging.md #conversion: 'the Bid price is used for sell deals'")
    if seen != ["BUY", "SELL"]:
        FAILURES.append(f"conversion sides were {seen}, expected ['BUY', 'SELL']")


def margin_units_are_percent() -> None:
    """The M1 unit decision, re-checked here because M3 touches the same numbers."""
    print("\n[4] Margin thresholds are PERCENT (M1's decision, re-verified)")

    level = margin_level(Decimal("10000"), Decimal("25000"))
    check("equity 10k / margin 25k", level, Decimal("40"),
          "40%, not 0.4 - MT5 stores MarginCall as '50.00'")
    from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED

    unlimited = margin_level(Decimal("10000"), Decimal("0"))
    check("no margin in use -> sentinel", unlimited, MARGIN_LEVEL_UNLIMITED,
          "must not be 0, which reads as 'fully exhausted'")
    if unlimited < Decimal("1000"):
        FAILURES.append("an account with no positions reports a low margin level")


def stop_out_cycle() -> None:
    """A full stop-out on a group imported from the real server export."""
    print("\n[5] Stop-out cycle on the real demo\\Standard group")

    from core.domains.accounts.account import Account
    from core.domains.accounts.group import Group
    from core.domains.accounts.value_objects import MarginProfile
    from core.domains.common.value_objects import Money, Price, Volume
    from core.domains.oms.entities.position import Position
    from core.domains.oms.enums import PositionAction
    from core.domains.risk.engine import RiskEngine
    from core.domains.risk.models import RiskStatus

    # demo\Standard from Groups TCTrader-Live.json: MarginCall 10.00, MarginStopOut 1.00.
    group = Group(
        name="demo" + chr(92) + "Standard",
        currency="USD",
        margin=MarginProfile(
            margin_call_level=Decimal("10.00"),
            stop_out_level=Decimal("1.00"),
            leverage_default=100,
        ),
    )

    class Feed:
        def __init__(self, bid, ask):
            self.bid, self.ask = Decimal(bid), Decimal(ask)

        def get_bid(self, symbol):
            return self.bid

        def get_ask(self, symbol):
            return self.ask

    class Repo:
        def __init__(self, symbol):
            self.symbol = symbol

        def get_symbol(self, name):
            return self.symbol

    from core.domains.instruments.symbol import Symbol

    symbol = Symbol(
        name="EURUSD", base_currency="EUR", quote_currency="USD",
        margin_currency="EUR", contract_size=FX_CONTRACT, calc_mode=0,
    )

    account = Account(
        login="900001", group=group, currency="USD",
        balance=Money(Decimal("1100"), "USD"),
    )
    position = Position(
        position_id="P1", account_login="900001", symbol="EURUSD",
        action=PositionAction.BUY, volume=Volume(Decimal("1")),
        price_open=Price(Decimal("1.1000")), contract_size=FX_CONTRACT,
    )

    # Healthy: bid 1.1000, no PnL. margin = 1000 EUR * 1.1000 = 1100 USD.
    # equity 1100 / margin 1100 = 100%, above the 10% call level.
    engine = RiskEngine(symbol_repo=Repo(symbol), market_data_engine=Feed("1.1000", "1.1002"))
    snap = engine.calculate_margin_level(account, [position])
    print(f"    [....] at bid 1.1000: equity={cents(snap.equity)} margin={cents(snap.margin_used)} "
          f"level={cents(snap.margin_level)}% status={snap.status.name}")
    if snap.status is not RiskStatus.NORMAL:
        FAILURES.append(f"a level of {snap.margin_level}% should be NORMAL on a 10% call group")

    # Margin call: bid falls so equity drops below 10% of margin.
    engine = RiskEngine(symbol_repo=Repo(symbol), market_data_engine=Feed("1.0900", "1.0902"))
    snap = engine.calculate_margin_level(account, [position])
    print(f"    [....] at bid 1.0900: equity={cents(snap.equity)} margin={cents(snap.margin_used)} "
          f"level={cents(snap.margin_level)}% status={snap.status.name}")
    if not engine.detect_margin_call(account, snap):
        FAILURES.append(f"margin call not detected at level {snap.margin_level}% with a 10% threshold")
    else:
        print("    [PASS] margin call detected at the group's 10.00% threshold")

    # Stop out: equity falls below 1% of margin.
    engine = RiskEngine(symbol_repo=Repo(symbol), market_data_engine=Feed("1.0000", "1.0002"))
    snap = engine.calculate_margin_level(account, [position])
    print(f"    [....] at bid 1.0000: equity={cents(snap.equity)} margin={cents(snap.margin_used)} "
          f"level={cents(snap.margin_level)}% status={snap.status.name}")
    if not engine.detect_stop_out(account, snap):
        FAILURES.append(f"stop out not detected at level {snap.margin_level}% with a 1.00% threshold")
    else:
        print("    [PASS] stop out detected at the group's 1.00% threshold")

    selected = engine.select_positions_for_liquidation(account, [position])
    if len(selected) != 1:
        FAILURES.append(f"stop-out selected {len(selected)} positions, expected 1")
    else:
        print("    [PASS] the losing position is selected for liquidation")

    # A PROFITABLE account must select nothing. The old test asserted the opposite.
    healthy = Account(
        login="900002", group=group, currency="USD",
        balance=Money(Decimal("50000"), "USD"),
    )
    engine = RiskEngine(symbol_repo=Repo(symbol), market_data_engine=Feed("1.2000", "1.2002"))
    snap = engine.calculate_margin_level(healthy, [position])
    selected = engine.select_positions_for_liquidation(healthy, [position])
    print(f"    [....] profitable account: equity={cents(snap.equity)} "
          f"level={cents(snap.margin_level)}% selected={len(selected)}")
    if selected:
        FAILURES.append("a profitable account had positions selected for liquidation")
    else:
        print("    [PASS] a healthy account liquidates nothing")


def main() -> int:
    print("=== M3 proof: is the risk maths trustworthy? ===")
    print("Every expected value below is quoted from a source outside this codebase:")
    print("  - the audit's validation table (opencode_summery.md)")
    print("  - MT5's published worked examples (Platform-Setup.md)")
    print("  - the real server export's group thresholds (Groups TCTrader-Live.json)")

    audit_validation_rows()
    mt5_published_examples()
    bid_ask_asymmetry()
    margin_units_are_percent()
    stop_out_cycle()

    print()
    if FAILURES:
        print(f"=== M3 proof FAILED: {len(FAILURES)} check(s) ===")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("=== M3 proof PASSED ===")
    print("The four audit rows reproduce, MT5's own examples reproduce to the cent,")
    print("the spread is honoured in both directions, thresholds are PERCENT, and a")
    print("real imported group's stop-out cycle fires at its configured levels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
