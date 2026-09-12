"""
Close Position Command Handler.

This handler closes an open position by:
1. Creating a closing order (opposite side)
2. Recording a deal with entry=OUT
3. Updating position volume to 0
4. Updating account balance with realized PnL
5. Emitting PositionClosed event
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from core.domains.accounts.account import Account
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.entities.deal import Deal
from core.domains.oms.entities.order import Order
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import (
    DealEntry, DealReason, OrderReason, OrderState, OrderType, PositionAction, DealType
)
from core.events.domain_events import PositionClosed
from core.ports.interfaces import (
    IAccountRepository,
    IDealRepository,
    IEventBus,
    IOrderRepository,
    IPositionRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class ClosePositionCommand:
    """Command to close an open position."""
    account_login: int
    position_id: str
    volume: Optional[Decimal] = None  # None = close full position
    price: Optional[Decimal] = None  # None = use current market price
    comment: str = ""
    #: "SL" / "TP" / "SO" when a server-side trigger closed the position (M9);
    #: empty means a client/dealer close. Flows onto the closing deal AND order
    #: reasons, so statements say why the position closed.
    reason: str = ""
    #: D14: an optional sink the handler fills with what THIS close did -
    #: `deal_id`, `price`, `realized_pnl`, `volume_closed`. The handler's contract
    #: is "return the Position", and a partial close leaves that position open and
    #: floating, so a caller cannot read the leg's own result off it: `profit` is
    #: the remainder's unrealised PnL and `deal_close` is only set by a full close.
    #: Callers that do not pass a sink are unaffected.
    result: Optional[Dict[str, Any]] = None


class ClosePositionHandler:
    """Handler for ClosePositionCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        position_repo: IPositionRepository,
        order_repo: IOrderRepository,
        deal_repo: IDealRepository,
        event_bus: IEventBus,
        risk_engine=None,
    ):
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.order_repo = order_repo
        self.deal_repo = deal_repo
        self.event_bus = event_bus
        # Optional since M6: with an engine, the realised result is converted
        # quote->deposit (a USDJPY close used to add a raw JPY amount to a USD
        # balance). Without one, the legacy same-currency maths is kept and a
        # warning is logged, because the alternative - refusing - would break
        # single-currency setups that never needed conversion.
        self.risk_engine = risk_engine

    async def _revalue_after_close(self, account: Any, closed_position: Any,
                                   close_price: Optional[Decimal] = None,
                                   closed_volume: Optional[Decimal] = None) -> None:
        """Recompute equity and margin from the positions that are STILL open. D10.

        One source of truth: the same MT5-accurate engine the fill path uses, over
        the same open-position walk. A fourth local formula here is how the three
        previous margin implementations diverged in the first place (see the header
        of core/domains/market_data/margin.py).

        Without a risk engine - a single-currency setup, or a test double - this
        falls back to subtracting the closed leg's own requirement, and logs that
        it did. A silent fallback that gets margin wrong is how this class of bug
        survives; the fallback is better than leaving the hold in place, but an
        operator should know which one ran.
        """
        currency = account.currency

        open_positions = []
        getter = getattr(self.position_repo, "get_by_account", None) or \
            getattr(self.position_repo, "get_positions_by_account", None)
        if getter is not None:
            try:
                rows = await getter(account.login)
                # Filter on the CURRENT state of each row, not on identity with the
                # position being closed. A PARTIAL close reduces the position's
                # volume and leaves it open (time_done stays None), so excluding it
                # by position_id would drop a leg that is still live and still needs
                # margin - the exact bug this recompute exists to prevent, on the
                # partial path. The repository hands back the mutated object for a
                # full close too (volume 0 / time_done set), so both filter out here.
                open_positions = []
                for p in (rows or []):
                    if getattr(p, "time_done", None) is not None:
                        continue
                    vol = getattr(getattr(p, "volume", None), "value", None)
                    if not vol or vol <= 0:
                        continue
                    open_positions.append(p)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "could not list open positions for account %s after a close: %s - "
                    "margin will be estimated from the closed leg alone", account.login, exc,
                )

        # --- equity: balance + credit + the unrealised PnL of what is STILL open.
        unrealized = Decimal("0")
        if self.risk_engine is not None and open_positions:
            for p in open_positions:
                try:
                    unrealized += self.risk_engine.calculate_position_pnl(account, p)
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "cannot value still-open position %s after a close: %s - equity "
                        "excludes it", getattr(p, "position_id", "?"), exc,
                    )
        account.profit = Money(unrealized, currency)
        account.equity = Money(
            account.balance.amount + account.credit.amount + unrealized, currency)

        # --- margin: recomputed over the still-open positions only.
        if self.risk_engine is not None:
            try:
                snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
                account.margin_used = Money(snapshot.margin_used, currency)
                account.margin_free = Money(
                    max(Decimal("0"), account.equity.amount - snapshot.margin_used), currency)
                account.recompute_margin_level()
                return
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "margin recompute failed for account %s after a close: %s - falling "
                    "back to subtracting the closed leg, which is approximate",
                    account.login, exc,
                )

        # Fallback: no engine, or the engine failed. Release the closed leg's own
        # requirement rather than leaving it held forever.
        logger.warning(
            "account %s was closed without a risk-engine margin recompute; releasing "
            "the closed leg's requirement approximately. Wire a risk_engine into "
            "ClosePositionHandler for exact figures.", account.login,
        )
        released = self._closed_leg_margin(
            account, closed_position, close_price, closed_volume)
        account.margin_used = Money(
            max(Decimal("0"), account.margin_used.amount - released), currency)
        account.margin_free = Money(
            max(Decimal("0"), account.equity.amount - account.margin_used.amount), currency)
        account.recompute_margin_level()

    @staticmethod
    def _closed_leg_margin(account: Any, position: Any,
                           close_price: Optional[Decimal] = None,
                           closed_volume: Optional[Decimal] = None) -> Decimal:
        """The closed leg's margin requirement, for the no-engine fallback.

        Deliberately simple and deliberately conservative: notional / leverage in
        the position's own currency, with no conversion. It is a fallback that must
        never make free margin WORSE than leaving the hold in place, and it is
        labelled approximate wherever it runs.

        Both the volume and the price are passed IN, because by the time this runs
        the caller has already reduced `position.volume` by the closed amount - on a
        full close it is 0, so reading the position would release nothing. And
        `price_current` is Optional (migration 002), so the price this close actually
        used is the only reliable one.
        """
        try:
            volume = Decimal(str(closed_volume)) if closed_volume else Decimal(
                str(getattr(getattr(position, "volume", None), "value", 0)))
            price = Decimal(str(close_price)) if close_price else Decimal(
                str(getattr(getattr(position, "price_open", None), "value", 0)))
            contract = Decimal(str(getattr(position, "contract_size", 0) or 0))
            if contract <= 0:
                contract = Decimal("1")
            leverage = Decimal(str(account.effective_leverage() or 100))
            if volume <= 0 or price <= 0 or leverage <= 0:
                return Decimal("0")
            return (volume * contract * price) / leverage
        except (ArithmeticError, ValueError, TypeError, AttributeError):
            return Decimal("0")

    async def handle(self, command: ClosePositionCommand) -> Position:
        """Execute the close position command."""
        # 1. Fetch position
        position = await self.position_repo.find_by_id(command.position_id)
        if not position:
            raise ValueError(f"Position {command.position_id} not found")

        if position.account_login != command.account_login:
            raise ValueError(f"Position does not belong to account {command.account_login}")

        if position.time_done is not None:
            raise ValueError(f"Position {command.position_id} is already closed")

        # 2. Determine close volume
        close_volume = command.volume if command.volume else position.volume.value
        if close_volume > position.volume.value:
            raise ValueError(f"Close volume {close_volume} exceeds position volume {position.volume.value}")

        # 3. Determine closing side (opposite of position)
        if position.action == PositionAction.BUY:
            close_side = "SELL"
            deal_type = DealType.SELL
        else:
            close_side = "BUY"
            deal_type = DealType.BUY

        # 4. Get current price (or use provided price)
        # In production, fetch from market data feed
        # D10: `price_current` is Optional and migration 002 made the column
        # nullable for exactly this reason - a fresh position has no current price
        # until the first tick reprices it, and a sentinel of 0 or 1 would be a lie
        # that some later calculation multiplies by. That migration's own docstring
        # names the AttributeError this line was still raising: dereferencing
        # `.value` on None. It fired on ANY close that did not pass an explicit
        # price, which is the normal case - the client asks to close "at market".
        #
        # The fallback order is deliberate. `price_open` is a real price this
        # position actually traded at, so closing at it books zero PnL: wrong, but
        # honest, and visibly wrong on the statement. Inventing the raw request
        # price or 0 would silently move money.
        if command.price:
            current_price = command.price
        else:
            _pc = getattr(position, "price_current", None)
            current_price = getattr(_pc, "value", _pc)
            if current_price is None:
                _po = getattr(position, "price_open", None)
                current_price = getattr(_po, "value", _po)
                logger.warning(
                    "position %s has no current price (no tick has repriced it since "
                    "it opened); closing at its open price %s, which books zero PnL. "
                    "Pass an explicit price, or let the feed revalue it first.",
                    position.position_id, current_price,
                )
            if current_price is None:
                raise ValueError(
                    f"position {position.position_id} has neither a current price nor "
                    f"an open price, so it cannot be closed without an explicit one"
                )

        # 5. Create closing order
        reason_name = (command.reason or "").upper()
        deal_reason = (
            DealReason[reason_name] if reason_name in DealReason.__members__ else DealReason.CLIENT
        )
        order_reason = (
            OrderReason[reason_name] if reason_name in OrderReason.__members__ else OrderReason.CLIENT
        )
        closing_order = Order(
            account_login=command.account_login,
            symbol=position.symbol,
            order_type=OrderType[close_side],
            volume_initial=Volume(close_volume),
            volume_current=Volume(close_volume),
            price_order=Price(current_price),
            state=OrderState.FILLED,
            reason=order_reason,
            comment=f"[CLOSE] {command.comment}".strip(),
        )
        await self.order_repo.save(closing_order)

        # 6. Calculate realized PnL
        account_for_pnl = await self.account_repo.find_by_login(command.account_login)
        if self.risk_engine is not None and account_for_pnl is not None:
            # Converted, side-correct, single source of truth (margin.position_pnl).
            realized_pnl = self.risk_engine.realized_pnl(
                account_for_pnl, position, current_price, close_volume
            )
            realized_pnl_money = Money(realized_pnl, account_for_pnl.currency)
        else:
            if self.risk_engine is None:
                logger.warning(
                    "ClosePositionHandler has no risk_engine: realised PnL is NOT "
                    "currency-converted (correct only when quote == account currency)"
                )
            if position.action == PositionAction.BUY:
                price_diff = current_price - position.price_open.value
            else:
                price_diff = position.price_open.value - current_price
            realized_pnl = price_diff * close_volume * position.contract_size
            realized_pnl_money = Money(realized_pnl, position.profit.currency)

        # 7. Create closing deal
        closing_deal = Deal(
            order_id=closing_order.ticket_id,
            position_id=position.position_id,
            account_login=command.account_login,
            symbol=position.symbol,
            deal_type=deal_type,
            entry=DealEntry.OUT,
            reason=deal_reason,
            volume=Volume(close_volume),
            price=Price(current_price),
            profit=realized_pnl_money,
            swap=position.swap,
            commission=position.commission,
            comment=closing_order.comment,
        )
        await self.deal_repo.save(closing_deal)

        # D14: report the leg, from the deal that was just booked rather than from
        # the position - which on a partial close is still open, still floating,
        # and still carrying whatever the last tick wrote into `profit`.
        if command.result is not None:
            command.result.update({
                "deal_id": closing_deal.deal_id,
                "price": current_price,
                "realized_pnl": realized_pnl,
                "volume_closed": close_volume,
            })

        # 8. Update position
        #
        # D12: a FULL close also stamps the close onto the position, because this
        # object is what every caller sees afterwards - the client route builds its
        # response from it, the manager OrderClose endpoint reports from it, and
        # liquidation_worker already reads `position.profit.amount` as the realised
        # figure. Without this the route could only read volume 0 and a
        # `price_current` no tick had set since the position opened, so a close that
        # had genuinely dealt answered `volume_closed 0E-8 / close_price 0 /
        # realized_pnl 0E-8`. `profit` becoming the realised result on a closed
        # position is also what MT5 reports: a position in history shows its result,
        # not its last floating estimate.
        #
        # A PARTIAL close deliberately leaves `profit` alone. The position is still
        # open and still floating, so writing a realised number into a floating
        # field would be the same lie pointing the other way; the next tick reprices
        # the remainder.
        position.volume = Volume(position.volume.value - close_volume)
        # `price_current` is the last price this position dealt at, on a partial
        # close as much as on a full one - it is a fact about the trade, not an
        # estimate of the remainder.
        position.price_current = Price(current_price)
        if position.volume.value == Decimal('0'):
            position.time_done = datetime.now(timezone.utc)
            position.deal_close = closing_deal.deal_id
            position.profit = Money(realized_pnl, position.profit.currency)
        await self.position_repo.save(position)

        # 9. Update account balance with realized PnL, then RECOMPUTE margin.
        #
        # D10: this step used to set balance and equity and save - it never
        # touched margin. RecordDealHandler._recalculate_account_margin is the
        # only code that walks the open positions, and a close does not go through
        # it, so every closed position left its margin requirement behind forever.
        # Free margin only ever shrank: an account that traded and closed
        # repeatedly eventually could not open anything while holding nothing, and
        # its falling margin_level drifted toward a stop-out that would liquidate
        # positions it did not have.
        #
        # Equity was also wrong: `balance + account.profit` reads the account's own
        # stale profit field, which only the tick pipeline refreshes. That carries
        # the CLOSED position's last floating PnL into equity permanently, so a
        # close realised the result into balance AND left its unrealised shadow in
        # equity - double-counted, in the direction that flatters the account.
        account = account_for_pnl
        if account:
            account.balance = Money(account.balance.amount + realized_pnl, account.currency)
            # close_volume is passed because step 8 has ALREADY reduced
            # position.volume by it - reading the position would give the remainder
            # (0 on a full close), and the fallback would release nothing.
            await self._revalue_after_close(
                account, position, close_price=current_price,
                closed_volume=close_volume,
            )
            await self.account_repo.save(account)

        # 10. Emit PositionClosed event
        event = PositionClosed(
            aggregate_id=position.position_id,
            payload={
                "position_id": position.position_id,
                "account_login": command.account_login,
                "symbol": position.symbol,
                "volume_closed": str(close_volume),
                "close_price": str(current_price),
                "realized_pnl": str(realized_pnl),
                "deal_id": closing_deal.deal_id,
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Position {position.position_id} closed: volume={close_volume}, pnl={realized_pnl}")

        return position