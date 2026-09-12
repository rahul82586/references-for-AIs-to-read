"""
M2 acceptance tests: configuration can enter the system, and it stays MT5-exact.

Runs against SQLite so it works in CI without a PostgreSQL service. The one accommodation
that requires is compiling postgresql.JSONB to JSON on SQLite; production runs
PostgreSQL, where JSONB is native and indexable.
"""

from __future__ import annotations

import os
import pathlib
from decimal import Decimal

import pytest
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles


@compiles(JSONB, "sqlite")
def _compile_jsonb_on_sqlite(type_, compiler, **kw):  # noqa: ANN001
    """Let the JSONB columns create on SQLite. Test-harness only."""
    return "JSON"


from core.domains.accounts.enums import AccountType, MarginMode, SOActivation  # noqa: E402
from core.domains.common.value_objects import Money  # noqa: E402
from core.domains.identity.models import ManagerRole  # noqa: E402
from core.domains.instruments.enums import CalculationMode  # noqa: E402
from infrastructure.config import loader, seeder  # noqa: E402
from infrastructure.config.loader import ConfigError  # noqa: E402
from infrastructure.mt5 import wire  # noqa: E402
from infrastructure.persistence.config_mappers import (  # noqa: E402
    group_mt5_record,
    symbol_mt5_record,
)
from infrastructure.persistence.database import Base, DatabaseManager  # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402  (registers every table)
from infrastructure.persistence.di_setup import setup_persistence_di  # noqa: E402

FIXTURES = pathlib.Path(
    os.environ.get("BROKER_MT5_FIXTURES", "")
    or pathlib.Path(__file__).resolve().parents[4] / "decoded" / "mt5-format-structure"
)
CONFIG_ROOT = pathlib.Path(__file__).resolve().parents[3] / "config"

requires_fixtures = pytest.mark.skipif(
    not FIXTURES.is_dir(), reason=f"MT5 export fixtures not found at {FIXTURES}"
)


class _NullEventBus:
    """Minimal IEventBus. Registration is synchronous, as the contract now requires."""

    def __init__(self) -> None:
        self.published: list = []
        self.subscribed: list = []

    async def publish(self, event) -> None:
        self.published.append(event)

    def subscribe(self, channel, handler):
        self.subscribed.append(channel)
        return None

    def unsubscribe(self, channel, handler) -> None:
        pass

    async def disconnect(self) -> None:
        pass


@pytest.fixture
async def providers(tmp_path):
    manager = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    await manager.create_tables()
    wired = setup_persistence_di(manager)
    wired["event_bus"] = _NullEventBus()
    yield wired
    await manager.close()


async def _seed(wired, **kwargs):
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    return await seeder.seed_all(
        group_repo=wired["group_repo"],
        symbol_repo=wired["symbol_repo"],
        manager_repo=wired["manager_repo"],
        account_repo=wired["account_repo"],
        config_root=CONFIG_ROOT,
        password_hasher=Argon2PasswordHasher(),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Loader strictness
# ---------------------------------------------------------------------------


def test_loader_accepts_the_shipped_group_config():
    groups = loader.load_groups(CONFIG_ROOT / "groups" / "default_groups.yaml")
    assert len(groups) == 7
    names = {g.name for g in groups}
    assert "real" + chr(92) + "real" in names
    assert "demo" + chr(92) + "Standard" in names


def test_loader_accepts_the_shipped_symbol_config():
    symbols = loader.load_symbols(CONFIG_ROOT / "symbols" / "instruments.yaml")
    assert len(symbols) == 5
    by_name = {s.name: s for s in symbols}
    # The nested category headings in the YAML are flattened; the symbol name wins.
    assert set(by_name) == {"EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"}


def test_loader_rejects_fraction_margin_thresholds(tmp_path):
    """0.8 / 0.5 was the bug: percent margin levels compared against fractions."""
    path = tmp_path / "groups.yaml"
    path.write_text(
        "g:\n  name: 'real" + chr(92) + "real'\n  margin:\n    margin_call_level: 0.8\n"
    )
    with pytest.raises(ConfigError, match="FRACTION"):
        loader.load_groups(path)


def test_loader_accepts_a_legitimate_one_percent_stop_out(tmp_path):
    """13 of the 20 groups on the reference server use MarginStopOut 1.00.

    A blanket "<= 1 is a fraction" rule would reject a real broker configuration, so
    only the specific fraction literals this codebase used are rejected.
    """
    path = tmp_path / "groups.yaml"
    path.write_text(
        "g:\n  name: 'demo" + chr(92) + "Standard'\n  margin:\n"
        "    margin_call_level: 10\n    stop_out_level: 1\n"
    )
    groups = loader.load_groups(path)
    assert groups[0].margin.stop_out_level == Decimal("1")


def test_loader_rejects_unknown_keys(tmp_path):
    """Tolerating unknown keys is how a config drifts into running on defaults."""
    path = tmp_path / "groups.yaml"
    path.write_text("g:\n  name: 'real" + chr(92) + "real'\n  leverage: 100\n")
    with pytest.raises(ConfigError, match="unknown key"):
        loader.load_groups(path)


def test_loader_rejects_the_flat_pre_m1_group_shape(tmp_path):
    path = tmp_path / "groups.yaml"
    path.write_text("g:\n  name: 'real" + chr(92) + "real'\n  margin_call_level: 80\n")
    # The unknown-key check fires first, which is the more useful message: it names the
    # offending key and lists every valid one.
    with pytest.raises(ConfigError, match="margin_call_level"):
        loader.load_groups(path)


def test_loader_rejects_the_pre_m1_symbol_shape(tmp_path):
    path = tmp_path / "symbols.yaml"
    path.write_text(
        "s:\n  name: EURUSD\n  precision: 5\n  margins:\n    initial_percent: 1.0\n"
    )
    with pytest.raises(ConfigError, match="margins"):
        loader.load_symbols(path)


def test_loader_rejects_a_non_positive_point(tmp_path):
    """MT5's Point is always populated; TickSize is the field that is often zero."""
    path = tmp_path / "symbols.yaml"
    path.write_text("s:\n  name: EURUSD\n  tick_size: 0\n")
    with pytest.raises(ConfigError, match="must be positive"):
        loader.load_symbols(path)


def test_loader_rejects_an_unmappable_enum(tmp_path):
    path = tmp_path / "symbols.yaml"
    path.write_text("s:\n  name: EURUSD\n  calc_mode: NOT_A_MODE\n")
    with pytest.raises(ConfigError, match="not a valid CalculationMode"):
        loader.load_symbols(path)


def test_loader_accepts_enum_names_and_mt5_integers(tmp_path):
    """MT5 stores integers; a hand-written YAML naturally says MARKET."""
    for value, expected in [("MARKET", 2), (2, 2), ("2", 2)]:
        path = tmp_path / f"symbols-{value}.yaml"
        path.write_text(f"s:\n  name: EURUSD\n  exec_mode: {value}\n")
        symbol = loader.load_symbols(path)[0]
        assert int(symbol.exec_mode.value) == expected


def test_loader_rejects_duplicate_names(tmp_path):
    path = tmp_path / "symbols.yaml"
    path.write_text("a:\n  name: EURUSD\nb:\n  name: EURUSD\n")
    with pytest.raises(ConfigError, match="duplicate symbol name"):
        loader.load_symbols(path)


# ---------------------------------------------------------------------------
# Seeding from YAML
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_seed_populates_groups_symbols_and_first_admin(providers):
    report = await _seed(providers)

    assert report.groups_created == 7
    assert report.symbols_created == 5
    assert report.admin_created is True
    assert report.admin_login == seeder.FIRST_ADMIN_LOGIN

    groups = await providers["group_repo"].get_all()
    symbols = await providers["symbol_repo"].get_all_symbols()
    managers = await providers["manager_repo"].find_all()
    assert len(groups) == 7
    assert len(symbols) == 5
    assert len(managers) == 1

    # The password was hashed, not stored, and is not in the serialised report.
    admin = managers[0]
    assert admin.login == str(seeder.FIRST_ADMIN_LOGIN)
    assert admin.role is ManagerRole.SUPER_ADMIN
    assert admin.password_hash and "PLAINTEXT" not in admin.password_hash
    assert admin.must_change_password is True
    assert "admin_password" not in report.as_dict()
    assert report.admin_password and len(report.admin_password) >= 7


@pytest.mark.asyncio
async def test_seed_is_idempotent(providers):
    first = await _seed(providers)
    second = await _seed(providers)

    assert first.groups_created == 7
    assert second.groups_created == 0
    assert second.symbols_created == 0
    assert second.admin_created is False

    groups = await providers["group_repo"].get_all()
    symbols = await providers["symbol_repo"].get_all_symbols()
    managers = await providers["manager_repo"].find_all()
    assert len(groups) == 7
    assert len(symbols) == 5
    assert len(managers) == 1


@pytest.mark.asyncio
async def test_seeded_thresholds_are_percent(providers):
    await _seed(providers)
    groups = {g.name: g for g in await providers["group_repo"].get_all()}

    real = groups["real" + chr(92) + "real"]
    assert real.margin.margin_call_level == Decimal("50")
    assert real.margin.stop_out_level == Decimal("30")
    assert real.margin.mode is MarginMode.RETAIL_HEDGED
    assert real.account_type is AccountType.REAL

    demo = groups["demo" + chr(92) + "Standard"]
    assert demo.account_type is AccountType.DEMO
    assert demo.margin.margin_call_level == Decimal("10")
    assert demo.margin.stop_out_level == Decimal("1")

    coverage = groups["coverage" + chr(92) + "house"]
    assert coverage.account_type is AccountType.COVERAGE


@pytest.mark.asyncio
async def test_account_type_is_derived_from_the_group_path(providers):
    await _seed(providers)
    groups = {g.name: g for g in await providers["group_repo"].get_all()}
    assert groups["preliminary"].account_type is AccountType.PRELIMINARY
    # The path prefix says demo, but the YAML states CONTEST explicitly, and the
    # explicit value must win.
    assert groups["demo" + chr(92) + "Challenge"].account_type is AccountType.CONTEST


@pytest.mark.asyncio
async def test_coverage_account_is_created(providers):
    report = await _seed(providers)
    assert report.coverage_accounts == 1
    accounts = await providers["account_repo"].find_all()
    assert len(accounts) == 1
    assert accounts[0].account_type is AccountType.COVERAGE
    assert accounts[0].group.name == "coverage" + chr(92) + "house"


@pytest.mark.asyncio
async def test_stop_out_state_survives_persistence(providers):
    """The old 14-column AccountModel dropped all five so_* fields on every save.

    That made the state machine restart from NONE on each tick, so MarginCallEntered
    fired forever and StopOutExited was unreachable.
    """
    await _seed(providers)
    account = (await providers["account_repo"].find_all())[0]

    account.so_activation = SOActivation.STOP_OUT
    account.so_level = Decimal("27.5")
    account.so_equity = Money(Decimal("550"), account.currency)
    account.so_margin = Money(Decimal("2000"), account.currency)
    # D1: margin_level is DERIVED state, not stored state - unlike the five
    # so_* fields this test exists to protect, which are the stop-out machine's
    # real memory. 550 / 2000 * 100 = 27.5, so setting the inputs and asserting
    # the output pins the derivation instead of the column.
    account.equity = Money(Decimal("550"), account.currency)
    account.margin_used = Money(Decimal("2000"), account.currency)
    account.margin_level = Decimal("27.5")
    account.color_tag = "red"
    await providers["account_repo"].save(account)

    reloaded = await providers["account_repo"].find_by_login(str(account.login))
    assert reloaded.so_activation is SOActivation.STOP_OUT
    assert reloaded.so_level == Decimal("27.5")
    assert reloaded.so_equity.amount == Decimal("550")
    assert reloaded.margin_level == Decimal("27.5")
    assert reloaded.color_tag == "red"


@pytest.mark.asyncio
async def test_a_stale_margin_level_column_is_never_served(providers):
    """D1: the column is written for external SQL consumers but the domain
    object never trusts it. Before the fix a defaulted 0 was served to clients
    and fed to the routing engine as a real comparison value.
    """
    await _seed(providers)
    account = (await providers["account_repo"].find_all())[0]
    account.equity = Money(Decimal("9999"), account.currency)
    account.margin_used = Money(Decimal("107.978"), account.currency)
    account.margin_level = Decimal("0")  # deliberately stale / wrong
    await providers["account_repo"].save(account)

    reloaded = await providers["account_repo"].find_by_login(str(account.login))
    assert reloaded.margin_level == (Decimal("9999") / Decimal("107.978")) * Decimal("100")
    assert reloaded.margin_level != Decimal("0")


@pytest.mark.asyncio
async def test_config_cache_initialize_finds_the_methods_it_calls(providers):
    """ConfigCache.initialize() calls get_all() and find_all(); neither used to exist."""
    from application.cache.config_cache import ConfigCache

    await _seed(providers)
    cache = ConfigCache(
        group_repo=providers["group_repo"],
        account_repo=providers["account_repo"],
        symbol_repo=providers["symbol_repo"],
        holiday_repo=providers["holiday_repo"],
        position_repo=providers["position_repo"],
        event_bus=providers["event_bus"],
    )
    await cache.initialize()

    assert len(cache.get_all_groups()) == 7
    assert len(cache.get_all_symbols()) == 5
    assert cache.get_symbol("EURUSD") is not None
    assert cache.get_symbol("EURUSD").tick_size == Decimal("0.00001")


@pytest.mark.asyncio
async def test_cache_invalidation_actually_subscribes(providers):
    """subscribe() was async and ConfigCache never awaited it, so this list was empty."""
    from application.cache.config_cache import ConfigCache

    bus = providers["event_bus"]
    cache = ConfigCache(
        group_repo=providers["group_repo"],
        account_repo=providers["account_repo"],
        symbol_repo=providers["symbol_repo"],
        holiday_repo=providers["holiday_repo"],
        position_repo=providers["position_repo"],
        event_bus=bus,
    )
    await cache.initialize()
    assert bus.subscribed, "ConfigCache registered no event handlers at all"
    assert len(bus.subscribed) >= 9


# ---------------------------------------------------------------------------
# Seeding from a real MT5 server export
# ---------------------------------------------------------------------------


@requires_fixtures
@pytest.mark.asyncio
async def test_a_whole_real_mt5_server_can_be_seeded(providers):
    """20 groups and 362 symbols off a live server, into the database."""
    report = await _seed(
        providers,
        mt5_groups=FIXTURES / "Groups TCTrader-Live.json",
        mt5_symbols=FIXTURES / "Symbols TCTrader-Live.json",
    )

    groups = await providers["group_repo"].get_all()
    symbols = await providers["symbol_repo"].get_all_symbols()

    # 20 from MT5 plus coverage\house from the YAML, which MT5 does not have.
    assert len(groups) == 21
    assert len(symbols) == 362
    assert report.admin_created is True


@requires_fixtures
@pytest.mark.asyncio
async def test_seeded_mt5_symbols_keep_point_and_ticksize_apart(providers):
    await _seed(providers, mt5_symbols=FIXTURES / "Symbols TCTrader-Live.json")
    symbols = {s.name: s for s in await providers["symbol_repo"].get_all_symbols()}

    btc = symbols["BTCUSD"]
    assert btc.tick_size == Decimal("1.00000000")
    assert btc.mt5_tick_size == Decimal("0")
    assert btc.digits == 0
    assert btc.contract_size == Decimal("1.00000000")
    # CalcMode 5 is FOREX_NO_LEVERAGE. The pre-M1 enum read it as STOCKS.
    assert btc.calc_mode is CalculationMode.FOREX_NO_LEVERAGE

    ada = symbols["ADAUSD"]
    assert ada.tick_size == Decimal("0.00001000")
    assert ada.mt5_tick_size == Decimal("0.00000")


@requires_fixtures
@pytest.mark.asyncio
async def test_seeded_mt5_groups_reexport_field_identically(providers):
    """The M1 guarantee, now held through a real database write and read."""
    await _seed(providers, mt5_groups=FIXTURES / "Groups TCTrader-Live.json")
    original = {
        r["Group"]: r
        for r in wire.records(
            wire.decode_file(FIXTURES / "Groups TCTrader-Live.json"), "ConfigGroups"
        )
    }

    repo = providers["group_repo"]
    checked = 0
    for name, raw in original.items():
        row = await repo.find_row_by_name(name)
        assert row is not None, f"{name} was not persisted"
        out = group_mt5_record(row)
        differing = {k: (raw[k], out.get(k)) for k in raw if out.get(k) != raw[k]}
        assert not differing, f"{name}: {list(differing.items())[:3]}"
        checked += 1
    assert checked == 20


@requires_fixtures
@pytest.mark.asyncio
async def test_seeded_mt5_symbols_reexport_field_identically(providers):
    await _seed(providers, mt5_symbols=FIXTURES / "Symbols TCTrader-Live.json")
    original = {
        r["Symbol"]: r
        for r in wire.records(
            wire.decode_file(FIXTURES / "Symbols TCTrader-Live.json"), "ConfigSymbols"
        )
    }

    repo = providers["symbol_repo"]
    checked = 0
    for name, raw in original.items():
        row = await repo.find_row_by_name(name)
        assert row is not None, f"{name} was not persisted"
        out = symbol_mt5_record(row)
        differing = {k for k in raw if out.get(k) != raw[k]}
        assert not differing, f"{name}: {sorted(differing)[:4]}"
        checked += 1
    assert checked == 362


# ---------------------------------------------------------------------------
# Manager rights
# ---------------------------------------------------------------------------


def test_rights_masks_survive_a_full_128_right_administrator():
    """128 rights do not fit in two signed 64-bit words; they need three."""
    from infrastructure.persistence.account_models import masks_to_rights, rights_to_masks

    rights = ["1"] * 128
    masks = rights_to_masks(rights)
    assert len(masks) == 3
    for mask in masks:
        assert mask.bit_length() <= 63, f"mask {mask} would overflow a signed BigInteger"
    assert masks_to_rights(masks) == rights


def test_rights_masks_round_trip_every_single_right():
    from infrastructure.persistence.account_models import masks_to_rights, rights_to_masks

    for index in range(128):
        rights = ["0"] * 128
        rights[index] = "1"
        assert masks_to_rights(rights_to_masks(rights)) == rights, f"right {index} lost"


def test_generated_password_meets_mt5_length_bounds():
    for _ in range(50):
        password = seeder.generate_password()
        assert 7 <= len(password) <= 64
        assert password.isalnum()


@requires_fixtures
@pytest.mark.asyncio
async def test_seeded_mt5_groups_keep_their_trade_flags(providers):
    """TradeFlags 215 came back as 15: the loader dropped it and the default won.

    MT5's EnTradeFlags bits are real trading permissions - SO_COMPENSATION allows
    negative-balance compensation after a stop-out, HEDGE_PROHIBIT forbids hedged
    positions. Losing them silently changes what clients are allowed to do.
    """
    await _seed(providers, mt5_groups=FIXTURES / "Groups TCTrader-Live.json")
    original = {
        r["Group"]: int(r["TradeFlags"])
        for r in wire.records(
            wire.decode_file(FIXTURES / "Groups TCTrader-Live.json"), "ConfigGroups"
        )
    }
    groups = {g.name: g for g in await providers["group_repo"].get_all()}
    for name, flags in original.items():
        assert int(groups[name].trade_flags) == flags, f"{name}: {flags} became {int(groups[name].trade_flags)}"


def test_explicit_account_type_beats_the_group_path_prefix():
    """demo\Challenge is a CONTEST group; coverage\house is a COVERAGE account."""
    contest = loader.parse_group(
        {"name": "demo" + chr(92) + "Challenge", "account_type": "CONTEST"}, "test"
    )
    assert contest.account_type is AccountType.CONTEST

    derived = loader.parse_group({"name": "demo" + chr(92) + "Standard"}, "test")
    assert derived.account_type is AccountType.DEMO
