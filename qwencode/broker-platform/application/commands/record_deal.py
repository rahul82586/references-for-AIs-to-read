"""
Record Deal Command Handler.
Triggered when a match occurs (Internal Engine or External LP Fill).
Updates Positions, Balances, and publishes Deal events.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
import uuid

from core.domains.accounts.models import Account, AccountType
from core.domains.oms.entities.order import Order, OrderState, OrderType
from core.domains.oms.entities.deal import Deal, DealType
from core.domains.oms.entities.position import Position
from core.domains.common.value_objects import Price, Volume, Money
from core.events.domain_events import DealCreated, PositionUpdated
from core.ports.interfaces import IOrderRepository, IEventBus, IAccountRepository, IPositionRepository, ISymbolRepository, IMarketDataFeed, IDealRepository

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
        order = await order_repo.find_by_id(command.order_id, session=session) if hasattr(order_repo, 'find_by_id') and 'session' in order_repo.find_by_id.__code__.co_varnames else await order_repo.find_by_id(command.order_id)
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

        if hasattr(order_repo, 'save') and 'session' in order_repo.save.__code__.co_varnames:
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
            if hasattr(deal_repo, 'save') and 'session' in deal_repo.save.__code__.co_varnames:
                await deal_repo.save(deal, session=session)
            else:
                await deal_repo.save(deal)

        # 3. Fetch Account
        account = await account_repo.find_by_login(command.account_login, session=session) if hasattr(account_repo, 'find_by_login') and 'session' in account_repo.find_by_login.__code__.co_varnames else await account_repo.find_by_login(command.account_login)
        if not account:
            raise ValueError(f"Account {command.account_login} not found")

        # 4. Apply Deal to Position(s)
        await self._apply_deal_to_positions(account, deal, position_repo=position_repo, session=session)

        # 5. Update Account Balance AND Margin
        if deal.profit.amount != 0:
            account.balance = account.balance + deal.profit
            logger.debug(f"Account {account.login_id} balance updated by {deal.profit.amount}")

        if deal.commission.amount != 0:
            account.balance = account.balance + deal.commission

        await self._recalculate_account_margin(account, position_repo=position_repo, session=session)

        if hasattr(account_repo, 'save') and 'session' in account_repo.save.__code__.co_varnames:
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

    async def _apply_deal_to_positions(self, account: Account, deal: Deal, position_repo=None, session=None):
        """
        Handles the complex logic of updating positions based on Deal type.
        Respects the Group's Position Mode (HEDGING vs NETTING).
        """
        if deal.deal_type not in [DealType.BUY, DealType.SELL]:
            return  # Ignore non-trading deals for position logic

        group_mode = account.group.execution.mode if hasattr(account.group, 'execution') and hasattr(account.group.execution, 'mode') else None  # HEDGING or NETTING

        # Fetch symbol for contract size
        symbol = await self.symbol_repo.find_by_name(deal.symbol)
        if not symbol:
            raise ValueError(f"Symbol {deal.symbol} not found for position calculation")

        pos_repo = position_repo or self.position_repo

        if (hasattr(group_mode, 'name') and group_mode.name in ["EXCHANGE", "NETTING"]):
            # NETTING MODE: Opposite deals reduce/close existing positions
            await self._apply_deal_netting_mode(account, deal, symbol, position_repo=pos_repo, session=session)
        else:
            # HEDGING MODE (Default MT5 Retail): Every deal creates a new independent position
            await self._apply_deal_hedging_mode(account, deal, symbol, position_repo=pos_repo, session=session)

    async def _apply_deal_hedging_mode(self, account: Account, deal: Deal, symbol, position_repo=None, session=None):
        """Hedging: Every BUY/SELL creates a NEW independent position."""
        position_id = f"{account.login_id}_{deal.symbol}_{str(uuid.uuid4())[:8]}"

        new_position = Position(
            id=position_id,
            account_login=account.login_id,
            symbol=deal.symbol,
            volume=deal.volume,
            side=deal.deal_type,
            average_price=deal.price,
            contract_size=symbol.contract_size,
            opened_at=datetime.now(timezone.utc)
        )

        pos_repo = position_repo or self.position_repo
        if hasattr(pos_repo, 'save') and 'session' in pos_repo.save.__code__.co_varnames:
            await pos_repo.save(new_position, session=session)
        else:
            await pos_repo.save(new_position)
        logger.debug(f"New Position {position_id} created (Hedging)")

        evt = PositionUpdated(
            aggregate_id=position_id,
            payload={
                "position_id": position_id,
                "account_login": account.login_id,
                "symbol": deal.symbol,
                "volume": str(new_position.volume.value),
                "side": new_position.side.value,
                "action": "OPENED"
            }
        )
        await self.event_bus.publish(evt)

    async def _apply_deal_netting_mode(self, account: Account, deal: Deal, symbol, position_repo=None, session=None):
        """
        Netting: Opposite deals reduce/close existing positions.
        Same direction adds to position.
        """
        deal_side = OrderType.BUY if deal.deal_type == DealType.BUY else OrderType.SELL
        pos_repo = position_repo or self.position_repo

        # Find existing position for this symbol and side
        existing_positions = await pos_repo.get_positions_by_account(account.login_id) if hasattr(pos_repo, 'get_positions_by_account') else await pos_repo.find_by_account(account.login_id)
        existing_positions = [p for p in existing_positions if p.symbol == deal.symbol]

        # Filter for same side positions (in netting there should be only one per symbol)
        matching_position = None
        for pos in existing_positions:
            if pos.side == deal_side:
                matching_position = pos
                break

        if matching_position:
            # Same direction: Add to position
            if deal_side == matching_position.side:
                total_val = (matching_position.average_price.value * matching_position.volume.value) + \
                           (deal.price.value * deal.volume.value)
                new_vol = matching_position.volume.value + deal.volume.value
                matching_position.volume = Volume(new_vol)
                matching_position.average_price = Price(total_val / new_vol)
                if hasattr(pos_repo, 'save') and 'session' in pos_repo.save.__code__.co_varnames:
                    await pos_repo.save(matching_position, session=session)
                else:
                    await pos_repo.save(matching_position)
                logger.debug(f"Position {matching_position.id} increased (Netting)")
        else:
            # No existing position or opposite side: Create new or reverse
            opposite_positions = [p for p in existing_positions if p.side != deal_side]

            if opposite_positions:
                opp_pos = opposite_positions[0]
                if deal.volume.value < opp_pos.volume.value:
                    opp_pos.volume = Volume(opp_pos.volume.value - deal.volume.value)
                    if hasattr(pos_repo, 'save') and 'session' in pos_repo.save.__code__.co_varnames:
                        await pos_repo.save(opp_pos, session=session)
                    else:
                        await pos_repo.save(opp_pos)
                    logger.debug(f"Position {opp_pos.id} partially closed (Netting)")
                elif deal.volume.value == opp_pos.volume.value:
                    if hasattr(pos_repo, 'delete'):
                        await pos_repo.delete(opp_pos.id)
                    logger.debug(f"Position {opp_pos.id} fully closed (Netting)")
                else:
                    if hasattr(pos_repo, 'delete'):
                        await pos_repo.delete(opp_pos.id)
                    position_id = f"{account.login_id}_{deal.symbol}_{str(uuid.uuid4())[:8]}"
                    new_vol = deal.volume.value - opp_pos.volume.value
                    new_position = Position(
                        id=position_id,
                        account_login=account.login_id,
                        symbol=deal.symbol,
                        volume=Volume(new_vol),
                        side=deal_side,
                        average_price=deal.price,
                        contract_size=symbol.contract_size,
                        opened_at=datetime.now(timezone.utc)
                    )
                    if hasattr(pos_repo, 'save') and 'session' in pos_repo.save.__code__.co_varnames:
                        await pos_repo.save(new_position, session=session)
                    else:
                        await pos_repo.save(new_position)
                    logger.debug(f"Position reversed (Netting)")
            else:
                position_id = f"{account.login_id}_{deal.symbol}_{str(uuid.uuid4())[:8]}"
                new_position = Position(
                    id=position_id,
                    account_login=account.login_id,
                    symbol=deal.symbol,
                    volume=deal.volume,
                    side=deal_side,
                    average_price=deal.price,
                    contract_size=symbol.contract_size,
                    opened_at=datetime.now(timezone.utc)
                )
                if hasattr(pos_repo, 'save') and 'session' in pos_repo.save.__code__.co_varnames:
                    await pos_repo.save(new_position, session=session)
                else:
                    await pos_repo.save(new_position)
                logger.debug(f"New Position {position_id} created (Netting)")

    async def _recalculate_account_margin(self, account: Account, position_repo=None, session=None):
        """
        Recalculates margin_used and margin_free based on all open positions.
        Formula: Sum(Position.Volume * ContractSize * CurrentPrice) / Leverage
        """
        pos_repo = position_repo or self.position_repo
        if hasattr(pos_repo, 'get_positions_by_account') and 'session' in pos_repo.get_positions_by_account.__code__.co_varnames:
            all_positions = await pos_repo.get_positions_by_account(account.login_id, session=session)
        elif hasattr(pos_repo, 'get_positions_by_account'):
            all_positions = await pos_repo.get_positions_by_account(account.login_id)
        elif hasattr(pos_repo, 'find_by_account'):
            all_positions = await pos_repo.find_by_account(account.login_id)
        else:
            all_positions = []

        total_margin_used = Decimal('0')

        for position in all_positions:
            if position.volume.value == 0:
                continue

            tick = await self.market_feed.get_latest_tick(position.symbol) if self.market_feed else None
            current_price = Decimal(tick['ask']) if (tick and isinstance(tick, dict) and 'ask' in tick) else getattr(tick, 'ask', position.average_price.value)

            symbol = await self.symbol_repo.find_by_name(position.symbol)
            if not symbol:
                continue

            position_margin = symbol.calculate_margin_required(
                position.volume.value,
                Decimal(str(current_price))
            )
            total_margin_used += position_margin

        currency = account.balance.currency
        account.margin_used = Money(total_margin_used, currency)
        account.margin_free = Money(account.balance.amount - total_margin_used, currency)

        logger.debug(
            f"Account {account.login_id} margin recalculated: "
            f"Used={total_margin_used}, Free={account.margin_free.amount}"
        )
