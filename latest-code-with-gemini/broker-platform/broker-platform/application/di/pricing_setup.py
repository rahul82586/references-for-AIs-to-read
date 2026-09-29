"""Client quote provider: ConfigCache + market data engine -> priced quotes.

The matching engine asks this provider for the (bid, ask) a specific CLIENT
should trade at; the provider resolves the symbol's base spread settings and
the account's group overrides from the ConfigCache (synchronous, MT5-like hot
path) and transforms the latest raw tick through core.domains.pricing.

Stale-quote refusal: a fill priced off a tick older than
PRICING_MAX_TICK_AGE_SECONDS (default 60; 0 disables) raises the engine's
NoQuoteError, so the order is REJECTED with a reason instead of filling at a
price the market left behind — the Centroid "stale prices" rule, and the same
honesty as the A-Book stub: refuse rather than fake.

Accounts created after startup may not be in the ConfigCache yet; an unknown
account prices at the SYMBOL's settings (no group override) rather than
failing — a slightly un-marked-up fill is recoverable, a refused legitimate
order is not. The gap is logged at debug and closes when the cache learns the
account (ConfigCache invalidation events).
"""
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Optional, Tuple

from core.domains.pricing.engine import client_quote, resolve_spread_settings

logger = logging.getLogger(__name__)

DEFAULT_MAX_TICK_AGE_SECONDS = 60


def max_tick_age_from_env() -> int:
    raw = os.environ.get("PRICING_MAX_TICK_AGE_SECONDS", "").strip()
    if not raw:
        return DEFAULT_MAX_TICK_AGE_SECONDS
    try:
        return max(0, int(raw))
    except ValueError:
        logger.warning(
            "PRICING_MAX_TICK_AGE_SECONDS=%r is not an integer; using %d",
            raw, DEFAULT_MAX_TICK_AGE_SECONDS,
        )
        return DEFAULT_MAX_TICK_AGE_SECONDS


def build_client_quote_provider(
    *,
    config_cache: Any,
    market_data_engine: Any,
    max_tick_age_seconds: Optional[int] = None,
) -> Callable[[str, Any], Optional[Tuple[Decimal, Decimal]]]:
    """Return provider(symbol_name, account_login) -> (bid, ask) | None.

    None means "cannot price this" and the engine falls through to its own raw
    path (which raises its honest NoQuoteError when there is nothing there).
    A stale quote raises NoQuoteError directly so the rejection reason says
    STALE rather than NO QUOTE.
    """
    if max_tick_age_seconds is None:
        max_tick_age_seconds = max_tick_age_from_env()

    def provider(symbol_name: str, account_login: Any) -> Optional[Tuple[Decimal, Decimal]]:
        from infrastructure.engines.book_matching_engine import NoQuoteError

        getter = getattr(market_data_engine, "get_latest_tick", None)
        tick = getter(symbol_name) if getter is not None else None
        if tick is None:
            return None
        raw_bid = getattr(tick, "bid", None)
        raw_ask = getattr(tick, "ask", None)
        if raw_bid is None or raw_ask is None:
            return None

        timestamp = getattr(tick, "timestamp", None)
        if max_tick_age_seconds > 0 and timestamp is not None:
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            if age > max_tick_age_seconds:
                raise NoQuoteError(
                    f"quote for {symbol_name} is {age:.0f}s old (limit "
                    f"{max_tick_age_seconds}s): refusing to price a stale quote"
                )

        symbol_cfg = config_cache.get_symbol(symbol_name)
        group = None
        account = None
        try:
            account = config_cache.get_account(int(account_login))
        except (TypeError, ValueError):
            account = None
        if account is not None:
            # The attached group object is authoritative (both the SQL mapper
            # and the harness attach it). The cache indexes groups by their
            # uuid while account.group_id commonly holds the NAME, so the
            # cache lookup is only a fallback - relying on it alone silently
            # priced every order without group overrides.
            group = getattr(account, "group", None) or config_cache.get_group(account.group_id)
        elif account_login is not None:
            logger.debug(
                "account %s is not in the ConfigCache; pricing %s at symbol "
                "settings without group overrides", account_login, symbol_name,
            )

        settings = resolve_spread_settings(symbol_cfg, group)
        bid, ask = Decimal(str(raw_bid)), Decimal(str(raw_ask))
        if not settings.has_effect():
            return bid, ask  # raw pass-through, but still freshness-checked
        point = getattr(symbol_cfg, "tick_size", None) or Decimal("0.00001")
        return client_quote(bid, ask, point=Decimal(str(point)), settings=settings)

    return provider
