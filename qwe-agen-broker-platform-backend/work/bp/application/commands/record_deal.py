"""
Record Deal Command Handler.
Triggered when a match occurs (Internal Engine or External LP Fill).
Updates Positions, Balances, and publishes Deal events.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional
import uuid

from core.domains.accounts.models import Account, AccountType
from core.domains.oms.entities.order import Order, OrderState, OrderType
from core.domains.oms.entities.deal import Deal, DealType
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
from core.domains.common.value_objects import Price, Volume, Money
from core.events.domain_events import DealCreated, PositionUpdated
from core.ports.interfaces import IOrderRepository, IEventBus, IAccountRepository, IPositionRepository, ISymbolRepository, IMarketDataFeed, IDealRepository
from core.domains.market_data.feed_access import await_tick, tick_bid, tick_ask

logger = logging.getLogger(__name__)


@dataclass
class RecordDealCommand:
    """
    Command to record an execution (fill).
    Triggered by the Matching Engine or Liquidity Gateway.
    """
    order_id: str
    account_login: str
    symbol: str
    volume: Decimal
    price: Decimal
    deal_type: DealType  # BUY, SELL, SWAP, COMMISSION
    commission_amount: Decimal = Decimal('0')
    swap_amount: Decimal = Decimal('0')
    profit: Decimal = Decimal('0')
    external_deal_id: Optional[str] = None  # ID from LP (e.g., LMAX, Binance)


def _accepts_session(method: Any) -> bool:
    """Does this repository method take a `session` keyword argument?

    The check this replaces was `_accepts_session(method)`, which reads a
    method's LOCAL VARIABLES as well as its parameters. SqlOrderRepository.find_by_id was
    declared `find_by_id(self, order_id)` but its body did
    `async with self.session_factory() as session:` - so the probe saw a name called
    "session", concluded the parameter existed, and passed `session=None` to a method that
    could not accept it: TypeError on the write path of every single fill, against the real
    repositories only. Test doubles declared the parameter, which is why it went unseen.
    """
    import inspect

    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        return False
    for name, parameter in signature.parameters.items():
        if name == "session":
            return True
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            return True
    return False


def position_action_for(deal_type: Any) -> PositionAction:
    """The PositionAction a deal opens, from its DealType.

    Position.action is a PositionAction, but this handler assigned it a DealType in
    hedging mode and an OrderType in netting mode. All three enums spell their members
    "BUY"/"SELL", so nothing raised - the values just were not equal:

      * Position.reverse() computed `SELL if self.action == PositionAction.BUY else BUY`
        and got BUY, so reversing a long produced another long;
      * the netting filter `pos.action == deal_side` never matched, so a netting account
        accumulated one position per deal instead of netting them;
      * LiquidationWorker's `p.action == PositionAction.BUY` was False for every position,
        so it valued longs at the ASK instead of the BID and picked the wrong one to close;
      * close_position chose the wrong closing side.

    Anything that is not a BUY is a SELL, which is the whole of PositionAction.
    """
    name = getattr(deal_type, "name", None) or str(deal_type)
    return PositionAction.BUY if str(name).upper().startswith("BUY") else PositionAction.SELL


class RecordDealHandler:
    """
    Handler for recording trades.

    Architectural Purpose:
    This is the critical 'Write' path for trade execution. It ensures
    atomicity of the 'Deal -> Position -> Balance' update sequence.
    Runs inside a DB Transaction via UnitOfWork.
    """

    def __init__(
        self,
        order_repo: IOrderRepository,
        account_repo: IAccountRepository,
        position_repo: IPositionRepository,
        event_bus: IEventBus,
        symbol_repo: ISymbolRepository,
        market_feed: IMarketDataFeed,
        deal_repo: Optional[IDealRepository] = None,
        uow_factory: Optional[Any] = None
    ):
        self.order_repo = order_repo
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.event_bus = event_bus
        self.symbol_repo = symbol_repo
        self.market_feed = market_feed
        self.deal_repo = deal_repo
        self.uow_factory = uow_factory

    async def execute(self, command: RecordDealCommand) -> Deal:
        logger.info(f"Recording Deal for Order {command.order_id}, Volume {command.volume}")

        if self.uow_factory:
            async with self.uow_factory() as uow:
                return await self._execute_internal(command, uow=uow)
        else:
            return await self._execute_internal(command)

    async def _execute_internal(self, command: RecordDealCommand, uow: Optional[Any] = None) -> Deal:
        session = uow.session if uow else None
        order_repo = uow.orders if uow and hasattr(uow, 'orders') else self.order_repo
        deal_repo = uow.deals if uow and hasattr(uow, 'deals') else self.deal_repo
        account_repo = uow.accounts if uow and hasattr(uow, 'accounts') else self.account_repo
        position_repo = uow.positions if uow and hasattr(uow, 'positions') else self.position_repo

        # 1. Fetch and Update Order
        order = await order_repo.find_by_id(command.order_id, session=session) if hasattr(order_repo, 'find_by_id') and _accepts_session(order_repo.find_by_id) else await order_repo.find_by_id(command.order_id)
        if not order:
            raise ValueError(f"Order {command.order_id} not found")

        # Apply fill to order (updates state to FILLED or PARTIALLY_FILLED)
        volume_obj = Volume(Decimal(str(command.volume)))
        price_obj = Price(Decimal(str(command.price)))

        try:
            order.apply_fill(volume_obj, price_obj)
        except ValueError as e:
            logger.error(f"Failed to apply fill to order {order.ticket_id}: {e}")
            raise

        if hasattr(order_repo, 'save') and _accepts_session(order_repo.save):
            await order_repo.save(order, session=session)
        else:
            await order_repo.save(order)

        # 2. Create Immutable Deal Entity
        deal_id = str(uuid.uuid4())
        deal = Deal(
            deal_id=deal_id,
            order_id=command.order_id,
            account_login=command.account_login,
            symbol=command.symbol,
            deal_type=command.deal_type,
            volume=volume_obj,
            price=price_obj,
            commission=Money(Decimal(str(command.commission_amount)), "USD"),
            swap=Money(Decimal(str(command.swap_amount)), "USD"),
            profit=Money(Decimal(str(command.profit)), "USD"),
            created_at=datetime.now(timezone.utc)
        )

        # Save Deal to Repository (Append-only log)
        if deal_repo:
            if hasattr(deal_repo, 'save') and _accepts_session(deal_repo.save):
                await deal_repo.save(deal, session=session)
            else:
                await deal_repo.save(deal)

        # 3. Fetch Account
        account = await account_repo.find_by_login(command.account_login, session=session) if hasattr(account_repo, 'find_by_login') and _accepts_session(account_repo.find_by_login) else await account_repo.find_by_login(command.account_login)
        if not account:
            raise ValueError(f"Account {command.account_login} not found")

        # 4. Apply Deal to Position(s)
        await self._apply_deal_to_positions(account, deal, order=order, position_repo=position_repo, session=session)

        # 5. Update Account Balance AND Margin
        if deal.profit.amount != 0:
            account.balance = account.balance + deal.profit
            logger.debug(f"Account {account.login} balance updated by {deal.profit.amount}")

        if deal.commission.amount != 0:
            account.balance = account.balance + deal.commission

        # M6: the approval's reservation has done its job - the real requirement
        # is recomputed into margin_used next. Release the order's exact hold (in
        # the same transaction when we have one) and zero the order's field so a
        # replay or a second deal on the same order cannot release it twice.
        await self._release_order_reservation(order, account, session=session)

        await self._recalculate_account_margin(account, position_repo=position_repo, session=session)

        if hasattr(account_repo, 'save') and _accepts_session(account_repo.save):
            await account_repo.save(account, session=session)
        else:
            await account_repo.save(account)

        # 6. Publish Event
        event = DealCreated(
            aggregate_id=deal.deal_id,
            payload={
                "deal_id": deal.deal_id,
                "order_id": deal.order_id,
                "account_login": deal.account_login,
                "symbol": deal.symbol,
                "type": deal.deal_type.value,
                "volume": str(deal.volume.value),
                "price": str(deal.price.value),
                "commission": str(deal.commission.amount),
                "profit": str(deal.profit.amount)
            }
        )
        await self.event_bus.publish(event)
        logger.info(f"Deal {deal.deal_id} recorded and event published")

        return deal

    async def _apply_deal_to_positions(self, account: Account, deal: Deal, order=None, position_repo=None, session=None):
        """
        Handles the complex logic of updating positions based on Deal type.
        Respects the Group's Position Mode (HEDGING vs NETTING).
        """
        if deal.deal_type not in [DealType.BUY, DealType.SELL]:
            return  # Ignore non-trading deals for position logic

        # MT5 SDK, IMTConGroup::EnMarginMode: MARGIN_MODE_RETAIL (0) and the
        # exchange modes use NETTING position accounting; MARGIN_MODE_RETAIL_HEDGED
        # (2) uses HEDGING. The group's MarginProfile.mode carries this straight
        # off the wire (MarginMode). This previously read
        # `account.group.execution.mode` - an attribute Group does not have - so
        # the guard yielded None and every account silently ran hedging: the
        # netting branch was unreachable code.
        margin_mode = getattr(getattr(account.group, 'margin', None), 'mode', None)
        group_mode = margin_mode  # HEDGING or NETTING, per EnMarginMode

        # Fetch symbol for contract size
        symbol = await self.symbol_repo.find_by_name(deal.symbol)
        if not symbol:
            raise ValueError(f"Symbol {deal.symbol} not found for position calculation")

        pos_repo = position_repo or self.position_repo

        mode_name = getattr(group_mode, 'name', str(group_mode) if group_mode else "")
        if mode_name in ("RETAIL", "EXCHANGE_DISCOUNT", "EXCHANGE", "NETTING"):
            # MarginMode.RETAIL is MT5's netting accounting (SDK: "The netting
            # position accounting system is used"); EXCHANGE_DISCOUNT likewise.
            # NETTING MODE: Opposite deals reduce/close existing positions
            await self._apply_deal_netting_mode(account, deal, symbol, order=order, position_repo=pos_repo, session=session)
        else:
            # HEDGING MODE (Default MT5 Retail): Every deal creates a new independent position
            await self._apply_deal_hedging_mode(account, deal, symbol, order=order, position_repo=pos_repo, session=session)

    async def _apply_deal_hedging_mode(self, account: Account, deal: Deal, symbol, order=None, position_repo=None, session=None):
        """Hedging: Every BUY/SELL creates a NEW independent position."""
        position_id = f"{account.login}_{deal.symbol}_{str(uuid.uuid4())[:8]}"

        new_position = Position(
            position_id=position_id,
            account_login=account.login,
            symbol=deal.symbol,
            volume=deal.volume,
            action=position_action_for(deal.deal_type),
            price_open=deal.price,
            contract_size=symbol.contract_size,
            time_create=datetime.now(timezone.utc),
            # M9: the opening order's SL/TP transfer onto the position. They were
            # dropped here before - a client's stop existed on the order, never on
            # the position, and nothing server-side could ever fire it.
            price_sl=order.price_sl if order is not None else None,
            price_tp=order.price_tp if order is not None else None,
        )

        pos_repo = position_repo or self.position_repo
        if hasattr(pos_repo, 'save') and _accepts_session(pos_repo.save):
            await pos_repo.save(new_position, session=session)
        else:
            await pos_repo.save(new_position)
        logger.debug(f"New Position {position_id} created (Hedging)")

        evt = PositionUpdated(
            aggregate_id=position_id,
            payload={
                "position_id": position_id,
                "account_login": account.login,
                "symbol": deal.symbol,
                "volume": str(new_position.volume.value),
                "side": new_position.action.value,
                "action": "OPENED"
            }
        )
        await self.event_bus.publish(evt)

    async def _apply_deal_netting_mode(self, account: Account, deal: Deal, symbol, order=None, position_repo=None, session=None):
        """
        Netting: Opposite deals reduce/close existing positions.
        Same direction adds to position.

        Every reduction books its realised PnL to the balance (M6): before this,
        the closed volume - and the client's profit or loss with it - simply
        disappeared, and the account kept trading with money it had already lost
        or earned. The result is computed by RiskEngine.realized_pnl, i.e. the
        same converted, side-correct maths the margin loop uses.
        """
        # PositionAction, not OrderType: this is compared against Position.action and
        # assigned to it below. See position_action_for().
        deal_side = position_action_for(deal.deal_type)
        pos_repo = position_repo or self.position_repo

        # Find existing position for this symbol and side
        existing_positions = await self._positions_for_account(pos_repo, account.login, session)
        existing_positions = [p for p in existing_positions if p.symbol == deal.symbol]

        # Filter for same side positions (in netting there should be only one per symbol)
        matching_position = None
        for pos in existing_positions:
            if pos.action == deal_side:
                matching_position = pos
                break

        if matching_position:
            # Same direction: Add to position
            if deal_side == matching_position.action:
                total_val = (matching_position.price_open.value * matching_position.volume.value) + \
                           (deal.price.value * deal.volume.value)
                new_vol = matching_position.volume.value + deal.volume.value
                matching_position.volume = Volume(new_vol)
                matching_position.price_open = Price(total_val / new_vol)
                if hasattr(pos_repo, 'save') and _accepts_session(pos_repo.save):
                    await pos_repo.save(matching_position, session=session)
                else:
                    await pos_repo.save(matching_position)
                logger.debug(f"Position {matching_position.position_id} increased (Netting)")
        else:
            # No existing position or opposite side: Create new or reverse
            opposite_positions = [p for p in existing_positions if p.action != deal_side]

            if opposite_positions:
                opp_pos = opposite_positions[0]
                if deal.volume.value < opp_pos.volume.value:
                    await self._book_netting_realized(
                        account, deal, opp_pos, symbol, deal.volume.value, session=session
                    )
                    opp_pos.volume = Volume(opp_pos.volume.value - deal.volume.value)
                    if hasattr(pos_repo, 'save') and _accepts_session(pos_repo.save):
                        await pos_repo.save(opp_pos, session=session)
                    else:
                        await pos_repo.save(opp_pos)
                    logger.debug(f"Position {opp_pos.position_id} partially closed (Netting)")
                elif deal.volume.value == opp_pos.volume.value:
                    await self._book_netting_realized(
                        account, deal, opp_pos, symbol, opp_pos.volume.value, session=session
                    )
                    await self._mark_closed(pos_repo, opp_pos, deal, session=session)
                    logger.debug(f"Position {opp_pos.position_id} fully closed (Netting)")
                else:
                    # Reversal: the whole old position closes at the deal price
                    # (its PnL is realised), and the remainder reopens flat.
                    # The old volume is captured BEFORE _mark_closed zeroes it -
                    # reading it afterwards made the reopened leg the full deal
                    # volume instead of the remainder.
                    old_vol = opp_pos.volume.value
                    await self._book_netting_realized(
                        account, deal, opp_pos, symbol, old_vol, session=session
                    )
                    await self._mark_closed(pos_repo, opp_pos, deal, session=session)
                    position_id = f"{account.login}_{deal.symbol}_{str(uuid.uuid4())[:8]}"
                    new_vol = deal.volume.value - old_vol
                    new_position = Position(
                        position_id=position_id,
                        account_login=account.login,
                        symbol=deal.symbol,
                        volume=Volume(new_vol),
                        action=deal_side,
                        price_open=deal.price,
                        contract_size=symbol.contract_size,
                        time_create=datetime.now(timezone.utc),
                        price_sl=order.price_sl if order is not None else None,
                        price_tp=order.price_tp if order is not None else None,
                    )
                    if hasattr(pos_repo, 'save') and _accepts_session(pos_repo.save):
                        await pos_repo.save(new_position, session=session)
                    else:
                        await pos_repo.save(new_position)
                    logger.debug(f"Position reversed (Netting)")
            else:
                position_id = f"{account.login}_{deal.symbol}_{str(uuid.uuid4())[:8]}"
                new_position = Position(
                    position_id=position_id,
                    account_login=account.login,
                    symbol=deal.symbol,
                    volume=deal.volume,
                    action=deal_side,
                    price_open=deal.price,
                    contract_size=symbol.contract_size,
                    time_create=datetime.now(timezone.utc)
                )
                if hasattr(pos_repo, 'save') and _accepts_session(pos_repo.save):
                    await pos_repo.save(new_position, session=session)
                else:
                    await pos_repo.save(new_position)
                logger.debug(f"New Position {position_id} created (Netting)")

    async def _mark_closed(self, pos_repo, position: Position, deal: Deal, session=None) -> None:
        """Close a position the way every other closing path does: keep the row.

        Volume to zero, time_done stamped, deal_close linked, saved. The previous
        `if hasattr(pos_repo, 'delete')` probe skipped silently on any repository
        without delete (the in-memory double has none), leaving a ghost position
        that kept being margined. Closed rows are history; deleting them is not
        what ClosePositionHandler or the LiquidationWorker do either.
        """
        position.volume = Volume(0)
        position.time_done = datetime.now(timezone.utc)
        position.deal_close = deal.deal_id
        if hasattr(pos_repo, 'save') and _accepts_session(pos_repo.save):
            await pos_repo.save(position, session=session)
        else:
            await pos_repo.save(position)

    async def _release_order_reservation(self, order, account, session=None) -> None:
        """Release the margin this order reserved at approval (M6)."""
        reserved = Decimal(str(getattr(order, "reserved_margin", 0) or 0))
        if reserved <= 0:
            return
        from application.services.margin_reservation import release_margin

        await release_margin(
            self.account_repo, account.login, reserved, account=account, session=session
        )
        order.reserved_margin = Decimal("0")
        order_repo = self.order_repo
        if hasattr(order_repo, "save"):
            if _accepts_session(order_repo.save):
                await order_repo.save(order, session=session)
            else:
                await order_repo.save(order)

    async def _book_netting_realized(
        self, account: Account, deal: Deal, position: Position, symbol,
        closed_volume: Decimal, session=None,
    ) -> None:
        """Book the realised result of a netting close onto the balance.

        The OUT deal also carries the realised profit, the way MT5's statements
        show it, and is re-saved so the ledger matches the balance movement.
        The account itself is persisted by the caller's flow (margin
        recalculation runs after this and the account save follows it).

        The symbol is passed in, already awaited by _apply_deal_to_positions:
        RiskEngine's symbol lookup is synchronous (ConfigCache-shaped) and this
        handler holds an ASYNC repository, so the conversion engine here is used
        for rates only - the same pattern _recalculate_account_margin uses - and
        the PnL itself goes through margin.position_pnl, the single source of
        truth (side-correct, quote->deposit converted).
        """
        from core.domains.market_data.margin import SymbolMarginSpec, position_pnl
        from core.domains.risk.engine import RiskEngine

        spec = SymbolMarginSpec.from_symbol(symbol)
        quote_currency = getattr(symbol, 'quote_currency', '') or spec.margin_currency
        action = position.action.value if hasattr(position.action, 'value') else str(position.action)
        conversion = RiskEngine(symbol_repo=self.symbol_repo, market_data_engine=self.market_feed)
        realized = position_pnl(
            side=action,
            volume_lots=Decimal(str(closed_volume)),
            open_price=position.price_open.value,
            bid=deal.price.value,
            ask=deal.price.value,
            contract_size=spec.contract_size,
            quote_currency=quote_currency,
            deposit_currency=account.currency,
            # _rate_lookup adapts (from, to, side) onto get_conversion_rate's
            # keyword-only side - passing the public method positionally would
            # land "PROFIT" in its market_feed parameter.
            rate_lookup=conversion._rate_lookup,
        )
        # The balance itself is booked ONCE, centrally: step 5 of _execute_internal
        # adds deal.profit to the balance. Setting the profit here and mutating the
        # balance too would book every netting close twice.
        deal.profit = Money(realized, account.currency)
        if hasattr(self.deal_repo, 'save'):
            if _accepts_session(self.deal_repo.save):
                await self.deal_repo.save(deal, session=session)
            else:
                await self.deal_repo.save(deal)
        logger.info(
            "netting close: %s %s of %s realised %s %s",
            closed_volume, position.action, position.symbol, realized, account.currency,
        )

    @staticmethod
    async def _positions_for_account(pos_repo, account_login: int, session=None) -> List[Position]:
        """Open positions for an account, through whichever name the repo exposes.

        Three names are in circulation (get_positions_by_account, get_by_account,
        find_by_account) because IPositionRepository declares the first as canonical
        and the second as a compatibility alias. Probing two of the three and falling
        back to an empty list meant a repository exposing only `get_by_account` - which
        the PostgreSQL one did - silently margined the account over ZERO positions,
        writing margin_used = 0 after every deal. An unknown repository shape is now an
        error, because "no positions" and "could not look" must not write the same
        numbers to the account.
        """
        for name in ("get_positions_by_account", "get_by_account", "find_by_account"):
            method = getattr(pos_repo, name, None)
            if method is None:
                continue
            accepts_session = _accepts_session(method)
            if accepts_session and session is not None:
                return await method(account_login, session=session)
            return await method(account_login)
        raise TypeError(
            f"{type(pos_repo).__name__} exposes none of get_positions_by_account / "
            f"get_by_account / find_by_account; account margin cannot be recalculated"
        )

    async def _recalculate_account_margin(self, account: Account, position_repo=None, session=None):
        """
        Recalculates margin_used and margin_free based on all open positions.
        Formula: Sum(Position.Volume * ContractSize * CurrentPrice) / Leverage
        """
        pos_repo = position_repo or self.position_repo
        all_positions = await self._positions_for_account(pos_repo, account.login, session)

        total_margin_used = Decimal('0')

        # Margin is computed once for the whole account through the MT5-accurate engine,
        # not per position with a local formula. This used to call
        # symbol.calculate_margin_required(...), a method that exists on Position and not
        # on Symbol, so it raised for every position - and because this is the
        # recalculation that runs after every deal and writes account.margin_used /
        # margin_free, the figures the stop-out logic reads were never updated at all.
        from core.domains.market_data.margin import (
            Leg,
            MarginCalculationError,
            SymbolMarginSpec,
            calculate_account_margin,
        )
        from core.domains.risk.engine import RiskEngine

        legs = []
        specs = {}
        unrealized = Decimal("0")
        conversion = RiskEngine(symbol_repo=self.symbol_repo, market_data_engine=self.market_feed)

        for position in all_positions:
            if position.volume.value == 0:
                continue

            symbol = await self.symbol_repo.find_by_name(position.symbol)
            if not symbol:
                # A position in a symbol that is not configured cannot be margined. Log it
                # loudly rather than skipping it silently: skipping understates the
                # requirement and lets the account trade past its margin.
                logger.error(
                    "position %s is in unconfigured symbol %s; it cannot be margined",
                    position.position_id,
                    position.symbol,
                )
                continue

            spec = SymbolMarginSpec.from_symbol(symbol)
            specs[position.symbol] = spec

            # await_tick handles both feed shapes. This used to be
            # `await self.market_feed.get_latest_tick(...)`, and MarketDataEngine's
            # getter is synchronous - awaiting its Tick raised TypeError on the write
            # path that runs after every single deal.
            tick = await await_tick(self.market_feed, position.symbol)
            bid = Decimal(str(tick["bid"])) if isinstance(tick, dict) and tick.get("bid") else None
            ask = Decimal(str(tick["ask"])) if isinstance(tick, dict) and tick.get("ask") else None
            if bid is None:
                bid = getattr(tick, "bid", None)
            if ask is None:
                ask = getattr(tick, "ask", None)

            action = (
                position.action.value if hasattr(position.action, "value") else str(position.action)
            )

            if bid and ask:
                from core.domains.market_data.margin import position_pnl

                try:
                    unrealized += position_pnl(
                        side=action,
                        volume_lots=position.volume.value,
                        open_price=position.price_open.value,
                        bid=Decimal(str(bid)),
                        ask=Decimal(str(ask)),
                        contract_size=spec.contract_size,
                        quote_currency=getattr(symbol, "quote_currency", "") or spec.margin_currency,
                        deposit_currency=account.currency,
                        rate_lookup=conversion._rate_lookup,
                    )
                except MarginCalculationError as exc:
                    logger.error(
                        "cannot value position %s (%s); equity will exclude it: %s",
                        position.position_id,
                        position.symbol,
                        exc,
                    )

            legs.append(
                Leg(
                    symbol=position.symbol,
                    operation=action,
                    volume=position.volume.value,
                    price=position.price_open.value,
                    is_pending=False,
                    spec=spec,
                )
            )

        if legs:
            breakdown = calculate_account_margin(
                legs,
                specs=specs,
                deposit_currency=account.currency,
                rate_lookup=conversion._rate_lookup,
                leverage=account.effective_leverage(),
                # Maintenance margin for positions already open. MT5: "When opening
                # positions, the initial margin is checked. For open positions, the
                # maintenance margin is checked."
                maintenance=True,
            )
            total_margin_used += breakdown.total

        currency = account.balance.currency
        # Equity is balance + credit + unrealised PnL, matching MT5 and matching
        # Account.update_equity. Using balance alone - as this did - ignores both broker
        # credit and open PnL, so a profitable account looked poorer than it was and a
        # client trading on credit was stopped out early.
        equity = account.balance.amount + account.credit.amount + unrealized
        account.margin_used = Money(total_margin_used, currency)
        account.margin_free = Money(equity - total_margin_used, currency)
        account.equity = Money(equity, currency)

        logger.debug(
            f"Account {account.login} margin recalculated: "
            f"Used={total_margin_used}, Free={account.margin_free.amount}"
        )
