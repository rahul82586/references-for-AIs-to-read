"""Swap (rollover) worker — charges overnight positions at the daily rollover.

M6: this module was rewritten from the pre-M3 vocabulary it was never run with
(`position.side`, `position.average_price`, `position.id`, a base `DomainEvent`
constructed with an `init=False` event_type — every line raised) and from a
swap model that did not match MT5. The maths now follows the MT5 Administrator
guide, Symbols → Symbol Settings → Swaps (the authority in the reference
corpus), per SwapMode:

  POINTS (1)             swap = rate × point_price, where
                         point_price = volume × contract_size × point, in the
                         PROFIT currency, converted to the deposit currency at
                         the current rate. (Guide's own example: Buy 5.00
                         USDTRY, contract 100 000 → 5 × 100 000 × 0.00001 = 5
                         TRY → × 0.2274587 = 1.14 USD → × (−11.35) = −12.94.)
  SYMBOL_CURRENCY (2)    swap = rate × volume, charged in the BASE currency
  MARGIN_CURRENCY (3)    ... in the margin currency
  GROUP_CURRENCY (4)     ... in the deposit currency (no conversion)
  PROFIT_CURRENCY (9)    ... in the profit currency
                         Money modes convert to the deposit currency at the
                         rate UNFAVOURABLE to the trader (guide: a positive
                         swap sells the swap currency, a negative one buys).
  INTEREST_CURRENT (5)   annual %: (cost_of_1_lot × volume × rate / 100) /
  INTEREST_OPEN (6)      days_in_year (SwapYearDay, default 360/365). Cost of
                         1 lot is the contract size in the BASE currency for
                         Forex, contract × price for CFD-family modes; CURRENT
                         uses the live price, OPEN the position's open price.
  DISABLED (0)           nothing is charged.

Day multipliers (guide: "specify 1 to charge the regular amount, 3 for triple
swap or 0 to cancel"; "by default swap is not calculated on Saturday and
Sunday"): weekday = 1, the symbol's Swap3Day = 3, weekend = 0. MT5's day index
is 0=Sunday — wire-verified on the reference export (EURUSD Swap3Day=5 with
SwapRateFriday=3.0). Group-level overrides (GroupSymbolOverride.swap_long /
swap_short) take precedence over the symbol's rates, and a group's
SwapConfiguration.enable_swaps=False disables charging for the whole group.

The charge itself goes through the LedgerEngine: an immutable SWAP
BalanceOperation row AND the balance movement in one call. The position's
`swap` field accumulates in the deposit currency for statements.

Documented gaps (deliberate, not silent):
  * The per-day SwapRate{Sunday..Saturday} multiplier TABLE is not modelled
    (the seven wire fields quarantine losslessly); the swap_3day/weekend rule
    reproduces the reference server's actual curve but a custom curve needs the
    table.
  * Holiday adjustment ("day before a holiday doubles, holiday itself zero")
    is not applied.
  * REOPEN_* modes are not implemented; they log once and charge nothing.
  * Server-level swap control (trade server Config) has no equivalent yet.
"""
import asyncio
import inspect
import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Optional

from core.domains.common.value_objects import Money
from core.domains.instruments.enums import CalculationMode, SwapMode
from core.domains.ledger.engine import LedgerEngine
from core.domains.ledger.models import BalanceOperationType
from core.domains.market_data.feed_access import await_tick, tick_bid, tick_ask
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
from core.domains.risk.engine import RiskEngine
from core.events.domain_events import SwapApplied
from core.ports.interfaces import (
    IAccountRepository,
    IEventBus,
    IPositionRepository,
    ISymbolRepository,
)

logger = logging.getLogger(__name__)

_QUANT = Decimal("0.00000001")


class SwapWorker:
    """Charges swaps once per day at the broker's rollover hour (UTC)."""

    def __init__(
        self,
        ledger_engine: LedgerEngine,
        position_repo: IPositionRepository,
        account_repo: IAccountRepository,
        symbol_repo: ISymbolRepository,
        event_bus: IEventBus,
        market_data_engine: Optional[Any] = None,
        rollover_hour_utc: int = 22,  # 5 PM New York, MT5's common default
    ):
        self.ledger_engine = ledger_engine
        self.position_repo = position_repo
        self.account_repo = account_repo
        self.symbol_repo = symbol_repo
        self.event_bus = event_bus
        self.market_data_engine = market_data_engine
        self.rollover_hour_utc = rollover_hour_utc
        self._running = False
        # conversion uses rates only, never symbols: RiskEngine's symbol lookup
        # is synchronous (ConfigCache-shaped) and this worker holds async repos.
        self._conversion = (
            RiskEngine(symbol_repo=None, market_data_engine=market_data_engine)
            if market_data_engine is not None
            else None
        )
        self._warned_modes: set = set()

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Wait for the rollover hour, charge once per UTC date."""
        logger.info("SwapWorker started, rollover at %02d:00 UTC", self.rollover_hour_utc)
        self._running = True
        last_processed = None
        while self._running:
            now = datetime.now(timezone.utc)
            if now.hour == self.rollover_hour_utc and last_processed != now.date():
                try:
                    await self.process_rollover(now)
                except Exception:  # noqa: BLE001 - the loop must survive a bad night
                    logger.exception("swap rollover failed for %s", now.date())
                last_processed = now.date()
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(60)

    async def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------
    # Rollover
    # ------------------------------------------------------------------

    async def process_rollover(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        """Charge every open position for one rollover. Public for tests/ops."""
        now = now or datetime.now(timezone.utc)
        positions = await self._open_positions()
        charged = 0
        skipped = 0
        total = Decimal("0")
        for position in positions:
            try:
                amount = await self._apply_swap_for_position(position, now)
            except Exception:  # noqa: BLE001 - one bad position must not stop the night
                logger.exception(
                    "swap failed for position %s", getattr(position, "position_id", "?")
                )
                skipped += 1
                continue
            if amount is None:
                skipped += 1
            else:
                charged += 1
                total += amount
        report = {"date": str(now.date()), "charged": charged, "skipped": skipped, "total": str(total)}
        logger.info("swap rollover %s: %s", now.date(), report)
        return report

    async def _open_positions(self):
        repo = self.position_repo
        for name in ("get_open_positions", "get_positions_by_account"):
            getter = getattr(repo, name, None)
            if getter is None:
                continue
            if name == "get_open_positions":
                result = getter()
                if inspect.isawaitable(result):
                    result = await result
                return result
        return []

    # ------------------------------------------------------------------
    # One position
    # ------------------------------------------------------------------

    def _day_multiplier(self, symbol: Any, now: datetime) -> Decimal:
        """1 on weekdays, 3 on the symbol's triple day, 0 on weekends.

        MT5 day index is 0=Sunday (wire-verified: EURUSD Swap3Day=5 pairs with
        SwapRateFriday=3.0). Python's weekday() is Monday-first.
        """
        mt5_day = (now.weekday() + 1) % 7  # Sun=0 .. Sat=6
        if mt5_day in (0, 6):
            return Decimal("0")
        triple = getattr(symbol, "swap_3day", None)
        if triple is not None and int(triple) == mt5_day:
            return Decimal("3")
        return Decimal("1")

    async def _symbol_for(self, name: str) -> Optional[Any]:
        getter = getattr(self.symbol_repo, "get_symbol", None)
        if getter is not None:
            result = getter(name)
            if inspect.isawaitable(result):
                result = await result
            if result is not None:
                return result
        finder = getattr(self.symbol_repo, "find_by_name", None)
        if finder is not None:
            result = finder(name)
            if inspect.isawaitable(result):
                result = await result
            return result
        return None

    def _group_override(self, account: Any, symbol_name: str):
        group = getattr(account, "group", None)
        for override in getattr(group, "symbol_overrides", None) or []:
            pattern = getattr(override, "symbol_pattern", "") or ""
            if pattern == symbol_name or (pattern.endswith("*") and symbol_name.startswith(pattern[:-1])):
                return override
        return None

    async def _apply_swap_for_position(self, position: Position, now: datetime) -> Optional[Decimal]:
        account = await self.account_repo.find_by_login(position.account_login)
        if account is None:
            logger.warning("account %s not found for swap on %s", position.account_login, position.position_id)
            return None

        group = getattr(account, "group", None)
        swap_profile = getattr(group, "swaps", None)
        if swap_profile is not None and not getattr(swap_profile, "enable_swaps", True):
            return None

        symbol = await self._symbol_for(position.symbol)
        if symbol is None:
            logger.warning("symbol %s not configured; no swap charged for %s", position.symbol, position.position_id)
            return None

        multiplier = self._day_multiplier(symbol, now)
        if multiplier == 0:
            return None

        mode = getattr(symbol, "swap_mode", SwapMode.DISABLED)
        if isinstance(mode, str):  # tolerate a raw wire int/str from odd producers
            try:
                mode = SwapMode(int(mode))
            except ValueError:
                mode = SwapMode.DISABLED
        if mode == SwapMode.DISABLED:
            return None

        action = position.action if isinstance(position.action, PositionAction) else PositionAction(str(position.action))
        override = self._group_override(account, position.symbol)
        long_rate = symbol.swap_long if override is None or override.swap_long is None else override.swap_long
        short_rate = symbol.swap_short if override is None or override.swap_short is None else override.swap_short
        rate = Decimal(str(long_rate if action == PositionAction.BUY else short_rate))
        if rate == 0:
            return None

        volume = position.volume.value
        days_in_year = Decimal(str(getattr(symbol, "swap_year_days", 0) or 365))

        amount: Optional[Decimal] = None  # in the account (deposit) currency
        if mode == SwapMode.POINTS:
            point_price = volume * symbol.contract_size * symbol.tick_size  # profit ccy
            amount = self._to_deposit(point_price, symbol.quote_currency, account, side="PROFIT") * rate
        elif mode in (SwapMode.SYMBOL_CURRENCY, SwapMode.MARGIN_CURRENCY,
                      SwapMode.GROUP_CURRENCY, SwapMode.PROFIT_CURRENCY):
            currency = {
                SwapMode.SYMBOL_CURRENCY: symbol.base_currency,
                SwapMode.MARGIN_CURRENCY: getattr(symbol, "margin_currency", "") or symbol.base_currency,
                SwapMode.GROUP_CURRENCY: account.currency,
                SwapMode.PROFIT_CURRENCY: symbol.quote_currency,
            }[mode]
            amount = self._to_deposit(
                rate * volume, currency, account, side=None  # unfavourable side chosen inside
            )
        elif mode in (SwapMode.INTEREST_CURRENT, SwapMode.INTEREST_OPEN):
            cost_one_lot = await self._cost_of_one_lot(symbol, position, mode)
            if cost_one_lot is None:
                logger.warning(
                    "no price for %s; INTEREST swap skipped for %s (refusing to guess)",
                    symbol.name, position.position_id,
                )
                return None
            amount_base = cost_one_lot * volume * rate / Decimal("100") / days_in_year
            amount = self._to_deposit(amount_base, symbol.base_currency, account, side=None)
        else:
            if mode not in self._warned_modes:
                self._warned_modes.add(mode)
                logger.warning("swap mode %s is not implemented; charging nothing (loudly, once)", mode)
            return None

        amount = (amount * multiplier).quantize(_QUANT, rounding=ROUND_HALF_UP)
        if amount == 0:
            return None

        money = Money(amount, account.currency)
        await self.ledger_engine.record_operation(
            account_login=position.account_login,
            operation_type=BalanceOperationType.SWAP,
            amount=money,
            reference_id=position.position_id,
            comment=f"Swap {position.symbol} {now:%a} x{multiplier}",
        )
        position.swap = Money(position.swap.amount + amount, account.currency)
        await self.position_repo.save(position)
        await self.event_bus.publish(
            SwapApplied(
                aggregate_id=position.position_id,
                payload={
                    "position_id": position.position_id,
                    "account_login": str(position.account_login),
                    "symbol": position.symbol,
                    "swap_amount": str(amount),
                    "currency": account.currency,
                    "multiplier": str(multiplier),
                    "mode": str(getattr(mode, "name", mode)),
                },
            )
        )
        logger.info(
            "swap charged: %s %s x%s = %s %s",
            position.symbol, rate, multiplier, amount, account.currency,
        )
        return amount

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def _to_deposit(self, amount: Decimal, currency: str, account: Any, side: Optional[str]) -> Decimal:
        """Convert `amount` from `currency` into the account's deposit currency.

        side="PROFIT" uses the PnL conversion rate (points mode, per the guide:
        "converting at the current rate"). side=None selects the rate
        UNFAVOURABLE to the trader, per the money-mode rule: a positive swap
        sells the swap currency, a negative one buys it.
        """
        if not currency or currency == account.currency:
            return amount
        if self._conversion is None:
            raise RuntimeError(
                f"swap needs a {currency}->{account.currency} conversion but the worker "
                "has no market data engine; refusing to charge an unconverted amount"
            )
        if side is None:
            side = "SELL" if amount >= 0 else "BUY"
        rate = self._conversion.get_conversion_rate(currency, account.currency, side=side)
        if rate is None or Decimal(str(rate)) <= 0:
            raise RuntimeError(f"no usable rate for swap conversion {currency}->{account.currency}")
        return amount * Decimal(str(rate))

    async def _cost_of_one_lot(self, symbol: Any, position: Position, mode: SwapMode) -> Optional[Decimal]:
        """Cost of one lot in the BASE currency (guide, 'Calculation in percentage').

        Forex-family: the contract size itself (constant through time).
        CFD-family: contract size x price. Futures would additionally scale by
        tick_value/tick_size; not exercised by any configured symbol yet.
        """
        calc = getattr(symbol, "calc_mode", CalculationMode.FOREX)
        calc_name = getattr(calc, "name", str(calc))
        if calc_name in ("FOREX", "FOREX_NO_LEVERAGE"):
            return symbol.contract_size

        if mode == SwapMode.INTEREST_OPEN:
            return symbol.contract_size * position.price_open.value

        tick = await await_tick(self.market_data_engine, position.symbol)
        if tick is None:
            return None
        bid, ask = tick_bid(tick), tick_ask(tick)
        if bid is None or ask is None:
            return None
        price = bid if position.action == PositionAction.BUY else ask
        return symbol.contract_size * Decimal(str(price))
