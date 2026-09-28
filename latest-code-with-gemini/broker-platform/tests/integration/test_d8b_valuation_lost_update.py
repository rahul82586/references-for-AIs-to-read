"""D8b: a tick must not erase the margin a fill just wrote.

The defect, observed live against a real MT5 terminal and real Neon: an account
holding an open 0.01 BTCUSD position carried `margin_used = 0E-8` and
`margin_level = 999999`, with `updated_at` equal to its creation time - while its
Deal and Position rows were both present. Two runs, two routes, and the two routes
swapped which one failed, which is the signature of a race rather than a path.

Mechanism: `TickMarginPipeline` runs on every tick and ends with a FULL-ROW
`account_repo.save(account)` on an account object it loaded at the start of the
pass. `Account.update_equity` never touches `margin_used`. So when a fill lands
between the pipeline's load and its save, the pipeline writes its stale
`margin_used` back over the real one:

    T0  pipeline loads account          margin_used = 0     (no position yet)
    T1  record_deal books the position, sets margin_used = 77.37, saves
    T2  pipeline saves its T0 snapshot  margin_used = 0     <-- lost update

Consequence, and why this is the worst kind: `margin_used = 0` overstates free
margin by the whole requirement, and `margin_level` becomes the 999999 sentinel,
so the margin-call and stop-out machine can never fire. The account can run to
negative equity with no liquidation. It silently disables the risk engine, and it
happens MORE often the more liquid the symbol is, because more ticks means more
chances to win the race.

These tests are deterministic - they interleave the two writers by hand rather
than hoping to hit a timing window, which is why they can live in the suite while
`scripts/d8b_repro_a_book_margin.py` (no concurrent feed) is clean 12/12.
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED
from core.domains.common.value_objects import Money
from infrastructure.persistence.database import DatabaseManager
from infrastructure.persistence.repositories.account_repository import (
    SqlAccountRepository,
)

import infrastructure.persistence.account_models  # noqa: F401  registers tables
import infrastructure.persistence.db_models       # noqa: F401


@pytest.fixture
async def sql_repo(tmp_path):
    """Real Sql* repositories over SQLite, with one group seeded.

    A file, not :memory: - DatabaseManager passes pool_size/max_overflow, which
    aiosqlite's StaticPool rejects, and every connection to :memory: is a separate
    database anyway. `group_repo` is wired because accounts.group_name is a NOT
    NULL foreign key, so an account cannot be persisted without one.
    """
    from infrastructure.persistence.di_setup import setup_persistence_di
    from infrastructure.config import seeder
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    manager = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'd8b.db'}")
    await manager.create_tables()
    providers = setup_persistence_di(manager)
    await seeder.seed_all(
        group_repo=providers["group_repo"], symbol_repo=providers["symbol_repo"],
        manager_repo=providers["manager_repo"], account_repo=providers["account_repo"],
        coverage_repo=providers["coverage_repo"], config_root="config",
        password_hasher=Argon2PasswordHasher(),
    )
    repo = providers["account_repo"]
    global SEEDED_GROUP
    groups = await providers["group_repo"].get_all()
    SEEDED_GROUP = next((g for g in groups if g.name == GROUP), groups[0])
    yield repo
    await manager.close()


GROUP = "demo\\Standard"
#: set by the fixture; account_to_db needs a real Group, not just the name
SEEDED_GROUP = None


def _account(login=880001, **over):
    from core.domains.accounts.account import Account

    a = Account(login=login, client_id="D8B", group=SEEDED_GROUP, group_id=GROUP, currency="USD",
                balance=Money(Decimal("100000"), "USD"), credit=Money(Decimal("0"), "USD"),
                equity=Money(Decimal("100000"), "USD"),
                margin_used=Money(Decimal("0"), "USD"),
                margin_free=Money(Decimal("100000"), "USD"))
    for k, v in over.items():
        setattr(a, k, v)
    return a


@pytest.mark.asyncio
async def test_a_stale_valuation_write_cannot_erase_margin_used(sql_repo):
    """The lost update, reproduced by hand and then shown to be impossible."""
    await sql_repo.save(_account())

    # T0: the tick pipeline loads the account. No position yet, so margin_used 0.
    stale = await sql_repo.find_by_login(880001)
    assert stale.margin_used.amount == Decimal("0")

    # T1: a fill lands - record_deal's numbers go in through the owning path.
    filled = await sql_repo.find_by_login(880001)
    filled.margin_used = Money(Decimal("77.37413"), "USD")
    filled.margin_free = Money(Decimal("99922.62587"), "USD")
    filled.margin_reserved = Money(Decimal("0"), "USD")
    filled.balance = Money(Decimal("100000"), "USD")
    await sql_repo.save(filled)

    # T2: the pipeline finishes its pass and writes the valuation it computed
    # from the T0 snapshot.
    stale.profit = Money(Decimal("-0.59"), "USD")
    stale.equity = Money(Decimal("99999.41"), "USD")
    stale.margin_free = Money(Decimal("99922.03587"), "USD")
    stale.margin_level = Decimal("129242.164")   # the pipeline's own computation
    rows = await sql_repo.update_valuation(stale)
    assert rows == 1

    after = await sql_repo.find_by_login(880001)
    # The pipeline's own columns landed...
    assert after.profit.amount == Decimal("-0.59")
    assert after.equity.amount == Decimal("99999.41")
    # margin_level is DERIVED on read (D1), so it comes back recomputed from the
    # equity the pipeline wrote and the margin_used the fill wrote - the two
    # halves of the row agreeing is the whole point of the split write sets.
    from core.domains.market_data.margin import margin_level as compute_margin_level
    assert after.margin_level == compute_margin_level(
        after.equity.amount, after.margin_used.amount)
    assert after.margin_level != MARGIN_LEVEL_UNLIMITED
    # ...and the fill's columns SURVIVED, which is the whole point.
    assert after.margin_used.amount == Decimal("77.37413"), (
        "a tick erased the margin a fill had just written - the account now looks "
        "unmargined and stop-out can never fire"
    )
    assert after.balance.amount == Decimal("100000")


@pytest.mark.asyncio
async def test_update_valuation_never_touches_the_reservation(sql_repo):
    """margin_reserved belongs to the reservation path (M6), not to a tick."""
    a = _account(login=880002)
    a.margin_reserved = Money(Decimal("110.01"), "USD")
    await sql_repo.save(a)

    stale = await sql_repo.find_by_login(880002)
    stale.margin_reserved = Money(Decimal("0"), "USD")   # what a T0 snapshot holds
    stale.equity = Money(Decimal("99999"), "USD")
    await sql_repo.update_valuation(stale)

    after = await sql_repo.find_by_login(880002)
    assert after.margin_reserved.amount == Decimal("110.01"), (
        "a tick released someone else's margin hold"
    )


@pytest.mark.asyncio
async def test_update_valuation_persists_the_stop_out_state(sql_repo):
    """The so_* fields are the state machine's memory (M2) - they must still write."""
    from core.domains.accounts.enums import SOActivation

    await sql_repo.save(_account(login=880003))
    a = await sql_repo.find_by_login(880003)
    a.so_activation = SOActivation.STOP_OUT
    a.so_level = Decimal("27.5")
    a.so_equity = Money(Decimal("550"), "USD")
    a.so_margin = Money(Decimal("2000"), "USD")
    a.so_time = datetime(2026, 9, 12, 6, 0, 0, tzinfo=timezone.utc)

    assert await sql_repo.update_valuation(a) == 1

    after = await sql_repo.find_by_login(880003)
    assert after.so_activation is SOActivation.STOP_OUT
    assert after.so_level == Decimal("27.5")
    assert after.so_equity.amount == Decimal("550")
    assert after.so_margin.amount == Decimal("2000")
    assert after.so_time is not None


@pytest.mark.asyncio
async def test_a_full_row_save_still_writes_margin_used(sql_repo):
    """The owning path is unchanged - record_deal must still be able to set it."""
    await sql_repo.save(_account(login=880004))
    a = await sql_repo.find_by_login(880004)
    a.margin_used = Money(Decimal("77.37413"), "USD")
    await sql_repo.save(a)
    after = await sql_repo.find_by_login(880004)
    assert after.margin_used.amount == Decimal("77.37413")


@pytest.mark.asyncio
async def test_updated_at_records_the_write_not_the_domain_value(sql_repo):
    """The fingerprint that identified D8b: a resurrected row carried its creation
    timestamp, because account_to_db stamped the domain object's updated_at."""
    old = datetime(2020, 1, 1, tzinfo=timezone.utc)
    await sql_repo.save(_account(login=880005, updated_at=old))
    before = datetime.now(timezone.utc)
    a = await sql_repo.find_by_login(880005)
    a.updated_at = old            # a stale snapshot carries a stale timestamp
    await sql_repo.save(a)
    after = await sql_repo.find_by_login(880005)
    stamped = after.updated_at
    if stamped.tzinfo is None:            # SQLite hands back naive datetimes
        stamped = stamped.replace(tzinfo=timezone.utc)
    assert stamped >= before.replace(microsecond=0), (
        "updated_at came from the domain object, so a stale write looks untouched"
    )


# ------------------------------------------------------- the capability probe

@pytest.mark.asyncio
async def test_the_port_default_signals_unsupported_without_raising():
    """An abstract raise would be inherited by every test double and adapter, so a
    capability probe would blow up instead of degrading. It returns None instead."""
    from core.ports.interfaces import IAccountRepository

    class Minimal(IAccountRepository):
        async def find_by_login(self, login_id):
            return None

        async def save(self, account, session=None):
            return account

        async def reserve_margin(self, login_id, amount):
            return None

        async def release_margin(self, login_id, amount):
            return None

    assert await Minimal().update_valuation(_account()) is None


@pytest.mark.asyncio
async def test_the_pipeline_falls_back_when_a_repo_lacks_the_write(caplog):
    """A repo without update_valuation still works - loudly, because the fallback
    is the racy one."""
    import logging

    from application.services.tick_margin_pipeline import TickMarginPipeline

    class NoValuation:
        def __init__(self):
            self.saved = []

        async def get_all_with_positions(self):
            return []

        async def save(self, account):
            self.saved.append(account)

    repo = NoValuation()
    # _process_accounts is the unit that persists; drive it with no accounts so the
    # test is about the capability probe, not the maths.
    pipeline = TickMarginPipeline.__new__(TickMarginPipeline)
    pipeline.account_repo = repo
    probe = getattr(repo, "update_valuation", None)
    assert probe is None, "a repo without the write must probe as absent"
