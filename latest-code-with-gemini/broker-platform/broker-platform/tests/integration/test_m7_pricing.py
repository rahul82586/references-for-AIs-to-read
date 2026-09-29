"""M7: client pricing through the REAL trading stack.

The unit tests pin the transform maths; these pin the wiring: an order placed
through CreateOrderHandler -> risk -> router -> BookMatchingEngine fills at the
GROUP'S price, not the raw feed price — and a stale quote refuses the fill
instead of trading on a price the market left behind.
"""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.value_objects import GroupSymbolOverride
from core.domains.execution.models import CoverageAccount
from core.domains.market_data.models import Tick
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_eurusd,
    make_group,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
POINT = Decimal("0.00001")


def coverage():
    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


def floating_eurusd():
    """EURUSD with Spread=0 (floating) so the feed's own spread passes through
    and only the group transform moves the client price."""
    return replace(make_eurusd(), spread=0, spread_balance=0)


def harness_kwargs(overrides=None, symbol=None):
    group = make_group()
    if overrides:
        group.symbol_overrides = list(overrides)
    return {
        "groups": [group],
        "symbols": [symbol or floating_eurusd()],
        "accounts": [make_account(group=group)],
        "coverage": coverage(),
    }


async def buy(h, volume="0.10"):
    return await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=OrderType.BUY, volume=Decimal(volume))
    )


async def sell(h, volume="0.10"):
    return await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=OrderType.SELL, volume=Decimal(volume))
    )


async def test_group_spread_diff_raises_the_buyers_price_only():
    """SpreadDiff=20, balance 0: the ask widens 20 points, the bid is untouched."""
    h = await build_harness(**harness_kwargs(
        overrides=[GroupSymbolOverride(symbol_pattern="*", spread_diff=20, spread_diff_balance=0)]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    filled = await buy(h)
    assert filled.state == OrderState.FILLED
    assert filled.price_order.value == ASK + 20 * POINT  # 1.10030, not the raw 1.10010

    h2 = await build_harness(**harness_kwargs(
        overrides=[GroupSymbolOverride(symbol_pattern="*", spread_diff=20, spread_diff_balance=0)]
    ))
    await h2.publish_tick("EURUSD", BID, ASK)
    sold = await sell(h2)
    assert sold.price_order.value == BID  # the seller still gets the raw bid


async def test_spread_diff_balance_splits_the_markup_across_both_sides():
    """Balance=20 of a 20-point diff: ALL of it lowers the bid, ask untouched."""
    h = await build_harness(**harness_kwargs(
        overrides=[GroupSymbolOverride(symbol_pattern="*", spread_diff=20, spread_diff_balance=20)]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    sold = await sell(h)
    assert sold.price_order.value == BID - 20 * POINT  # 1.09980

    h2 = await build_harness(**harness_kwargs(
        overrides=[GroupSymbolOverride(symbol_pattern="*", spread_diff=20, spread_diff_balance=20)]
    ))
    await h2.publish_tick("EURUSD", BID, ASK)
    filled = await buy(h2)
    assert filled.price_order.value == ASK  # (20-20)=0 added to the ask


async def test_symbol_fixed_spread_replaces_the_feed_spread():
    """Spread=30/Balance=10 with NO group override: the client spread is exactly
    30 points around the raw bid, whatever the feed's own spread was."""
    symbol = replace(make_eurusd(), spread=30, spread_balance=10)
    h = await build_harness(**harness_kwargs(symbol=symbol))
    await h.publish_tick("EURUSD", BID, ASK)

    filled = await buy(h)
    assert filled.price_order.value == BID - 10 * POINT + 30 * POINT  # 1.10020

    h2 = await build_harness(**harness_kwargs(symbol=symbol))
    await h2.publish_tick("EURUSD", BID, ASK)
    sold = await sell(h2)
    assert sold.price_order.value == BID - 10 * POINT  # 1.09990


async def test_no_settings_means_raw_fills_unchanged():
    """The default configuration (floating spread, no overrides, no symbol
    diff) must reproduce the pre-M7 fills EXACTLY - the whole existing e2e
    suite depends on this, and so does every broker that runs raw spreads."""
    h = await build_harness(**harness_kwargs())
    await h.publish_tick("EURUSD", BID, ASK)

    filled = await buy(h)
    assert filled.price_order.value == ASK


async def test_a_stale_quote_refuses_the_fill_instead_of_trading():
    """Centroid's stale-price rule: a quote older than the limit is not a price.

    Two layers exist: MarketDataEngine rejects OLD ticks at ingestion (its own
    10-second filtration), and the pricing provider rejects quotes that WERE
    fresh but aged past PRICING_MAX_TICK_AGE_SECONDS while the market went
    quiet. This pins the second layer: the order is REJECTED with the reason,
    and no fill is invented from the aged number.
    """
    h = await build_harness(**harness_kwargs())
    await h.publish_tick("EURUSD", BID, ASK)  # fresh: stored and published

    # age the STORED quote past the limit (the feed simply stopped talking)
    h.market_data_engine.ticks["EURUSD"] = Tick(
        symbol="EURUSD", bid=BID, ask=ASK, spread=ASK - BID,
        timestamp=datetime.now(timezone.utc) - timedelta(seconds=300),
        source="TEST",
    )

    # M8 sharpened WHERE the refusal happens: the risk price now comes through
    # the same client-quote provider as the fill, so the stale quote is refused
    # at pricing time - persisted REJECTED (audit trail) and raised as ValueError
    # (HTTP 400), the same contract as "no price at all".
    with pytest.raises(ValueError, match="stale"):
        await buy(h)

    rejected = [o for o in h.order_repo.orders.values() if o.state == OrderState.REJECTED]
    assert len(rejected) == 1
    assert "stale" in (rejected[0].comment or "").lower()
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []


async def test_resting_pending_survives_a_stale_quote_and_fills_on_a_fresh_one():
    """Staleness refuses FILLS; it must not delete resting orders. The pending
    stays on the book through the stale tick and activates on the fresh one —
    at the group's transformed price."""
    h = await build_harness(**harness_kwargs(
        overrides=[GroupSymbolOverride(symbol_pattern="*", spread_diff=20, spread_diff_balance=0)]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    # a BUY_LIMIT far below the market rests
    pending = await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=OrderType.BUY_LIMIT, volume=Decimal("0.10"),
                           price=Decimal("1.05000"))
    )
    assert pending.state == OrderState.PLACED
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []

    # a stale tick must not activate it (and must not kill it). The engine's
    # ingestion filtration drops it before the book ever sees it; the provider
    # layer would refuse it too if it arrived via a bus event.
    old = datetime.now(timezone.utc) - timedelta(seconds=300)
    await h.market_data_engine.process_tick(
        Tick(symbol="EURUSD", bid=Decimal("1.04000"), ask=Decimal("1.04010"),
             spread=POINT, timestamp=old, source="TEST")
    )
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []

    # a FRESH tick through the limit fills at min(client ask, limit)
    await h.publish_tick("EURUSD", Decimal("1.04000"), Decimal("1.04010"))
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert len(deals) == 1
    # client ask = 1.04010 + 20 points = 1.04030, limit 1.05000 -> the better
    # client ask wins, exactly the limit-or-better rule, now group-priced
    assert deals[0].price.value == Decimal("1.04030")


async def test_provider_prices_accounts_missing_from_the_cache_at_symbol_settings():
    """An account created after the cache loaded still trades (symbol-level
    settings), rather than being refused for a wiring gap."""
    from application.di.pricing_setup import build_client_quote_provider

    h = await build_harness(**harness_kwargs(symbol=replace(make_eurusd(), spread_diff=5)))
    await h.publish_tick("EURUSD", BID, ASK)

    provider = build_client_quote_provider(
        config_cache=h.config_cache, market_data_engine=h.market_data_engine,
        max_tick_age_seconds=60,
    )
    quote = provider("EURUSD", 424242)  # unknown login
    assert quote == (BID, ASK + 5 * POINT)  # symbol diff applied, no group in play
