"""D6: one staleness limit, shared by ingestion and valuation, configurable.

The bug this pins: `MarketDataEngine._is_stale` and
`RiskEngine._verify_tick_freshness` each carried their own hard-coded `10.0`
literal. Neither was ever exercised, because every feed in the test estate stamps
`datetime.now()` - the mock feed and `m10_ws_simulator.py` - so ticks were always
~0s old. Against a real MetaTrader 5 terminal, where a tick carries the BROKER's
quote time, measured ages ran 0.4s-19.8s:

  * ingestion dropped 497 of 497 ticks, leaving the engine with no price at all
    while the socket stayed connected (the only evidence was a `logger.debug`);
  * valuation then raised `StaleQuoteError` and `GET /account/positions` returned
    500 on an account holding a live, margined position.

M7 had already made the PRICING guard configurable at 60s. These two now default
to the same number through one resolver, so the three guards cannot drift.
"""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from core.domains.market_data.engine import MarketDataEngine
from core.domains.market_data.models import Tick
from core.domains.market_data.quote_freshness import (
    DEFAULT_MAX_TICK_AGE_SECONDS,
    MARKET_DATA_MAX_TICK_AGE_ENV,
    resolve_max_tick_age_seconds,
)
from core.domains.risk.engine import MAX_QUOTE_AGE_SECONDS, RiskEngine, StaleQuoteError
from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

ENV = MARKET_DATA_MAX_TICK_AGE_ENV


def tick(age_seconds: float, symbol: str = "EURUSD") -> Tick:
    return Tick(
        symbol=symbol,
        bid=Decimal("1.15900"),
        ask=Decimal("1.15910"),
        spread=Decimal("0.00010"),
        timestamp=datetime.now(timezone.utc) - timedelta(seconds=age_seconds),
        source="TEST",
    )


# ------------------------------------------------------------- the resolver

def test_the_default_matches_the_pricing_guard_m7_chose():
    """60s, not 10s - and the same number in both engines."""
    assert DEFAULT_MAX_TICK_AGE_SECONDS == 60.0
    assert MAX_QUOTE_AGE_SECONDS == DEFAULT_MAX_TICK_AGE_SECONDS
    assert resolve_max_tick_age_seconds() == 60.0


def test_an_explicit_argument_beats_the_environment(monkeypatch):
    monkeypatch.setenv(ENV, "90")
    assert resolve_max_tick_age_seconds(25.0) == 25.0


def test_the_environment_overrides_the_default(monkeypatch):
    monkeypatch.setenv(ENV, "120")
    assert resolve_max_tick_age_seconds() == 120.0


def test_zero_disables_the_check(monkeypatch):
    monkeypatch.setenv(ENV, "0")
    assert resolve_max_tick_age_seconds() == 0.0


def test_a_malformed_value_falls_back_and_does_not_disable(monkeypatch, caplog):
    """Becoming 0 would silently switch the guard off - the dangerous direction."""
    monkeypatch.setenv(ENV, "not-a-number")
    with caplog.at_level(logging.WARNING):
        assert resolve_max_tick_age_seconds() == DEFAULT_MAX_TICK_AGE_SECONDS
    assert ENV in caplog.text


def test_a_negative_value_clamps_to_zero_not_to_negative(monkeypatch):
    monkeypatch.setenv(ENV, "-5")
    assert resolve_max_tick_age_seconds() == 0.0


# --------------------------------------------------------------- ingestion

@pytest.mark.asyncio
async def test_a_15_second_old_tick_is_now_stored():
    """The exact case that failed against the real terminal: 15s > old 10s limit."""
    eng = MarketDataEngine(event_bus=InProcessEventBus(), symbol_repo=None)
    await eng.process_tick(tick(15.0))
    assert "EURUSD" in eng.ticks, "a 15s-old tick must be ingested at the 60s default"


@pytest.mark.asyncio
async def test_a_tick_older_than_the_limit_is_still_refused():
    """Configurable does not mean absent - the guard still protects pricing."""
    eng = MarketDataEngine(event_bus=InProcessEventBus(), symbol_repo=None)
    await eng.process_tick(tick(90.0))
    assert eng.ticks == {}, "a 90s-old tick must be refused at the 60s default"


@pytest.mark.asyncio
async def test_zero_disables_ingestion_filtering():
    eng = MarketDataEngine(event_bus=InProcessEventBus(), symbol_repo=None,
                           max_tick_age_seconds=0)
    await eng.process_tick(tick(10_000.0))
    assert "EURUSD" in eng.ticks


@pytest.mark.asyncio
async def test_a_rejected_feed_is_reported_at_warning_not_debug(caplog):
    """The silence was half the bug: 497 drops and not one visible line."""
    eng = MarketDataEngine(event_bus=InProcessEventBus(), symbol_repo=None)
    with caplog.at_level(logging.WARNING):
        await eng.process_tick(tick(90.0))
    assert "stale" in caplog.text.lower()
    assert ENV in caplog.text, "the warning must name the knob that fixes it"


@pytest.mark.asyncio
async def test_the_warning_is_rate_limited(caplog):
    eng = MarketDataEngine(event_bus=InProcessEventBus(), symbol_repo=None)
    with caplog.at_level(logging.WARNING):
        for _ in range(50):
            await eng.process_tick(tick(90.0))
    warnings = [r for r in caplog.records if "stale" in r.getMessage().lower()]
    assert len(warnings) == 1, "the first drop warns; the rest must not flood the log"


# -------------------------------------------------------------- valuation

class _Feed:
    def __init__(self, tk):
        self._tk = tk

    def get_latest_tick(self, symbol):
        return self._tk


def _engine(max_age=None):
    kw = {} if max_age is None else {"max_quote_age_seconds": max_age}
    return RiskEngine(symbol_repo=None, market_data_engine=_Feed(tick(15.0)), **kw)


def test_valuation_accepts_a_15_second_old_quote_at_the_default():
    """The 500 on GET /account/positions, reproduced and fixed."""
    eng = _engine()
    assert eng.max_quote_age_seconds == 60.0
    assert eng._side_price("EURUSD", "bid") == Decimal("1.15900")


def test_valuation_still_refuses_a_quote_past_its_own_limit():
    eng = _engine(max_age=10.0)
    with pytest.raises(StaleQuoteError):
        eng._side_price("EURUSD", "bid")


def test_ingestion_and_valuation_agree_by_default():
    """The invariant D6 exists to protect: one knob, one number, two guards."""
    ing = MarketDataEngine(event_bus=InProcessEventBus(), symbol_repo=None)
    val = _engine()
    assert ing.max_tick_age_seconds == val.max_quote_age_seconds == 60.0
