"""M6: netting position accounting — reachable, and it books its realised PnL.

Two defects, one hiding the other:

1. `_apply_deal_to_positions` dispatched on `account.group.execution.mode` — an
   attribute Group does not have. The hasattr guard yielded None and EVERY
   account silently ran the hedging branch. Netting was unreachable code, which
   is why defect 2 survived M4's audit.
2. The netting branch reduced or deleted positions WITHOUT booking the realised
   result to the balance: the closed volume — and the client's profit or loss
   with it — vanished, and the account kept trading with money it had already
   lost or earned (M4 debt #2, the same class as the liquidation defect #16).

Dispatch now follows the MT5 SDK (IMTConGroup::EnMarginMode): MarginMode.RETAIL
(0) and EXCHANGE_DISCOUNT are NETTING; RETAIL_HEDGED (2) is HEDGING; unknown
keeps the historical hedging default. Realised PnL is computed by
RiskEngine.realized_pnl -> margin.position_pnl: converted quote->deposit at the
profit-currency rate, the same single source of truth the margin loop uses.
"""
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.enums import MarginMode
from core.domains.execution.models import CoverageAccount
from core.domains.oms.enums import DealEntry, OrderState, OrderType, PositionAction
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_group,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
CONTRACT = Decimal("100000")


def coverage():
    return [
        CoverageAccount(
            account_id="DEFAULT_COVERAGE",
            name="Default Coverage",
            currency="USD",
            nop_limit=Decimal("100"),
        )
    ]


def netting_harness_kwargs():
    """A broker whose demo group uses MT5's NETTING accounting (MarginMode 0)."""
    group = make_group(margin_mode=MarginMode.RETAIL)
    return {"groups": [group], "accounts": [make_account(group=group)], "coverage": coverage()}


async def place(h, order_type, volume, symbol="EURUSD"):
    return await h.stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=DEFAULT_LOGIN, symbol=symbol, order_type=order_type, volume=volume
        )
    )


async def test_netting_opposite_deal_closes_flat_and_books_the_loss():
    """Buy then sell the same volume: no position remains and the spread loss
    is ON THE BALANCE — before M6 the position vanished and so did the money."""
    h = await build_harness(**netting_harness_kwargs())
    await h.publish_tick("EURUSD", BID, ASK)

    buy_order = await place(h, OrderType.BUY, Decimal("0.10"))
    sell_order = await place(h, OrderType.SELL, Decimal("0.10"))
    assert buy_order.state == OrderState.FILLED and sell_order.state == OrderState.FILLED

    # flat
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []

    # bought at the ask, sold at the bid: -0.00010 x 0.10 x 100000 = -1.00 USD
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000") - Decimal("1")
    assert account.equity.amount == account.balance.amount  # nothing open

    # and the OUT deal carries the realised result, the way an MT5 statement does
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert len(deals) == 2
    out_deal = deals[-1]
    assert out_deal.profit.amount == Decimal("-1")


async def test_netting_partial_close_books_only_the_closed_volume():
    h = await build_harness(**netting_harness_kwargs())
    await h.publish_tick("EURUSD", BID, ASK)

    await place(h, OrderType.BUY, Decimal("0.20"))
    await place(h, OrderType.SELL, Decimal("0.10"))

    remaining = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert len(remaining) == 1
    assert remaining[0].action == PositionAction.BUY
    assert remaining[0].volume.value == Decimal("0.10")
    assert remaining[0].price_open.value == ASK  # untouched average

    # only the closed 0.10 is realised: -1.00 USD
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000") - Decimal("1")


async def test_netting_reversal_realises_the_old_side_and_reopens_the_remainder():
    h = await build_harness(**netting_harness_kwargs())
    await h.publish_tick("EURUSD", BID, ASK)

    await place(h, OrderType.BUY, Decimal("0.10"))
    await place(h, OrderType.SELL, Decimal("0.30"))

    positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert len(positions) == 1
    flipped = positions[0]
    assert flipped.action == PositionAction.SELL
    assert flipped.volume.value == Decimal("0.20")
    assert flipped.price_open.value == BID  # remainder opens at the deal price

    # the closed 0.10 BUY realised -1.00; the new SELL leg is unrealised only
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000") - Decimal("1")


async def test_netting_cross_currency_books_converted_pnl_not_raw_quote_amounts():
    """USDJPY on a USD account: the realised 4,800 JPY must land as ~31.9 USD.

    Before M6 there was no booking at all; the legacy ClosePositionHandler maths
    (still used when no engine is wired) would have added the raw JPY amount to
    a USD balance — a 150x error. This pins the converted result through the
    same rate machinery the margin loop uses.
    """
    # spread=0 (floating): make_usdjpy carries a FIXED spread of 10 points, and
    # since M7 the matching engine honours it (client ask = bid + 10 points).
    # This test pins netting maths, not pricing - float the symbol so the fills
    # are the published ticks. Fixed-spread behaviour has its own M7 tests.
    from dataclasses import replace as _replace
    from tests.integration.trading_harness import make_usdjpy as _usdjpy

    kwargs = netting_harness_kwargs()
    kwargs["symbols"] = [_replace(_usdjpy(), spread=0)]
    h = await build_harness(**kwargs)

    await h.publish_tick("USDJPY", Decimal("150.00"), Decimal("150.02"))
    await place(h, OrderType.BUY, Decimal("0.10"), symbol="USDJPY")

    await h.publish_tick("USDJPY", Decimal("150.50"), Decimal("150.52"))
    await place(h, OrderType.SELL, Decimal("0.10"), symbol="USDJPY")

    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []

    realised_jpy = (Decimal("150.50") - Decimal("150.02")) * Decimal("0.10") * CONTRACT
    assert realised_jpy == Decimal("4800.00")
    rate = h.stack.risk_engine._rate_lookup("JPY", "USD", "PROFIT")
    expected_usd = realised_jpy * Decimal(str(rate))

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    booked = account.balance.amount - Decimal("10000")
    assert booked == pytest.approx(expected_usd, rel=Decimal("1e-12"))
    # the conversion actually happened: 4800 JPY is ~31.9 USD, nowhere near 4800
    assert booked < Decimal("100")


async def test_hedging_groups_are_unaffected_by_the_netting_fix():
    """The seeded retail default (MarginMode 2) still stacks independent positions."""
    h = await build_harness(coverage=coverage())  # make_group defaults RETAIL_HEDGED
    await h.publish_tick("EURUSD", BID, ASK)

    await place(h, OrderType.BUY, Decimal("0.10"))
    await place(h, OrderType.SELL, Decimal("0.10"))

    positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert len(positions) == 2  # hedging: two independent positions
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000")  # nothing realised yet
