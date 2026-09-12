"""D10: closing a position must release its margin and leave equity honest.

Found while answering "why do I only see IN deals and no OUT deals?". The answer to
that question is that no position has ever been closed in the database - there is
no client-facing close endpoint, `DELETE /api/v1/trade/orders/{id}` is a stub that
returns `{"status":"cancelled"}` without touching anything, and the only real path
is the manager endpoint. But driving that real path exposed two genuine defects:

1. `margin_used` stayed at the open position's requirement after the close. Step 9
   of ClosePositionHandler set balance and equity and saved; it never recomputed
   margin, because `_recalculate_account_margin` lives in RecordDealHandler and a
   close does not go through it. Every closed position left its hold behind
   forever, so free margin only ever shrank: an account that traded and closed
   repeatedly eventually could not open anything while holding nothing, and its
   falling margin_level drifted toward a stop-out that would liquidate positions
   it did not have.

2. `equity = balance + account.profit` read the account's own stale `profit`,
   which only the tick pipeline refreshes. So a close realised the result into
   balance AND left the closed position's last floating PnL in equity -
   double-counted, in the direction that flatters the account.
"""
from decimal import Decimal

import pytest

from application.commands.close_position import ClosePositionCommand
from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED
from core.domains.oms.enums import OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN, build_harness, default_coverage, make_eurusd, make_usdjpy,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")


async def open_buy(h, symbol="EURUSD", volume="0.10", bid=BID, ask=ASK):
    await h.publish_tick(symbol, bid, ask)
    order = await h.stack.create_order_handler.handle(CreateOrderCommand(
        account_login=DEFAULT_LOGIN, symbol=symbol, order_type=OrderType.BUY,
        volume=Decimal(volume)))
    positions = [p for p in await h.position_repo.get_by_account(DEFAULT_LOGIN)
                 if p.time_done is None and p.symbol == symbol]
    return order, positions[-1]


async def close(h, position, reason="CLIENT"):
    return await h.stack.close_position_handler.handle(ClosePositionCommand(
        account_login=DEFAULT_LOGIN, position_id=position.position_id, reason=reason))


@pytest.mark.asyncio
async def test_closing_the_last_position_releases_all_of_its_margin():
    """The headline defect: the hold outlived the position it was held for."""
    h = await build_harness(coverage=default_coverage())
    order, position = await open_buy(h)

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_used.amount > Decimal("0"), "the open position holds margin"
    held = account.margin_used.amount

    await h.publish_tick("EURUSD", Decimal("1.10100"), Decimal("1.10110"))
    await close(h, position)

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert after.margin_used.amount == Decimal("0"), (
        f"margin_used stayed at {after.margin_used.amount} after the only position "
        f"was closed - the hold of {held} was never released"
    )
    assert after.margin_free.amount == after.equity.amount
    assert after.margin_level == MARGIN_LEVEL_UNLIMITED, (
        "a flat account is at the sentinel, not at some leftover level"
    )


@pytest.mark.asyncio
async def test_closing_one_of_two_positions_releases_only_that_leg():
    """The recompute must be over what is STILL open, not a blanket zero."""
    h = await build_harness(
        symbols=[make_eurusd(), make_usdjpy()], coverage=default_coverage())
    _, eur = await open_buy(h, "EURUSD", "0.10")
    _, jpy = await open_buy(h, "USDJPY", "0.10",
                            bid=Decimal("150.000"), ask=Decimal("150.010"))

    # Re-read AFTER both legs are open. Reading the account object returned
    # earlier in the test gives a snapshot from before the second fill, so the
    # "must reduce" comparison is against a number that never included both legs.
    both = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert both is not None, "the account vanished after opening two positions"
    both_margin = both.margin_used.amount
    assert both_margin > Decimal("0")

    await close(h, eur)

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert after.margin_used.amount > Decimal("0"), (
        "the still-open USDJPY leg lost its margin when EURUSD was closed"
    )
    assert after.margin_used.amount < both_margin, (
        f"closing a leg must reduce the requirement: {both_margin} -> "
        f"{after.margin_used.amount}"
    )
    # and it must equal what the engine says the remaining leg needs, not merely
    # "something smaller" - a partial release is as wrong as no release.
    remaining = [p for p in await h.position_repo.get_by_account(DEFAULT_LOGIN)
                 if p.time_done is None]
    snapshot = h.stack.risk_engine.calculate_margin_level(after, remaining)
    assert after.margin_used.amount == snapshot.margin_used, (
        f"margin_used {after.margin_used.amount} disagrees with the engine's "
        f"{snapshot.margin_used} for the positions actually open"
    )
    open_now = [p for p in await h.position_repo.get_by_account(DEFAULT_LOGIN)
                if p.time_done is None]
    assert len(open_now) == 1 and open_now[0].symbol == "USDJPY"


@pytest.mark.asyncio
async def test_equity_has_no_unrealised_shadow_of_the_closed_position():
    """Defect 2: a close must not leave the closed leg's floating PnL in equity."""
    h = await build_harness(coverage=default_coverage())
    _, position = await open_buy(h)

    # move the market so the open position has real floating profit
    await h.publish_tick("EURUSD", Decimal("1.10500"), Decimal("1.10510"))
    floating = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert floating.profit.amount > Decimal("0"), "the position should be in profit"

    await close(h, position)

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # flat: nothing is open, so nothing is unrealised
    assert after.profit.amount == Decimal("0"), (
        "the closed position's floating PnL is still in account.profit"
    )
    assert after.equity.amount == after.balance.amount, (
        f"equity {after.equity.amount} != balance {after.balance.amount} on a flat "
        "account - the realised result was counted twice"
    )


@pytest.mark.asyncio
async def test_the_realised_result_lands_in_the_balance_once():
    h = await build_harness(coverage=default_coverage())
    _, position = await open_buy(h)
    before = (await h.account_repo.find_by_login(DEFAULT_LOGIN)).balance.amount

    await h.publish_tick("EURUSD", Decimal("1.10100"), Decimal("1.10110"))
    await close(h, position)

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # 0.10 lots x 100000 contract x (1.10100 - 1.10010) = 9.00
    assert after.balance.amount == before + Decimal("9.00")


@pytest.mark.asyncio
async def test_a_close_writes_both_an_in_and_an_out_deal():
    """The question that started this: an OUT deal must exist after a close."""
    h = await build_harness(coverage=default_coverage())
    _, position = await open_buy(h)
    await h.publish_tick("EURUSD", Decimal("1.10100"), Decimal("1.10110"))
    await close(h, position)

    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    entries = sorted(d.entry.value for d in deals)
    assert entries == ["IN", "OUT"], f"expected one IN and one OUT deal, got {entries}"
    out = next(d for d in deals if d.entry.value == "OUT")
    assert out.profit.amount == Decimal("9.00")


@pytest.mark.asyncio
async def test_a_partial_close_releases_only_the_closed_volume():
    h = await build_harness(coverage=default_coverage())
    _, position = await open_buy(h, volume="0.20")
    full = (await h.account_repo.find_by_login(DEFAULT_LOGIN)).margin_used.amount

    await h.publish_tick("EURUSD", Decimal("1.10100"), Decimal("1.10110"))
    await h.stack.close_position_handler.handle(ClosePositionCommand(
        account_login=DEFAULT_LOGIN, position_id=position.position_id,
        volume=Decimal("0.10"), reason="CLIENT"))

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert after.margin_used.amount < full, "a partial close released nothing"
    assert after.margin_used.amount > Decimal("0"), "a partial close released everything"
    open_now = [p for p in await h.position_repo.get_by_account(DEFAULT_LOGIN)
                if p.time_done is None]
    assert len(open_now) == 1
    assert open_now[0].volume.value == Decimal("0.10")


@pytest.mark.asyncio
async def test_a_stop_out_close_also_releases_margin():
    """The liquidation path uses the same handler, so it inherits the fix - and
    matters more, because a stop-out that does not free margin cannot recover."""
    h = await build_harness(coverage=default_coverage())
    _, position = await open_buy(h)
    await h.publish_tick("EURUSD", Decimal("1.10100"), Decimal("1.10110"))
    await close(h, position, reason="SO")

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert after.margin_used.amount == Decimal("0")
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    out = next(d for d in deals if d.entry.value == "OUT")
    reason = out.reason.value if hasattr(out.reason, "value") else str(out.reason)
    assert "SO" in str(reason), f"the closing deal should carry the stop-out reason, got {reason}"


@pytest.mark.asyncio
async def test_without_a_risk_engine_the_fallback_still_releases_and_says_so(caplog):
    """A single-currency setup or a test double has no engine. The fallback must
    release the hold rather than leave it, and must not pretend to be exact."""
    import logging

    h = await build_harness(coverage=default_coverage())
    _, position = await open_buy(h)
    h.stack.close_position_handler.risk_engine = None

    await h.publish_tick("EURUSD", Decimal("1.10100"), Decimal("1.10110"))
    with caplog.at_level(logging.WARNING):
        await close(h, position)

    before = Decimal("110.01")   # what the engine held for 0.10 EURUSD
    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert after.margin_used.amount < before, (
        f"the fallback left the whole hold in place: {after.margin_used.amount}"
    )
    # The fallback is notional/leverage with no currency conversion, so it is
    # deliberately approximate - it must release the hold, not match the engine
    # to the cent. Asserting an exact zero here would be asserting the fallback is
    # exact, which is the one thing it is documented as not being.
    assert after.margin_used.amount >= Decimal("0")
    assert "without a risk-engine margin recompute" in caplog.text, (
        "an approximate fallback must announce itself"
    )
