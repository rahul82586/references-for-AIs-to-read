"""One answer to "how old may a quote be and still be usable?"

D6 found the same hard-coded 10.0 seconds written independently in two modules:

* `MarketDataEngine._is_stale`        - decide whether to STORE an incoming tick
* `RiskEngine._verify_tick_freshness` - decide whether to VALUE a position at a tick

Both were literals in the method body, neither was configurable, and they were only
ever exercised by feeds that stamp `datetime.now()` - the mock feed and
`m10_ws_simulator.py` - so their ticks were always ~0s old and neither limit ever
fired. Against a real MetaTrader 5 terminal, where a tick carries the BROKER's
quote time, measured ages ran 0.4s-19.8s. The ingestion limit silently discarded
497 of 497 ticks; the risk limit then made `GET /account/positions` raise
`StaleQuoteError` and return 500 on an account holding a live, margined position.

M7 had already made the *pricing* guard configurable at
`PRICING_MAX_TICK_AGE_SECONDS` (default 60). These two now default to the same
number, through this one function, so the three guards cannot drift apart again.

The three decisions are genuinely different and stay separately tunable:

    MARKET_DATA_MAX_TICK_AGE_SECONDS   store a tick? / value a position at it?
    PRICING_MAX_TICK_AGE_SECONDS       FILL an order at it?  (M7 - the strictest)

`0` disables either check, matching M7's convention.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_MAX_TICK_AGE_SECONDS",
    "MARKET_DATA_MAX_TICK_AGE_ENV",
    "resolve_max_tick_age_seconds",
]

#: Matches M7's PRICING_MAX_TICK_AGE_SECONDS default. It was 10.0 before D6.
DEFAULT_MAX_TICK_AGE_SECONDS = 60.0

MARKET_DATA_MAX_TICK_AGE_ENV = "MARKET_DATA_MAX_TICK_AGE_SECONDS"


def resolve_max_tick_age_seconds(explicit: Optional[float] = None) -> float:
    """The staleness limit in seconds. `0` disables the check.

    Precedence: an explicit argument (tests, and any caller that knows better)
    beats the environment, which beats the default.

    A malformed environment value warns and falls back to the default rather than
    raising at boot - and specifically rather than becoming 0, which would switch
    the guard off silently and let arbitrarily old quotes price real money.
    """
    if explicit is not None:
        try:
            return max(0.0, float(explicit))
        except (TypeError, ValueError):
            logger.warning(
                "max_tick_age_seconds=%r is not a number; using %s",
                explicit, DEFAULT_MAX_TICK_AGE_SECONDS,
            )
            return DEFAULT_MAX_TICK_AGE_SECONDS

    raw = (os.environ.get(MARKET_DATA_MAX_TICK_AGE_ENV) or "").strip()
    if not raw:
        return DEFAULT_MAX_TICK_AGE_SECONDS
    try:
        return max(0.0, float(raw))
    except ValueError:
        logger.warning(
            "%s=%r is not a number; using %s",
            MARKET_DATA_MAX_TICK_AGE_ENV, raw, DEFAULT_MAX_TICK_AGE_SECONDS,
        )
        return DEFAULT_MAX_TICK_AGE_SECONDS
