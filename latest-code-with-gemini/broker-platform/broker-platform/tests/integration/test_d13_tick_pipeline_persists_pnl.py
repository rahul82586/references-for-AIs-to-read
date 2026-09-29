"""D13 - the tick pipeline computed position PnL and then threw it away.

`TickMarginPipeline.process_tick()` did this:

    step 4   positions = await position_repo.get_by_symbol(symbol)
             for p in positions: p.update_unrealized_pnl(price, rate)   # in memory
    step 5   for login, account in accounts.items():
                 all_positions = await position_repo.get_by_account(login)  # SECOND fetch
                 total = sum(p.profit.amount for p in all_positions)        # reads the DB again
                 account.update_equity(total)
                 for p in all_positions: await position_repo.save(p)        # saves the STALE rows

The objects mutated in step 4 are never saved. Against a SQL repository every
fetch builds a NEW `Position` via `db_to_position(model)`, so step 5's
`get_by_account()` returns fresh copies straight from the database - still holding
`profit` 0 and `price_current` NULL - and those are what get summed into equity and
written back.

Observed live against Neon with a real MT5 feed delivering BTCUSD ticks every
~0.6s (`scripts/probe_position_repricing.py`):

    row price_current=None profit=0E-8   | account equity=100000.0000
    /account/positions unrealized_pnl=-0.5116      <- computed on demand, correct

so the client-facing query was right (M12 revalues on demand) while the stored
state never moved at all. Consequences, none of them cosmetic:

  * `position.price_current` stays NULL for the life of the position, so a market
    close has no price and falls back to `price_open`, booking zero PnL (the
    handler says so at WARNING). This is what the D12 cloud proof tripped over.
  * account `equity` is written as `balance`, so it never reflects open PnL.
  * `evaluate_margin_state()` therefore sees a flat equity, and the margin-call /
    stop-out state machine is unreachable from ticks - the liquidation worker has
    nothing to act on.

Every existing test missed it because `MockPositionRepository` returns the SAME
objects from both fetches, so the in-memory mutation is visible to step 5. The
mock was more coherent than the database. `CopyOnReadPositionRepository` below is
the honest double: it hands back a new object per fetch, exactly like
`db_to_position()`.
"""
import asyncio
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

import pytest

from application.services.tick_margin_pipeline import TickMarginPipeline
from core.domains.accounts.account import Account
from core.domains.accounts.enums import (
    AccountType, FreeMarginMode, MarginMode, StopOutMode,
)
from core.domains.accounts.group import Group, MarginProfile
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.instruments.symbol import Symbol
from core.domains.market_data.models import Tick
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
from core.domains.risk.engine import RiskEngine
from core.events.domain_events import DomainEvent
from core.ports.interfaces import (
    IAccountRepository, IEventBus, IPositionRepository, ISymbolRepository,
)


# ------------------------------------------------------------------ the doubles

class CopyOnReadPositionRepository(IPositionRepository):
    """Like the SQL repository: every read builds a NEW Position object.

    `save()` deep-copies into the store too, so holding a reference and mutating
    it afterwards cannot leak into "the database" - which is exactly what happens
    with an ORM session that is closed between calls.
    """

    def __init__(self):
        self.store: Dict[str, Position] = {}
        self.fetches = 0
        self.saves = 0
        self.valuations = 0
        #: set by a test to run between this repo's read and its write, i.e. exactly
        #: where a concurrent close lands in production
        self.on_after_fetch = None

    def _copy(self, p: Position) -> Position:
        return replace(
            p,
            volume=Volume(p.volume.value),
            price_open=Price(p.price_open.value),
            price_current=(Price(p.price_current.value) if p.price_current else None),
            profit=Money(p.profit.amount, p.profit.currency),
            swap=Money(p.swap.amount, p.swap.currency),
            commission=Money(p.commission.amount, p.commission.currency),
        )

    async def save(self, position: Position, session=None) -> Position:
        self.saves += 1
        self.store[position.position_id] = self._copy(position)
        return self.store[position.position_id]

    async def find_by_id(self, position_id: str) -> Optional[Position]:
        self.fetches += 1
        p = self.store.get(position_id)
        return self._copy(p) if p else None

    async def get_open_positions(self, session=None) -> List[Position]:
        self.fetches += 1
        return [self._copy(p) for p in self.store.values() if p.time_done is None]

    async def get_by_account(self, account_login: int, session=None) -> List[Position]:
        self.fetches += 1
        return [self._copy(p) for p in self.store.values()
                if p.account_login == account_login and p.time_done is None]

    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Position]:
        self.fetches += 1
        return [self._copy(p) for p in self.store.values()
                if p.account_login == account_login and p.symbol == symbol
                and p.time_done is None]

    async def get_by_symbol(self, symbol: str) -> List[Position]:
        self.fetches += 1
        rows = [self._copy(p) for p in self.store.values()
                if p.symbol == symbol and p.time_done is None]
        if self.on_after_fetch is not None:
            await self.on_after_fetch()
        return rows

    async def get_closed_positions(self, account_login: int, from_time: datetime,
                                   to_time: datetime) -> List[Position]:
        self.fetches += 1
        return [self._copy(p) for p in self.store.values()
                if p.account_login == account_login and p.time_done is not None]

    async def update_valuation(self, position_id: str, side: str, price_current,
                               when=None, session=None):
        """Faithful to the SQL statement: compute from the STORED row, skip closed.

        This is what makes the double able to catch D15. It reads the volume the
        store holds at write time - not the volume the caller thinks it has - and
        it refuses a position that has been closed since the caller fetched it.
        """
        self.valuations += 1
        stored = self.store.get(position_id)
        if stored is None or stored.time_done is not None:
            return None
        price = Decimal(str(price_current))
        diff = (price - stored.price_open.value) if str(side).upper().startswith("BUY") \
            else (stored.price_open.value - price)
        profit = diff * stored.volume.value * stored.contract_size
        stored.profit = Money(profit, stored.profit.currency)
        stored.price_current = Price(price)
        return {"volume": stored.volume.value, "profit": profit, "price_current": price}

    async def delete(self, position_id: str) -> bool:
        return self.store.pop(position_id, None) is not None


class RecordingAccountRepository(IAccountRepository):
    """Column-scoped writes only, like `update_valuation()` in the SQL repository."""

    def __init__(self):
        self.accounts: Dict[int, Account] = {}
        self.valuation_writes = 0

    async def save(self, account: Account, session=None) -> Account:
        self.accounts[account.login] = account
        return account

    async def find_by_login(self, login: int) -> Optional[Account]:
        return self.accounts.get(login)

    async def find_all(self) -> List[Account]:
        return list(self.accounts.values())

    async def update_valuation(self, account: Account) -> int:
        self.valuation_writes += 1
        self.accounts[account.login] = account
        return 1

    async def delete(self, login: int) -> bool:
        return self.accounts.pop(login, None) is not None


class SymbolRepositoryDouble(ISymbolRepository):
    def __init__(self, symbols: List[Symbol]):
        self.symbols = {s.name: s for s in symbols}

    async def find_by_name(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    async def get_all(self) -> List[Symbol]:
        return list(self.symbols.values())

    get_all_symbols = get_all

    def get_symbol(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    async def save(self, symbol: Symbol, session=None) -> Symbol:
        self.symbols[symbol.name] = symbol
        return symbol

    async def delete(self, name: str) -> bool:
        return self.symbols.pop(name, None) is not None


class EventBusDouble(IEventBus):
    def __init__(self):
        self.published: List[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.published.append(event)

    async def subscribe(self, channel, callback) -> None:
        pass

    async def disconnect(self) -> None:
        pass


# ------------------------------------------------------------------- the world

LOGIN = 100001


def build_world(stop_out: Decimal = Decimal("50"), margin_call: Decimal = Decimal("80")):
    group = Group(
        name="REAL_STANDARD", account_type=AccountType.REAL, currency="USD",
        margin=MarginProfile(
            mode=MarginMode.RETAIL, leverage_default=100, leverage_max=500,
            margin_call_level=margin_call, stop_out_level=stop_out,
            stop_out_mode=StopOutMode.PERCENT, free_margin_mode=FreeMarginMode.USE_PL,
        ),
    )
    account = Account(
        login=LOGIN, client_id="CLIENT_D13", group_id=group.id, group=group,
        account_type=AccountType.REAL, currency="USD",
        balance=Money(Decimal("10000.00"), "USD"),
        equity=Money(Decimal("10000.00"), "USD"),
        margin_used=Money(Decimal("5500.00"), "USD"),
        margin_free=Money(Decimal("4500.00"), "USD"),
        margin_level=Decimal("181.8"),
    )
    eurusd = Symbol(
        name="EURUSD", path="Forex\\EURUSD", base_currency="EUR", quote_currency="USD",
        tick_size=Decimal("0.00001"), tick_value=Decimal("1.0"),
        contract_size=Decimal("100000"), digits=5,
        volume_min=Decimal("0.01"), volume_max=Decimal("100.0"), volume_step=Decimal("0.01"),
    )
    # 5.0 lots BUY at 1.1000: margin 5500, so a 0.0100 fall is -5000 of PnL
    position = Position(
        position_id="POS_D13", account_login=LOGIN, symbol="EURUSD",
        action=PositionAction.BUY, volume=Volume(Decimal("5.0")),
        price_open=Price(Decimal("1.1000")), price_current=None,
        contract_size=Decimal("100000"), profit=Money(Decimal("0"), "USD"),
    )
    position_repo = CopyOnReadPositionRepository()
    account_repo = RecordingAccountRepository()
    symbol_repo = SymbolRepositoryDouble([eurusd])
    bus = EventBusDouble()
    return group, account, position, position_repo, account_repo, symbol_repo, bus


async def pipeline_for(position_repo, account_repo, symbol_repo, bus) -> TickMarginPipeline:
    engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=None)
    return TickMarginPipeline(
        position_repo=position_repo, account_repo=account_repo,
        symbol_repo=symbol_repo, risk_engine=engine, event_bus=bus,
    )


def tick(bid: str, ask: str) -> Tick:
    return Tick(symbol="EURUSD", bid=Decimal(bid), ask=Decimal(ask),
                spread=Decimal(ask) - Decimal(bid),
                timestamp=datetime.now(timezone.utc))


# -------------------------------------------------------------------- the tests

@pytest.mark.asyncio
async def test_a_tick_persists_the_pnl_it_computed():
    """The headline defect: step 4 computed it, step 5 saved something else."""
    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    await pos_repo.save(position)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    await pipeline.process_tick(tick("1.0900", "1.0902"))   # -5000

    stored = await pos_repo.find_by_id("POS_D13")
    assert stored.profit.amount == Decimal("-5000.00"), (
        f"the position row still says {stored.profit.amount}; the PnL this tick "
        f"computed was never written")
    assert stored.price_current is not None, (
        "price_current is still NULL, so a market close has no price to deal at")
    assert stored.price_current.value == Decimal("1.0900"), (
        "a BUY is valued at the bid")


@pytest.mark.asyncio
async def test_equity_follows_the_pnl_rather_than_the_balance():
    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    await pos_repo.save(position)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    await pipeline.process_tick(tick("1.0900", "1.0902"))   # -5000

    after = await acc_repo.find_by_login(LOGIN)
    assert after.equity.amount == Decimal("5000.00"), (
        f"equity is {after.equity.amount}: it was written as balance + the STALE "
        f"profit, so a live tick never moves it")
    assert after.profit.amount == Decimal("-5000.00"), (
        f"account profit is {after.profit.amount}")
    assert acc_repo.valuation_writes >= 1, "the column-scoped write must be the one used"


@pytest.mark.asyncio
async def test_stop_out_becomes_reachable_from_a_tick():
    """The point of the pipeline: a falling market must reach the state machine."""
    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    await pos_repo.save(position)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    await pipeline.process_tick(tick("1.0900", "1.0902"))   # equity 5000, level 90.9%
    assert not [e for e in bus.published if type(e).__name__ == "StopOutEntered"]

    # The state machine steps once per evaluation (test_margin_loop.py pins that),
    # so a gap straight through both levels needs one more tick to reach stop-out.
    await pipeline.process_tick(tick("1.0830", "1.0832"))   # equity 1500, level 27.3%
    names = [type(e).__name__ for e in bus.published]
    assert "MarginCallEntered" in names, f"events={names}"
    assert "StopOutEntered" not in names, f"one step per tick; events={names}"

    await pipeline.process_tick(tick("1.0820", "1.0822"))   # still below stop-out
    names = [type(e).__name__ for e in bus.published]
    assert "StopOutEntered" in names, (
        f"equity is 27% of margin and stop-out was never entered; events={names}")
    stopped = [e for e in bus.published if type(e).__name__ == "StopOutEntered"][0]
    assert Decimal(stopped.payload["equity"]) < Decimal("2000"), stopped.payload


@pytest.mark.asyncio
async def test_two_symbols_in_one_account_both_count():
    """Step 5 sums every open position, so a second symbol must not be lost."""
    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    gbpusd = Symbol(
        name="GBPUSD", path="Forex\\GBPUSD", base_currency="GBP", quote_currency="USD",
        tick_size=Decimal("0.00001"), tick_value=Decimal("1.0"),
        contract_size=Decimal("100000"), digits=5,
        volume_min=Decimal("0.01"), volume_max=Decimal("100.0"), volume_step=Decimal("0.01"),
    )
    await sym_repo.save(gbpusd)
    other = Position(
        position_id="POS_D13_GBP", account_login=LOGIN, symbol="GBPUSD",
        action=PositionAction.BUY, volume=Volume(Decimal("1.0")),
        price_open=Price(Decimal("1.3000")), price_current=Price(Decimal("1.3100")),
        contract_size=Decimal("100000"), profit=Money(Decimal("1000"), "USD"),
    )
    await pos_repo.save(position)
    await pos_repo.save(other)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    # an EURUSD tick must not wipe the GBPUSD leg's stored PnL
    await pipeline.process_tick(tick("1.0900", "1.0902"))   # EURUSD -5000

    gbp = await pos_repo.find_by_id("POS_D13_GBP")
    assert gbp.profit.amount == Decimal("1000"), (
        f"the untouched leg's profit became {gbp.profit.amount}")
    after = await acc_repo.find_by_login(LOGIN)
    assert after.equity.amount == Decimal("6000.00"), (
        f"equity {after.equity.amount} != balance 10000 + (-5000 + 1000)")


# ------------------------------------------------- D15: the concurrent close race

@pytest.mark.asyncio
async def test_a_close_landing_mid_tick_is_not_undone():
    """D15: measured live against Neon as an OUT deal for the ORIGINAL volume.

    The pipeline fetched the position, then a client closed half of it, then the
    pipeline wrote. With a full-row `save()` the write restored the volume the
    close had just reduced, and the NEXT close dealt a size the client no longer
    had. The column-scoped write computes profit from the row as it stands and
    returns what it wrote, so the pipeline's own view converges on the database
    instead of overwriting it.
    """
    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    await pos_repo.save(position)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    closed_half = asyncio.Event()

    async def partial_close():
        """Stand in for ClosePositionHandler: halve the volume and stamp the deal."""
        row = pos_repo.store["POS_D13"]
        row.volume = Volume(Decimal("2.5"))
        row.deal_close = None            # a partial close leaves it open
        closed_half.set()

    pos_repo.on_after_fetch = partial_close
    await pipeline.process_tick(tick("1.0900", "1.0902"))
    assert closed_half.is_set(), "the close must land between the read and the write"

    stored = await pos_repo.find_by_id("POS_D13")
    assert stored.volume.value == Decimal("2.5"), (
        f"the tick write restored the pre-close volume: {stored.volume.value}")
    # -0.0100 x 2.5 lots x 100000 = -2500, i.e. the PnL of the position that is
    # actually there, not of the 5 lots the pipeline had fetched
    assert stored.profit.amount == Decimal("-2500.00"), (
        f"profit {stored.profit.amount} was computed from a volume that no longer exists")
    after = await acc_repo.find_by_login(LOGIN)
    assert after.equity.amount == Decimal("7500.00"), (
        f"equity {after.equity.amount} ignored the close that landed mid-tick")


@pytest.mark.asyncio
async def test_a_full_close_mid_tick_drops_the_position_from_equity():
    """`time_done IS NULL` is what stops a tick revaluing a position that is gone."""
    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    await pos_repo.save(position)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    from datetime import datetime as _dt

    async def full_close():
        row = pos_repo.store["POS_D13"]
        row.volume = Volume(Decimal("0"))
        row.time_done = _dt.now(timezone.utc)
        row.deal_close = "DEAL_OUT"

    pos_repo.on_after_fetch = full_close
    await pipeline.process_tick(tick("1.0900", "1.0902"))

    after = await acc_repo.find_by_login(LOGIN)
    assert after.equity.amount == Decimal("10000.00"), (
        f"equity {after.equity.amount} still carries a PnL for a closed position")
    assert pos_repo.store["POS_D13"].profit.amount == Decimal("0"), (
        "the tick wrote a PnL onto a position that was already closed")


@pytest.mark.asyncio
async def test_repository_without_the_scoped_write_still_persists_but_says_so(caplog):
    """The fallback must work and must be loud: it is the racy path."""
    import logging

    class NoScopedWrite(CopyOnReadPositionRepository):
        """A repository that predates D15 - it has no column-scoped write at all.

        Shadowing at CLASS level matters: `del instance.update_valuation` would
        still leave the bound method on the class, getattr would find it, and the
        test would exercise the atomic path while claiming to test the fallback.
        """

        update_valuation = None

    _, account, position, pos_repo, acc_repo, sym_repo, bus = build_world()
    pos_repo = NoScopedWrite()
    pos_repo.store["POS_D13"] = position
    await pos_repo.save(position)
    await acc_repo.save(account)
    pipeline = await pipeline_for(pos_repo, acc_repo, sym_repo, bus)

    with caplog.at_level(logging.WARNING, logger="application.services.tick_margin_pipeline"):
        await pipeline.process_tick(tick("1.0900", "1.0902"))

    stored = await pos_repo.find_by_id("POS_D13")
    assert stored.profit.amount == Decimal("-5000.00"), "the legacy path must still persist"
    assert any("update_valuation" in r.message for r in caplog.records), (
        "the full-row fallback ran silently - an operator would never know they are on it")
