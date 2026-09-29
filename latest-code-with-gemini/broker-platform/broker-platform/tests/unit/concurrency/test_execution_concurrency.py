from core.domains.accounts.models import MarginProfile
import asyncio
import pytest
from decimal import Decimal
from datetime import datetime, timezone

from core.domains.accounts.models import Account, Group, AccountType, MarginProfile
from core.domains.instruments.models import Symbol
from core.domains.oms.entities.order import Order, OrderType, OrderState
from core.domains.oms.entities.deal import Deal, DealType
from core.domains.common.value_objects import Money, Price, Volume
from application.services.risk_service import PreTradeRiskService
from application.commands.record_deal import RecordDealCommand, RecordDealHandler


class MockEventBus:
    async def publish(self, event):
        pass


class MockOrderRepository:
    def __init__(self):
        self.orders = {}

    async def find_by_id(self, order_id: str, session=None):
        return self.orders.get(order_id)

    async def save(self, order, session=None):
        self.orders[order.ticket_id] = order
        return order


class MockAccountRepository:
    def __init__(self):
        self.accounts = {}

    async def find_by_login(self, login_id: str, session=None):
        return self.accounts.get(str(login_id))

    async def save(self, account, session=None):
        self.accounts[str(account.login)] = account
        return account


class MockPositionRepository:
    def __init__(self):
        self.positions = {}

    async def find_by_account(self, account_login: str, session=None):
        return [p for p in self.positions.values() if str(p.account_login) == str(account_login)]

    async def get_positions_by_account(self, account_login: str, session=None):
        return await self.find_by_account(account_login, session)

    async def save(self, position, session=None):
        self.positions[position.position_id] = position
        return position


class MockSymbolRepository:
    def __init__(self, symbol):
        self.symbol = symbol

    async def find_by_name(self, name: str):
        return self.symbol


class MockMarketFeed:
    """A feed readable both ways.

    RecordDealHandler awaits `get_latest_tick`. RiskEngine reads the feed SYNCHRONOUSLY -
    deliberately, since margin sits on the pre-trade hot path and an await there would put
    the feed's latency in front of every order. A mock that only offered the async form
    gave the engine no tick at all, so it could not price or convert anything.

    EURUSD is present because EUR -> USD is a real conversion for a USD account: the
    symbol's margin currency is EUR, and the engine refuses to assume 1.0.
    """

    _TICKS = {
        "EURUSD": {"bid": "1.1000", "ask": "1.1005"},
        "USDJPY": {"bid": "149.990", "ask": "150.000"},
    }

    async def get_latest_tick(self, symbol: str):
        return self._TICKS.get(symbol)

    def get_bid(self, symbol: str):
        tick = self._TICKS.get(symbol)
        return Decimal(tick["bid"]) if tick else None

    def get_ask(self, symbol: str):
        tick = self._TICKS.get(symbol)
        return Decimal(tick["ask"]) if tick else None


@pytest.mark.asyncio
async def test_concurrent_deal_execution_atomicity_and_locking():
    """
    Test firing two concurrent orders for the same account using asyncio.gather.
    Ensures per-account locking prevents race conditions and math is exact.
    """
    group = Group(name="REAL_STANDARD", margin=MarginProfile(leverage_default=100))
    account = Account(
        login=100001,
        group=group,
        account_type=AccountType.REAL,
        balance=Money(Decimal('10000.00'), "USD")
    )

    symbol = Symbol(
        name="EURUSD",
        path="Forex\\EURUSD",
        tick_size=Decimal('0.00001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=5,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01')
    )

    order1 = Order(
        ticket_id="ORD_1",
        account_login="100001",
        symbol="EURUSD",
        order_type=OrderType.BUY,
        volume_initial=Volume(Decimal('1.0')),
        price_order=Price(Decimal('1.1000')),
        state=OrderState.STARTED
    )

    order2 = Order(
        ticket_id="ORD_2",
        account_login="100001",
        symbol="EURUSD",
        order_type=OrderType.BUY,
        volume_initial=Volume(Decimal('1.0')),
        price_order=Price(Decimal('1.1000')),
        state=OrderState.STARTED
    )

    # An order cannot go STARTED -> FILLED. Order._VALID_TRANSITIONS requires it to be
    # PLACED first, which is correct: an order that was never sent to the market cannot be
    # filled against it. The test previously relied on the transition being allowed, so it
    # was really asserting that the state machine was too permissive.
    order1.transition_to(OrderState.PLACED)
    order2.transition_to(OrderState.PLACED)

    order_repo = MockOrderRepository()
    await order_repo.save(order1)
    await order_repo.save(order2)

    account_repo = MockAccountRepository()
    await account_repo.save(account)

    position_repo = MockPositionRepository()
    symbol_repo = MockSymbolRepository(symbol)
    event_bus = MockEventBus()
    market_feed = MockMarketFeed()

    risk_service = PreTradeRiskService()
    handler = RecordDealHandler(
        order_repo=order_repo,
        account_repo=account_repo,
        position_repo=position_repo,
        event_bus=event_bus,
        symbol_repo=symbol_repo,
        market_feed=market_feed
    )

    cmd1 = RecordDealCommand(
        order_id="ORD_1",
        account_login="100001",
        symbol="EURUSD",
        volume=Decimal('1.0'),
        price=Decimal('1.1000'),
        deal_type=DealType.BUY,
        commission_amount=Decimal('-5.00')
    )

    cmd2 = RecordDealCommand(
        order_id="ORD_2",
        account_login="100001",
        symbol="EURUSD",
        volume=Decimal('1.0'),
        price=Decimal('1.1000'),
        deal_type=DealType.BUY,
        commission_amount=Decimal('-5.00')
    )

    # Wrap inside per-account locks to simulate two-phase pipeline concurrency
    async def process_order(cmd):
        async with risk_service.account_lock(cmd.account_login):
            return await handler.execute(cmd)

    results = await asyncio.gather(process_order(cmd1), process_order(cmd2))

    updated_account = await account_repo.find_by_login("100001")

    # Starting balance = 10000.00, 2x $5 commissions = 9990.00
    assert updated_account.balance.amount == Decimal('9990.00')

    # Each position margin = (1.0 * 100000 * 1.1005) * 0.01 = 1100.50
    # 2 positions margin used = 2201.00
    assert updated_account.margin_used.amount == Decimal('2201.00')
    assert len(results) == 2
