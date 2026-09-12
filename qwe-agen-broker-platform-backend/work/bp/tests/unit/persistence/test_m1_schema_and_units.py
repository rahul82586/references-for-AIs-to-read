"""
M1 acceptance tests: one schema, one margin unit, MT5-aligned configuration models.

These are the tests that would have caught the defects M1 fixes. Each one asserts a
decision, not an implementation detail, so they stay meaningful as the code evolves.
"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED, Account
from core.domains.accounts.enums import AccountType, MarginMode, TradeFlags
from core.domains.accounts.group import Group
from core.domains.accounts.value_objects import (
    CommissionRule,
    GroupPermissions,
    GroupSymbolOverride,
    MarginProfile,
    RoutingRule,
    SwapConfiguration,
)
from core.domains.instruments.enums import CalculationMode, SwapMode, TradeMode
from core.domains.instruments.symbol import Symbol
from core.domains.instruments.value_objects import MarginRates, QuoteSession, TradingSession
from core.domains.risk.engine import RiskEngine
from core.domains.risk.models import MarginSnapshot, RiskStatus
from infrastructure.mt5 import enums as mt5enums
from infrastructure.mt5 import fieldmap
from infrastructure.mt5.codec import domain_to_record, record_to_domain
from infrastructure.persistence.config_mappers import (
    db_to_group,
    db_to_symbol,
    group_to_db,
    symbol_to_db,
)
from infrastructure.persistence.config_models import GroupModel, SymbolModel
from infrastructure.persistence.database import Base


# ---------------------------------------------------------------------------
# One schema
# ---------------------------------------------------------------------------


def test_there_is_exactly_one_declarative_base():
    """Two DeclarativeBase classes means two disjoint metadata registries.

    DatabaseManager.create_tables() used one and alembic/env.py the other, so the dev
    shortcut and the migration path created different schemas.
    """
    import infrastructure.persistence.config_models as config_models
    import infrastructure.persistence.db_models as db_models
    from infrastructure.persistence.database import Base as DatabaseBase

    assert db_models.Base is DatabaseBase
    assert config_models.Base is DatabaseBase


def test_every_table_is_registered_on_the_single_metadata():
    tables = set(Base.metadata.tables)
    expected = {
        "accounts",
        "balance_operations",
        "bars",
        "coverage_accounts",
        "deals",
        "domain_events",
        "groups",
        "holidays",
        "orders",
        "positions",
        "routing_rules",
        "symbols",
    }
    assert expected <= tables, f"missing tables: {expected - tables}"


def test_no_duplicate_tablename_across_models():
    """The DealModel/PositionModel shadowing bug, expressed as a schema invariant."""
    seen: dict[str, str] = {}
    for mapper in Base.registry.mappers:
        table = getattr(mapper.class_, "__tablename__", None)
        if not table:
            continue
        if table in seen:
            pytest.fail(f"__tablename__ {table!r} defined by both {seen[table]} and {mapper.class_.__name__}")
        seen[table] = mapper.class_.__name__


def test_alembic_revision_graph_is_resolvable():
    """The deleted migration.py had prose instead of revision variables."""
    import importlib.util
    import pathlib

    versions = pathlib.Path(__file__).resolve().parents[3] / "alembic" / "versions"
    found = []
    for path in sorted(versions.glob("*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "revision"), f"{path.name} has no `revision`"
        assert hasattr(module, "down_revision"), f"{path.name} has no `down_revision`"
        assert isinstance(module.revision, str) and module.revision, (
            f"{path.name} has an empty revision id"
        )
        found.append((module.revision, module.down_revision))

    assert found, "no migrations found"
    roots = [r for r, d in found if d is None]
    assert len(roots) == 1, f"expected exactly one graph root, got {roots}"


def test_generated_migration_covers_every_model_table():
    """The migration is generated from the models, so it cannot drift from them."""
    import pathlib
    import re

    versions = pathlib.Path(__file__).resolve().parents[3] / "alembic" / "versions"
    text = "".join(p.read_text(encoding="utf-8") for p in versions.glob("*.py"))
    created = set(re.findall(r"op\.create_table\(\s*['\"](\w+)['\"]", text))
    missing = set(Base.metadata.tables) - created
    assert not missing, f"migration does not create: {sorted(missing)}"


def test_group_model_has_no_fraction_scale_columns():
    """DECIMAL(5,4) could not hold a percent; that column type was the old fraction schema."""
    for name in ("margin_call", "margin_stop_out"):
        column = GroupModel.__table__.columns[name]
        assert column.type.scale <= 2, f"{name} scale {column.type.scale} suggests fractions"
        assert column.type.precision >= 5, f"{name} precision {column.type.precision} too small for percent"


def test_point_and_tick_size_are_distinct_columns():
    """MT5's Point and TickSize differ on all 362 reference symbols; neither may shadow the other."""
    columns = SymbolModel.__table__.columns
    assert "point" in columns
    assert "mt5_tick_size" in columns
    assert "tick_size" not in columns, (
        "an unqualified tick_size column is exactly the ambiguity that let Point and "
        "TickSize be merged"
    )


def test_symbol_model_carries_the_full_16_way_margin_matrix():
    columns = set(SymbolModel.__table__.columns.keys())
    for name in MarginRates.__dataclass_fields__:
        assert f"margin_{name}" in columns, f"missing column margin_{name}"


def test_stale_schema_sources_are_gone():
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[3]
    assert not (root / "ops" / "docker" / "init.sql").exists(), (
        "init.sql created a UUID-PK fraction-scale groups table that contradicted the model"
    )
    assert not (root / "alembic" / "versions" / "migration.py").exists(), (
        "migration.py had no revision variables, so alembic could not build a graph"
    )


# ---------------------------------------------------------------------------
# One margin unit: PERCENT
# ---------------------------------------------------------------------------


def _decode_sessions(days, cls):
    """MT5 Sunday-first per-day sessions -> flat domain session objects."""
    out = []
    for day in days or []:
        index = int(day.get("index", 0))
        for entry in day.get("sessions") or []:
            out.append(
                cls(
                    day_of_week=index,
                    open_minutes=int(entry.get("open_minutes", 0)),
                    close_minutes=int(entry.get("close_minutes", 0)),
                )
            )
    return out


def _account(equity: str, margin: str, call: str = "80", stop: str = "50") -> Account:
    from core.domains.common.value_objects import Money

    group = Group(
        id="g",
        name="real\\real",
        account_type=AccountType.REAL,
        currency="USD",
        margin=MarginProfile(
            margin_call_level=Decimal(call), stop_out_level=Decimal(stop)
        ),
    )
    account = Account(
        login="100001",
        group=group,
        currency="USD",
        balance=Money(Decimal("10000"), "USD"),
        equity=Money(Decimal(equity), "USD"),
        margin_used=Money(Decimal(margin), "USD"),
    )
    return account


def test_margin_profile_defaults_are_percent():
    profile = MarginProfile()
    assert profile.margin_call_level == Decimal("80")
    assert profile.stop_out_level == Decimal("50")
    assert profile.margin_call_level > Decimal("1"), (
        "a threshold <= 1 is a fraction, and fractions are the bug this test guards"
    )


def test_recompute_margin_level_is_the_only_formula_and_returns_percent():
    account = _account(equity="10000", margin="25000")
    assert account.recompute_margin_level() == Decimal("40")
    assert account.margin_level == Decimal("40")


def test_recompute_margin_level_with_no_margin_returns_the_sentinel_not_zero():
    """Zero would read as 'fully exhausted' and trigger an immediate stop-out."""
    account = _account(equity="10000", margin="0")
    assert account.recompute_margin_level() == MARGIN_LEVEL_UNLIMITED


def test_margin_call_fires_at_40_percent_with_mt5_thresholds():
    """The exact scenario that used to report no margin call and no stop-out."""
    account = _account(equity="10000", margin="25000", call="50", stop="30")
    account.recompute_margin_level()
    assert account.margin_level == Decimal("40")

    events = [e["event_type"] for e in account.evaluate_margin_state()]
    assert "MarginCallEntered" in events

    engine = RiskEngine()
    snapshot = MarginSnapshot(
        account_login="100001",
        balance=Decimal("10000"),
        equity=Decimal("10000"),
        margin_used=Decimal("25000"),
        margin_free=Decimal("-15000"),
        margin_level=Decimal("40"),
        status=RiskStatus.NORMAL,
    )
    assert engine.detect_margin_call(account, snapshot) is True


def test_stop_out_fires_at_25_percent_with_mt5_thresholds():
    account = _account(equity="5000", margin="20000", call="50", stop="30")
    account.recompute_margin_level()
    assert account.margin_level == Decimal("25")

    engine = RiskEngine()
    snapshot = MarginSnapshot(
        account_login="100001",
        balance=Decimal("5000"),
        equity=Decimal("5000"),
        margin_used=Decimal("20000"),
        margin_free=Decimal("-15000"),
        margin_level=Decimal("25"),
        status=RiskStatus.MARGIN_CALL,
    )
    assert engine.detect_stop_out(account, snapshot) is True


def test_healthy_account_fires_neither():
    account = _account(equity="100000", margin="25000", call="50", stop="30")
    account.recompute_margin_level()
    assert account.margin_level == Decimal("400")
    assert account.evaluate_margin_state() == []


def test_detect_margin_call_no_longer_raises_attribute_error():
    """It used to read group.margin_call_level; the field is group.margin.margin_call_level."""
    account = _account(equity="10000", margin="25000")
    engine = RiskEngine()
    snapshot = MarginSnapshot(
        account_login="100001",
        balance=Decimal("10000"),
        equity=Decimal("10000"),
        margin_used=Decimal("25000"),
        margin_free=Decimal("-15000"),
        margin_level=Decimal("40"),
        status=RiskStatus.NORMAL,
    )
    engine.detect_margin_call(account, snapshot)
    engine.detect_stop_out(account, snapshot)


def test_settings_yaml_thresholds_are_percent():
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[3]
    text = (root / "config" / "settings.yaml").read_text(encoding="utf-8")
    assert "margin_call_level: 0.8" not in text
    assert "stop_out_level: 0.5" not in text


# ---------------------------------------------------------------------------
# MT5-accurate enums
# ---------------------------------------------------------------------------


def test_calculation_mode_values_match_the_mt5_headers():
    assert CalculationMode.FOREX.value == 0
    assert CalculationMode.FUTURES.value == 1
    assert CalculationMode.CFD.value == 2
    assert CalculationMode.CFD_INDEX.value == 3
    assert CalculationMode.CFD_LEVERAGE.value == 4
    assert CalculationMode.FOREX_NO_LEVERAGE.value == 5
    assert CalculationMode.EXCHANGE_STOCKS.value == 32
    assert CalculationMode.SERV_COLLATERAL.value == 64


def test_calculation_mode_no_longer_has_the_asset_class_values():
    """BONDS/STOCKS/CRYPTO/METALS/ENERGY were an asset taxonomy, not MT5 calc modes."""
    for gone in ("BONDS", "STOCKS", "CRYPTO", "METALS", "ENERGY", "OPTIONS", "INDICES"):
        assert not hasattr(CalculationMode, gone), f"CalculationMode.{gone} should be gone"


def test_swap_mode_values_match_the_mt5_headers():
    assert SwapMode.POINTS.value == 1
    assert SwapMode.SYMBOL_CURRENCY.value == 2
    assert SwapMode.MARGIN_CURRENCY.value == 3
    assert SwapMode.GROUP_CURRENCY.value == 4
    assert SwapMode.INTEREST_CURRENT.value == 5
    assert SwapMode.PROFIT_CURRENCY.value == 9


def test_order_type_flags_is_a_bitmask_with_mt5_bit_values():
    from core.domains.instruments.enums import OrderTypeFlags

    assert OrderTypeFlags.MARKET.value == 1
    assert OrderTypeFlags.LIMIT.value == 2
    assert OrderTypeFlags.STOP.value == 4
    assert OrderTypeFlags.STOP_LIMIT.value == 8
    assert OrderTypeFlags.SL.value == 16
    assert OrderTypeFlags.TP.value == 32
    assert OrderTypeFlags.CLOSEBY.value == 64
    combined = OrderTypeFlags.MARKET | OrderTypeFlags.LIMIT | OrderTypeFlags.CLOSEBY
    assert int(combined) == 67


def test_symbol_defaults_to_the_full_order_flags_bitmask():
    """All 362 symbols in the reference export carry 127."""
    symbol = Symbol(name="EURUSD", path="FX\\Forex\\EURUSD")
    assert int(symbol.order_flags) == 127


def test_default_symbol_has_a_usable_calc_mode_and_trade_mode():
    symbol = Symbol(name="EURUSD", path="FX\\Forex\\EURUSD")
    assert symbol.calc_mode is CalculationMode.FOREX
    assert symbol.trade_mode is TradeMode.FULL


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


def test_trading_session_open_time_and_is_within_work():
    """Both raised AttributeError: the field is open_minutes, the code read open_minute."""
    from datetime import time

    session = TradingSession(day_of_week=2, open_minutes=230, close_minutes=630)
    assert session.open_time == time(3, 50)
    assert session.close_time == time(10, 30)
    assert session.is_within(time(4, 0)) is True
    assert session.is_within(time(11, 0)) is False


def test_trading_session_close_of_1440_clamps_instead_of_raising():
    from datetime import time

    session = TradingSession(open_minutes=0, close_minutes=1440)
    assert session.close_time == time(23, 59, 59)
    assert session.is_within(time(12, 0)) is True


def test_overnight_session_wraps_past_midnight():
    from datetime import time

    session = TradingSession(open_minutes=22 * 60, close_minutes=6 * 60)
    assert session.is_within(time(23, 0)) is True
    assert session.is_within(time(5, 0)) is True
    assert session.is_within(time(12, 0)) is False


# ---------------------------------------------------------------------------
# Codec-routed mappers: domain -> row -> domain, and MT5 -> row -> MT5
# ---------------------------------------------------------------------------


def _sample_group() -> Group:
    return Group(
        id="grp-1",
        name="real\\real",
        server_id=1,
        account_type=AccountType.REAL,
        currency="USD",
        margin=MarginProfile(
            mode=MarginMode.RETAIL_HEDGED,
            margin_call_level=Decimal("50"),
            stop_out_level=Decimal("30"),
            leverage_default=100,
            leverage_max=500,
        ),
        commissions=[
            CommissionRule(
                name="Forex",
                symbol_pattern="FX\\*",
                currency="USD",
                value=Decimal("3.5"),
                min_value=Decimal("0"),
            )
        ],
        symbol_overrides=[
            GroupSymbolOverride(
                symbol_pattern="FX\\Forex\\EURUSD",
                spread_diff=2,
                swap_long=Decimal("-7.9"),
                swap_short=Decimal("-0.83"),
            )
        ],
        limit_orders=200,
        limit_positions=200,
        limit_symbols=100,
        routing=RoutingRule(default_mode="b_book", lp_priority=["LMAX", "Centroid"]),
        permissions=GroupPermissions(allowed_symbols=["FX\\*"], allow_hedging=True),
        swaps=SwapConfiguration(swap_long=Decimal("-7.9"), swap_short=Decimal("-0.83")),
    )


def test_group_round_trips_through_the_database_model():
    original = _sample_group()
    row = group_to_db(original)
    restored = db_to_group(row)

    assert restored.name == original.name
    assert restored.id == original.id
    assert restored.currency == original.currency
    assert restored.account_type is AccountType.REAL
    # PERCENT survives the trip, and stays percent.
    assert restored.margin.margin_call_level == Decimal("50")
    assert restored.margin.stop_out_level == Decimal("30")
    assert restored.margin.mode is MarginMode.RETAIL_HEDGED
    assert restored.margin.leverage_default == 100
    assert restored.limit_orders == 200
    assert restored.routing.default_mode == "b_book"
    assert restored.routing.lp_priority == ["LMAX", "Centroid"]
    assert restored.permissions.allowed_symbols == ["FX\\*"]
    assert restored.swaps.swap_long == Decimal("-7.9")
    assert len(restored.commissions) == 1
    assert restored.commissions[0].symbol_pattern == "FX\\*"
    assert len(restored.symbol_overrides) == 1
    assert restored.symbol_overrides[0].spread_diff == 2


def test_account_type_is_derived_from_the_mt5_group_path():
    for path, expected in [
        ("real\\real", AccountType.REAL),
        ("real\\real-SF", AccountType.REAL),
        ("demo\\Standard", AccountType.DEMO),
        ("demo\\Challenge", AccountType.DEMO),
        ("managers\\dealers", AccountType.MANAGER),
        ("managers\\administrators", AccountType.MANAGER),
        ("preliminary", AccountType.PRELIMINARY),
    ]:
        assert mt5enums.account_type_from_group_path(path) is expected, path


def test_group_row_exports_to_mt5_wire_format_with_percent_thresholds():
    """The whole point of routing mappers through the codec: the row IS the MT5 record."""
    from infrastructure.mt5 import wire
    from infrastructure.persistence import config_mappers

    row = group_to_db(_sample_group())
    domain = config_mappers.db_to_group(row)
    # group_mt5_record IS the export path: it rebuilds the MT5 wire record from the row.
    record = config_mappers.group_mt5_record(row)

    assert record["Group"] == "real\\real"
    assert record["MarginCall"] == "50.00"
    assert record["MarginStopOut"] == "30.00"
    assert record["MarginMode"] == "2"  # MARGIN_MODE_RETAIL_HEDGED
    assert record["Currency"] == "USD"
    assert record["TradeFlags"] == str(int(domain.trade_flags))

    # And it satisfies the wire contract, so MT5 Administrator would accept the file.
    assert wire.validate(wire.build("ConfigGroups", [record])) == []


def test_group_export_scale_matches_mt5_not_python_repr():
    """"50" must go out as "50.00": MT5 writes MarginCall at 2 decimal places."""
    from infrastructure.persistence import config_mappers

    group = _sample_group()
    group.margin.margin_call_level = Decimal("50")
    row = group_to_db(group)
    record = config_mappers.group_mt5_record(row)
    assert record["MarginCall"] == "50.00"
    assert record["MarginStopOut"] == "30.00"


def _sample_symbol() -> Symbol:
    return Symbol(
        id="sym-1",
        name="EURUSD",
        path="FX\\Forex\\EURUSD",
        description="Euro vs US Dollar",
        base_currency="EUR",
        quote_currency="USD",
        calc_mode=CalculationMode.FOREX,
        digits=5,
        tick_size=Decimal("0.00001"),
        tick_value=Decimal("10"),
        contract_size=Decimal("100000"),
        volume_min=Decimal("0.01"),
        volume_max=Decimal("100"),
        volume_step=Decimal("0.01"),
        margin_rates=MarginRates(
            initial_buy=Decimal("0.01"), maintenance_buy=Decimal("0.005")
        ),
        swap_long=Decimal("-7.9"),
        swap_short=Decimal("-0.83"),
        swap_3day=3,
        trade_sessions=[
            TradingSession(day_of_week=1, open_minutes=0, close_minutes=1440),
            TradingSession(day_of_week=2, open_minutes=230, close_minutes=630),
        ],
    )


def test_symbol_round_trips_through_the_database_model():
    original = _sample_symbol()
    row = symbol_to_db(original)
    restored = db_to_symbol(row)

    assert restored.name == "EURUSD"
    assert restored.path == "FX\\Forex\\EURUSD"
    assert restored.base_currency == "EUR"
    assert restored.quote_currency == "USD"
    assert restored.digits == 5
    # Point is the precision step; it must survive as tick_size in the domain.
    assert restored.tick_size == Decimal("0.00001")
    assert restored.contract_size == Decimal("100000")
    assert restored.calc_mode is CalculationMode.FOREX
    assert restored.margin_rates.initial_buy == Decimal("0.01")
    assert restored.margin_rates.maintenance_buy == Decimal("0.005")
    # The other 14 rates keep their default rather than collapsing to zero.
    assert restored.margin_rates.initial_sell == Decimal("1.0")
    assert restored.swap_long == Decimal("-7.9")
    assert restored.swap_3day == 3


def test_symbol_sessions_survive_in_mt5_sunday_first_order():
    row = symbol_to_db(_sample_symbol())
    restored = db_to_symbol(row)

    by_day = {s.day_of_week: s for s in restored.trade_sessions}
    assert by_day[1].open_minutes == 0 and by_day[1].close_minutes == 1440
    assert by_day[2].open_minutes == 230 and by_day[2].close_minutes == 630
    # Index 1 is Monday in MT5's Sunday-first ordering, not Tuesday.
    from infrastructure.mt5.wire import WEEKDAY_SUNDAY_FIRST

    assert WEEKDAY_SUNDAY_FIRST[1] == "Monday"
    assert WEEKDAY_SUNDAY_FIRST[2] == "Tuesday"


def test_unmodelled_mt5_fields_survive_a_symbol_round_trip():
    """IETimeout is not modelled; the three symbol currencies now are.

    They must still be persistable, because a group or symbol imported from a real MT5
    server has to export back losslessly. That is what the mt5_extra pass-through is for.
    """
    record = {
        "Symbol": "EURUSD",
        "Path": "FX" + chr(92) + "Forex" + chr(92) + "EURUSD",
        "Point": "0.00001000",
        "TickSize": "0.00000",
        "CurrencyBase": "EUR",
        "CurrencyProfit": "USD",
        "CurrencyMargin": "EUR",
        "ContractSize": "100000.00000000",
        "IETimeout": "7",
    }
    domain = record_to_domain(record, fieldmap.SYMBOL_FIELDS)
    quarantine = domain["_mt5_extra"]
    scale = domain["_mt5_scale"]

    symbol = Symbol(
        name=domain["name"],
        path=domain.get("path", ""),
        base_currency=domain.get("base_currency", ""),
        # MT5 CurrencyProfit and CurrencyMargin are modelled fields as of M3, so they are
        # passed in explicitly rather than left to land in the quarantine.
        quote_currency=domain.get("quote_currency", ""),
        margin_currency=domain.get("margin_currency", ""),
        tick_size=domain["tick_size"],
        contract_size=domain["contract_size"],
    )
    row = symbol_to_db(symbol, mt5_extra=quarantine, mt5_scale=scale)

    # The currencies travel through real columns, not the pass-through. This is the
    # assertion that would fail if the fieldmap entries were dropped again.
    assert row.base_currency == "EUR"
    assert row.quote_currency == "USD", "CurrencyProfit must land in quote_currency"
    assert row.margin_currency == "EUR", "CurrencyMargin must be its own column"
    for modelled in ("CurrencyBase", "CurrencyProfit", "CurrencyMargin"):
        assert modelled not in row.mt5_extra, f"{modelled} is modelled, not quarantined"

    # IETimeout is still genuinely unmodelled, so the pass-through must keep working.
    assert row.mt5_extra["IETimeout"] == 7
    assert "TickSize" not in row.mt5_extra, "TickSize is a modelled field now"
    # Point and TickSize stay distinct across the trip.
    assert row.point == Decimal("0.00001000")
    assert row.mt5_tick_size == Decimal("0")

    restored = db_to_symbol(row)
    assert restored.name == "EURUSD"
    assert restored.tick_size == Decimal("0.00001000")
    # The three currencies survive the full trip, which is what makes a EURJPY position on
    # a USD account computable after an import/export cycle.
    assert restored.base_currency == "EUR"
    assert restored.quote_currency == "USD"
    assert restored.margin_currency == "EUR"


def test_group_mt5_extra_preserves_unmodelled_fields():
    group = _sample_group()
    row = group_to_db(group)
    # White-label and auth fields are MT5 columns we store but do not yet model in the
    # domain; they must still be readable off the row for a faithful export.
    assert row.company == ""
    assert row.auth_password_min == 8
    assert isinstance(row.mt5_extra, dict)

# ---------------------------------------------------------------------------
# The payoff: a real MT5 server export survives domain -> row -> export
# ---------------------------------------------------------------------------

import os
import pathlib

FIXTURES = pathlib.Path(
    os.environ.get("BROKER_MT5_FIXTURES", "")
    or pathlib.Path(__file__).resolve().parents[4] / "decoded" / "mt5-format-structure"
)
requires_fixtures = pytest.mark.skipif(
    not FIXTURES.is_dir(), reason=f"MT5 export fixtures not found at {FIXTURES}"
)


def _seeder_group(raw: dict, dom: dict) -> Group:
    """Build a Group from an MT5 record the way the M2 seeder will."""
    from infrastructure.mt5 import wire
    from infrastructure.persistence import config_mappers

    margin = dom.get("margin") or {}
    account_type = mt5enums.account_type_from_group_path(dom["name"]) or AccountType.REAL
    commissions = []
    for entry in dom.get("commissions") or []:
        tiers = entry.get("tiers") or []
        first = tiers[0] if tiers else {}
        commissions.append(
            CommissionRule(
                name=entry.get("name") or "",
                symbol_pattern=entry.get("symbol_pattern") or "*",
                currency=entry.get("currency") or "USD",
                value=first.get("rate") or Decimal(0),
            )
        )
    overrides = []
    for entry in dom.get("symbol_overrides") or []:
        overrides.append(
            GroupSymbolOverride(symbol_pattern=entry.get("symbol_pattern") or "*")
        )
    return Group(
        name=dom["name"],
        server_id=int(dom.get("server_id", 1)),
        currency=dom.get("currency", "USD"),
        account_type=account_type,
        margin=MarginProfile(
            mode=mt5enums.MARGIN_MODE_FROM_MT5.get(
                int(margin.get("mode", 0)), MarginMode.RETAIL
            ),
            margin_call_level=margin.get("margin_call_level") or Decimal("50"),
            stop_out_level=margin.get("stop_out_level") or Decimal("30"),
        ),
        trade_flags=TradeFlags(int(raw.get("TradeFlags", 0) or 0)),
        # All three limits must come off the wire. The domain defaults are 200/200/100,
        # and MT5's real groups carry 0 (= unlimited), so omitting any of them makes
        # the export assert our default over the server's actual value.
        limit_orders=int(raw.get("LimitOrders", 0) or 0),
        limit_positions=int(raw.get("LimitPositions", 0) or 0),
        limit_symbols=int(raw.get("LimitSymbols", 0) or 0),
        commissions=commissions,
        symbol_overrides=overrides,
    )


@requires_fixtures
def test_every_real_mt5_group_round_trips_through_the_database():
    """The M1 acceptance criterion, against the live server export rather than a mock.

    20 groups x 44 fields go MT5 record -> domain Group -> GroupModel row -> MT5
    record, and come out field-for-field identical while still satisfying the wire
    contract. This is what makes "import from MT5, edit, export back to MT5" safe.
    """
    from infrastructure.mt5 import wire
    from infrastructure.persistence import config_mappers

    records = wire.records(
        wire.decode_file(FIXTURES / "Groups TCTrader-Live.json"), "ConfigGroups"
    )
    assert len(records) == 20

    for raw in records:
        dom, extra, scale = config_mappers.split_mt5_record(raw, fieldmap.GROUP_FIELDS)
        row = config_mappers.group_to_db(
            _seeder_group(raw, dom),
            mt5_extra=extra,
            mt5_scale=scale,
            mt5_source=raw,
        )
        out = config_mappers.group_mt5_record(row)

        differing = {k: (raw[k], out.get(k)) for k in raw if out.get(k) != raw[k]}
        assert not differing, f"{raw['Group']}: {list(differing.items())[:3]}"
        assert wire.validate(wire.build("ConfigGroups", [out])) == []

        # And the domain object is usable, not just the wire record.
        group = config_mappers.db_to_group(row)
        assert group.name == raw["Group"]
        assert group.margin.margin_call_level == Decimal(raw["MarginCall"])


@requires_fixtures
def test_real_group_margin_thresholds_are_percent_from_the_server():
    """The live server stores 50.00 / 30.00, and demo groups go as low as 10.00 / 1.00."""
    from infrastructure.mt5 import wire
    from infrastructure.persistence import config_mappers

    records = wire.records(
        wire.decode_file(FIXTURES / "Groups TCTrader-Live.json"), "ConfigGroups"
    )
    by_name = {r["Group"]: r for r in records}

    real = by_name["real" + chr(92) + "real"]
    assert real["MarginCall"] == "50.00"
    assert real["MarginStopOut"] == "30.00"

    dom, extra, scale = config_mappers.split_mt5_record(real, fieldmap.GROUP_FIELDS)
    row = config_mappers.group_to_db(
        _seeder_group(real, dom), mt5_extra=extra, mt5_scale=scale, mt5_source=real
    )
    group = config_mappers.db_to_group(row)
    # Percent, straight off the wire, with the scale intact.
    assert group.margin.margin_call_level == Decimal("50.00")
    assert group.margin.stop_out_level == Decimal("30.00")
    assert group.account_type is AccountType.REAL
    assert row.margin_call == Decimal("50.00")


def test_inherit_sentinel_is_not_zero():
    """MT5 writes "default" in an override field to mean "inherit from the base symbol".

    Coercing it to 0 would turn "inherit the margin rate" into "the margin rate is
    zero". 60 of the 64 override fields carry the sentinel in the reference export.
    """
    from infrastructure.mt5.codec import INHERIT, is_inherited

    assert is_inherited("default") is True
    assert is_inherited("0") is False
    assert is_inherited(0) is False
    assert is_inherited("") is False

    override = GroupSymbolOverride(symbol_pattern="FX" + chr(92) + "*")
    group = _sample_group()
    group.symbol_overrides = [override]
    row = group_to_db(group)

    stored = row.symbol_overrides_json
    assert stored, "the override should have been persisted"
    # Every field the domain left unset must be the sentinel, not a number.
    for key in ("TradeMode", "ExecMode", "SpreadDiff", "VolumeMin", "MarginInitialBuy"):
        assert stored[0][key] == INHERIT, f"{key} became {stored[0][key]!r}, expected 'default'"


@requires_fixtures
def test_reference_export_uses_the_inherit_sentinel_widely():
    """Guards the assumption above against a fixture that would not exercise it."""
    from infrastructure.mt5 import wire
    from infrastructure.mt5.codec import is_inherited

    records = wire.records(
        wire.decode_file(FIXTURES / "Groups TCTrader-Live.json"), "ConfigGroups"
    )
    overrides = [o for r in records for o in r["Symbols"]]
    assert overrides
    sentinel_fields = {k for o in overrides for k, v in o.items() if is_inherited(v)}
    assert len(sentinel_fields) > 50, f"only {len(sentinel_fields)} fields use the sentinel"


@requires_fixtures
def test_every_real_mt5_symbol_round_trips_through_the_database():
    """362 symbols x 121 fields: MT5 -> domain -> SymbolModel row -> MT5, identical.

    This is the M1 acceptance criterion for the price list, and it is the property that
    makes "import a real MT5 server, edit it, hand it back" safe. It only holds because
    the row stores the imported record as its export baseline and overlays just the
    fields the domain can actually edit - our Symbol models 52 of MT5's 121 fields, so
    rebuilding the record from the domain alone would zero out the other 69.
    """
    from infrastructure.mt5 import wire
    from infrastructure.persistence import config_mappers

    records = wire.records(
        wire.decode_file(FIXTURES / "Symbols TCTrader-Live.json"), "ConfigSymbols"
    )
    assert len(records) == 362

    def or_default(value, fallback):
        # Decimal 0 is a real value; `or` would replace it with the fallback.
        return fallback if value is None else value

    identical = 0
    for raw in records:
        dom, extra, scale = config_mappers.split_mt5_record(raw, fieldmap.SYMBOL_FIELDS)
        margin = dom.get("margin_rates") or {}
        symbol = Symbol(
            name=dom["name"],
            path=dom.get("path", ""),
            description=dom.get("description", ""),
            base_currency=dom.get("base_currency", "USD"),
            quote_currency=dom.get("quote_currency", "USD"),
            digits=int(dom.get("digits", 5)),
            tick_size=or_default(dom.get("tick_size"), Decimal("0.00001")),
            mt5_tick_size=or_default(dom.get("mt5_tick_size"), Decimal(0)),
            tick_value=or_default(dom.get("tick_value"), Decimal(1)),
            contract_size=or_default(dom.get("contract_size"), Decimal(100000)),
            calc_mode=CalculationMode(int(dom.get("calc_mode", 0))),
            trade_mode=TradeMode(int(dom.get("trade_mode", 4))),
            swap_mode=SwapMode(int(dom.get("swap_mode", 0))),
            swap_long=or_default(dom.get("swap_long"), Decimal(0)),
            swap_short=or_default(dom.get("swap_short"), Decimal(0)),
            volume_min=or_default(dom.get("volume_min"), Decimal(0)),
            volume_max=or_default(dom.get("volume_max"), Decimal(0)),
            volume_step=or_default(dom.get("volume_step"), Decimal(0)),
            volume_limit=or_default(dom.get("volume_limit"), Decimal(0)),
            stops_level=int(dom.get("stops_level", 0)),
            freeze_level=int(dom.get("freeze_level", 0)),
            spread=int(dom.get("spread", 0)),
            spread_balance=int(dom.get("spread_balance", 0)),
            swap_3day=int(dom.get("swap_3day", 3)),
            swap_year_days=int(dom.get("swap_year_days", 0)),
            face_value=or_default(dom.get("face_value"), Decimal(0)),
            strike_price=or_default(dom.get("strike_price"), Decimal(0)),
            # Sessions must be decoded from MT5's Sunday-first 7-array. Leaving them
            # empty lets Symbol's own "open all day every day" default overwrite the
            # server's real session calendar on export.
            quote_sessions=_decode_sessions(dom.get("quote_sessions"), QuoteSession),
            trade_sessions=_decode_sessions(dom.get("trade_sessions"), TradingSession),
            margin_rates=MarginRates(
                **{k: or_default(v, Decimal(1)) for k, v in margin.items()}
            ),
        )
        row = config_mappers.symbol_to_db(
            symbol, mt5_extra=extra, mt5_scale=scale, mt5_source=raw
        )
        out = config_mappers.symbol_mt5_record(row)
        differing = {k for k in raw if out.get(k) != raw[k]}
        assert not differing, f"{raw['Symbol']}: {sorted(differing)[:4]}"
        identical += 1

    assert identical == len(records)


@requires_fixtures
def test_crypto_symbols_keep_point_and_ticksize_apart():
    """The concrete case: ADAUSD has Point 0.00001 and TickSize 0.

    If those two were merged, price quantisation would divide by zero or snap every
    crypto price to an integer. 131 of the 362 reference symbols have the two fields
    differing, and every crypto has TickSize = 0.
    """
    from infrastructure.mt5 import wire
    from infrastructure.persistence import config_mappers

    records = wire.records(
        wire.decode_file(FIXTURES / "Symbols TCTrader-Live.json"), "ConfigSymbols"
    )
    crypto = [r for r in records if r["Symbol"].endswith("USD") and r["CalcMode"] == "5"]
    assert crypto, "expected crypto symbols in the reference export"

    zero_ticksize = 0
    for raw in crypto:
        if Decimal(raw["TickSize"] or 0) == 0 and Decimal(raw["Point"] or 0) > 0:
            zero_ticksize += 1
            dom, extra, scale = config_mappers.split_mt5_record(raw, fieldmap.SYMBOL_FIELDS)
            assert dom["tick_size"] > 0, f"{raw['Symbol']}: Point must survive"
            assert dom["mt5_tick_size"] == 0, f"{raw['Symbol']}: TickSize must stay 0"
    assert zero_ticksize > 0, "expected at least one symbol with TickSize = 0"
