import logging
from decimal import Decimal
from typing import Any, List, Optional
from datetime import datetime, timezone

from .models import MarginSnapshot, RiskStatus
from ..accounts.models import Account
from ..oms.entities.position import Position
from ...ports.interfaces import ISymbolRepository, IMarketDataFeed

logger = logging.getLogger(__name__)

MAX_QUOTE_AGE_SECONDS = 10.0


class StaleQuoteError(ValueError):
    """Raised when a market data quote is older than allowed threshold."""
    pass


class CurrencyConversionError(Exception):
    """Raised when an exchange rate for converting quote_currency to account_currency is missing."""
    pass


class RiskEngine:
    """
    Pure domain logic for risk calculations.

    Architectural Purpose:
    Encapsulates all margin and stop-out logic. Uses MarketDataEngine or IMarketDataFeed
    for current market price lookup.

    MT5 Compliance:
    - Margin Level = (Equity / Margin Used) × 100
    - Stop Out: Closes worst-loss positions first until margin recovers
    """

    def __init__(self, symbol_repo: Optional[ISymbolRepository] = None, market_data_engine: Optional[Any] = None):
        self.symbol_repo = symbol_repo
        self.market_data_engine = market_data_engine

    def get_conversion_rate(
        self,
        quote_currency: str,
        account_currency: str,
        market_feed: Optional[Any] = None
    ) -> Decimal:
        """
        Retrieves exchange rate to convert amounts in quote_currency to account_currency.
        Raises CurrencyConversionError if rate is missing.
        """
        if not quote_currency or not account_currency or quote_currency == account_currency:
            return Decimal('1.0')

        feed = market_feed or self.market_data_engine
        if not feed:
            raise CurrencyConversionError(
                f"Missing exchange rate for {quote_currency} -> {account_currency}: Market feed unavailable"
            )

        # 1. Try direct pair e.g. JPYUSD
        direct_symbol = f"{quote_currency}{account_currency}"
        try:
            if hasattr(feed, 'get_latest_tick'):
                tick = feed.get_latest_tick(direct_symbol)
                if tick:
                    rate = Decimal(str(tick['bid'] if isinstance(tick, dict) and 'bid' in tick else getattr(tick, 'bid', 0)))
                    if rate > Decimal('0'):
                        return rate
            elif hasattr(feed, 'get_bid'):
                bid = feed.get_bid(direct_symbol)
                if bid:
                    return Decimal(str(bid))
        except Exception:
            pass

        # 2. Try inverse pair e.g. USDJPY
        inverse_symbol = f"{account_currency}{quote_currency}"
        try:
            if hasattr(feed, 'get_latest_tick'):
                tick = feed.get_latest_tick(inverse_symbol)
                if tick:
                    ask_price = Decimal(str(tick['ask'] if isinstance(tick, dict) and 'ask' in tick else getattr(tick, 'ask', 0)))
                    if ask_price > Decimal('0'):
                        return Decimal('1.0') / ask_price
            elif hasattr(feed, 'get_ask'):
                ask = feed.get_ask(inverse_symbol)
                if ask:
                    return Decimal('1.0') / Decimal(str(ask))
        except Exception:
            pass

        raise CurrencyConversionError(
            f"Missing exchange rate for {quote_currency} -> {account_currency}"
        )

    def _verify_tick_freshness(self, symbol: str, tick: Any) -> None:
        """Ensures tick data is non-null and not older than MAX_QUOTE_AGE_SECONDS."""
        if tick is None:
            raise ValueError(f"No market tick available for symbol {symbol}")
        
        tick_ts = getattr(tick, 'timestamp', None) if not isinstance(tick, dict) else tick.get('timestamp')
        if tick_ts is None:
            return

        now = datetime.now(timezone.utc)
        if tick_ts.tzinfo is None:
            tick_ts = tick_ts.replace(tzinfo=timezone.utc)

        age = (now - tick_ts).total_seconds()
        if age > MAX_QUOTE_AGE_SECONDS:
            raise StaleQuoteError(
                f"Quote for symbol {symbol} is stale ({age:.1f}s > {MAX_QUOTE_AGE_SECONDS}s threshold)"
            )

    def _get_bid(self, symbol: str) -> Decimal:
        """Helper to resolve bid price from MarketDataEngine or legacy feed."""
        if hasattr(self.market_data_engine, 'get_latest_tick'):
            tick = self.market_data_engine.get_latest_tick(symbol)
            if tick:
                self._verify_tick_freshness(symbol, tick)
                return Decimal(str(tick['bid'] if isinstance(tick, dict) else tick.bid))
        if hasattr(self.market_data_engine, 'get_bid'):
            return Decimal(str(self.market_data_engine.get_bid(symbol)))
        raise ValueError(f"No market data available for symbol {symbol}")

    def _get_ask(self, symbol: str) -> Decimal:
        """Helper to resolve ask price from MarketDataEngine or legacy feed."""
        if hasattr(self.market_data_engine, 'get_latest_tick'):
            tick = self.market_data_engine.get_latest_tick(symbol)
            if tick:
                self._verify_tick_freshness(symbol, tick)
                return Decimal(str(tick['ask'] if isinstance(tick, dict) else tick.ask))
        if hasattr(self.market_data_engine, 'get_ask'):
            return Decimal(str(self.market_data_engine.get_ask(symbol)))
    def calculate_margin_level(self, account: Account, positions: List[Position]) -> MarginSnapshot:
        """
        Calculate real-time margin level for an account (Layer 1: Fast local RAM estimate).
        Formula: MarginLevel = (Equity / MarginUsed) * 100
        """
        unrealized_pnl = Decimal('0')
        margin_used = Decimal('0')

        effective_leverage = Decimal(str(account.leverage if account.leverage and account.leverage > 0 else (account.group.leverage_default if account.group else 100)))
        if effective_leverage <= Decimal('0'):
            effective_leverage = Decimal('1.0')

        for position in positions:
            try:
                symbol_info = self.symbol_repo.get_symbol(position.symbol)
                contract_size = Decimal(str(getattr(symbol_info, 'contract_size', 100000)))

                # Get current market price based on position side
                if position.side.name == "BUY":
                    current_price = self._get_bid(position.symbol)
                    pnl_per_unit = current_price - position.average_price.value
                else:  # SELL
                    current_price = self._get_ask(position.symbol)
                    pnl_per_unit = position.average_price.value - current_price

                # Position PnL = price_diff * volume * contract_size
                position_pnl = pnl_per_unit * position.volume.value * contract_size
                unrealized_pnl += position_pnl

                # Position Margin = (price * volume * contract_size) / leverage
                margin_for_position = (current_price * position.volume.value * contract_size) / effective_leverage
                margin_used += margin_for_position

            except Exception as e:
                logger.error(f"Error calculating margin for position {position.id} on account {getattr(account, 'login', account.id)}: {e}", exc_info=True)
                has_calculation_error = True

        equity = account.balance.amount + unrealized_pnl
        margin_free = equity - margin_used

        # Calculate margin level with safe division
        if margin_used <= Decimal('0'):
            margin_level = Decimal('999999')
            status = RiskStatus.BLOCKED if has_calculation_error else RiskStatus.NORMAL
        else:
            margin_level = (equity / margin_used) * Decimal('100')

            # Determine risk status based on Group rules
            margin_call_level = Decimal(str(account.group.margin_call_level if account.group and hasattr(account.group, 'margin_call_level') else '0.8'))
            stop_out_level = Decimal(str(account.group.stop_out_level if account.group and hasattr(account.group, 'stop_out_level') else '0.5'))

            if has_calculation_error:
                status = RiskStatus.BLOCKED
            elif margin_level < stop_out_level:
                status = RiskStatus.STOPPED_OUT
            elif margin_level < margin_call_level:
                status = RiskStatus.MARGIN_CALL
            else:
                status = RiskStatus.NORMAL

        login_str = str(account.login if hasattr(account, 'login') else account.id)

        return MarginSnapshot(
            account_login=login_str,
            balance=account.balance.amount,
            equity=equity,
            margin_used=margin_used,
            margin_free=margin_free,
            margin_level=margin_level,
            status=status
        )

    def detect_margin_call(self, account: Account, snapshot: MarginSnapshot) -> bool:
        """Check if account has breached margin call threshold."""
        if not account.group:
            return False
        margin_call_level = Decimal(str(account.group.margin_call_level))
        return snapshot.margin_level < margin_call_level
    def detect_stop_out(self, account: Account, snapshot: MarginSnapshot) -> bool:
        """Check if account has breached stop-out threshold."""
        if not account.group:
            return False
        stop_out_level = Decimal(str(account.group.stop_out_level))
        return snapshot.margin_level < stop_out_level

    def select_positions_for_liquidation(
        self,
        account: Account,
        positions: List[Position],
        symbol_repo: Optional[ISymbolRepository] = None,
        market_feed: Optional[IMarketDataFeed] = None
    ) -> List[Position]:
        """
        Select positions to close during Stop Out.

        MT5 behavior: Close worst-loss positions first until margin level recovers.
        """
        active_symbol_repo = symbol_repo or self.symbol_repo
        active_feed = market_feed or self.market_data_engine
        positions_with_pnl = []

        for position in positions:
            try:
                symbol_info = active_symbol_repo.find_by_name(position.symbol) if (active_symbol_repo and hasattr(active_symbol_repo, 'find_by_name')) else (active_symbol_repo.get_symbol(position.symbol) if active_symbol_repo else None)
                contract_size = Decimal(str(getattr(symbol_info, 'contract_size', 100000)))

                quote_curr = getattr(symbol_info, 'quote_currency', 'USD') if symbol_info else 'USD'
                conv_rate = self.get_conversion_rate(quote_curr, account.currency, market_feed=active_feed)

                if position.side.name == "BUY":
                    if hasattr(active_feed, 'get_latest_tick'):
                        t = active_feed.get_latest_tick(position.symbol)
                        self._verify_tick_freshness(position.symbol, t)
                        current_price = Decimal(str(t['bid'] if isinstance(t, dict) and 'bid' in t else getattr(t, 'bid', 0)))
                    else:
                        current_price = Decimal(str(active_feed.get_bid(position.symbol)))
                    raw_pnl = (current_price - position.average_price.value) * position.volume.value * contract_size
                else:
                    if hasattr(active_feed, 'get_latest_tick'):
                        t = active_feed.get_latest_tick(position.symbol)
                        self._verify_tick_freshness(position.symbol, t)
                        current_price = Decimal(str(t['ask'] if isinstance(t, dict) and 'ask' in t else getattr(t, 'ask', 0)))
                    else:
                        current_price = Decimal(str(active_feed.get_ask(position.symbol)))
                    raw_pnl = (position.average_price.value - current_price) * position.volume.value * contract_size

                pnl = raw_pnl * conv_rate
                positions_with_pnl.append((position, pnl))
            except CurrencyConversionError:
                raise
            except Exception as e:
                logger.error(f"Error calculating liquidation PnL for position {position.id}: {e}")
                continue

        # Sort by PnL ascending (worst losses first)
        positions_with_pnl.sort(key=lambda x: x[1])

        return [pos for pos, pnl in positions_with_pnl]
