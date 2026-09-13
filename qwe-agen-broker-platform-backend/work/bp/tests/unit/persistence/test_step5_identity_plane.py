"""Step 5 (identity plane) — the entity/model/mapper atomicity guarantees.

Every assertion here pins a property that a previous defect broke, so the suite
fails at the point of the mistake rather than three milestones later:

* a model column with no mapper is a full-row ``save()`` waiting to blank it
  (D8b, D15, and D18 for groups);
* two stored facts for one MT5 bit is how ``margin_level`` came to be served from
  a place that never computed it (D1, D13, D16);
* a test that re-implements the code under test only proves the test agrees with
  itself (the drifted ``_seeder_group`` copy).
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
from decimal import Decimal

import pytest

from core.domains.accounts.account import Account
from core.domains.accounts.client import Client
from core.domains.accounts.enums import (
    AuthMode,
    HistoryLimit,
    MailMode,
    PermissionsFlags,
    ReportsMode,
    TradeFlags,
    TransferMode,
)
from core.domains.accounts.group import Group
from core.domains.identity.rights import (
    MT5_USER_RIGHT_ALL,
    MT5_USER_RIGHT_DEFAULT,
    UserRight,
)

requires_fixtures = pytest.mark.skipif(
    not os.environ.get("BROKER_MT5_FIXTURES"),
    reason="BROKER_MT5_FIXTURES not set (decoded mt5-format-structure)",
)
FIXTURES = pathlib.Path(os.environ.get("BROKER_MT5_FIXTURES", "."))


# ---------------------------------------------------------------------------
# 1. No model column without a mapper, in BOTH directions
# ---------------------------------------------------------------------------

#: Columns no mapper can own: primary/foreign keys and bookkeeping the database
#: or the framework fills in, not the domain.
_NOT_DOMAIN_OWNED = {
    "created_at",
    "updated_at",
    "group_name",   # written from account.group.name, not a domain field
    "last_valuation_at",  # written only by the valuation sweep (one writer)
}


def _mapped_names(fn, obj) -> set:
    """The model attributes a mapper function actually assigns."""
    import inspect

    src = inspect.getsource(fn)
    return set(
        name
        for name in __import__("re").findall(r"^\s{8}([a-z_0-9]+)=", src, __import__("re").M)
    )


def test_every_account_model_column_is_written_by_account_to_db():
    """The step-5 atomicity rule, enforced: declare a column, write it too.

    Migration 009 added 33 columns to `accounts`. If the model declares one that
    `account_to_db` never sets, `session.merge()` writes NULL/default over
    whatever the database held - silently, on every save. That is D8b.
    """
    from infrastructure.persistence.account_models import AccountModel, account_to_db

    columns = {c.name for c in AccountModel.__table__.columns}
    written = _mapped_names(account_to_db, None)
    missing = columns - written - _NOT_DOMAIN_OWNED
    assert not missing, (
        f"AccountModel declares columns account_to_db never writes: {sorted(missing)}. "
        "A declared column with no mapper is a full-row merge waiting to blank it."
    )


#: Columns db_to_account deliberately does NOT read back, and why. Each is a
#: one-writer decision, not an oversight - an empty diff here is the point.
_INTENTIONALLY_NOT_READ = {
    # D1 defence in depth: margin_level is DERIVED from equity / margin_used on
    # read rather than trusted from the column, so a stale or defaulted 0 can
    # never be served to a client or handed to routing as a real comparison.
    "margin_level",
    # The mask is the authority; is_enabled is a mirror written on the way in.
    # Reading it back would create the second writer this file exists to prevent.
    "is_enabled",
}


def test_every_account_model_column_is_read_by_db_to_account():
    """The other direction: a column nobody reads is a value nobody can serve."""
    import inspect
    import re

    from infrastructure.persistence.account_models import AccountModel, db_to_account

    columns = {c.name for c in AccountModel.__table__.columns}
    src = inspect.getsource(db_to_account)
    # Both access forms the mapper uses: `model.x` and `getattr(model, "x", ...)`.
    read = set(re.findall(r"model\.([a-z_0-9]+)", src))
    read |= set(re.findall(r"getattr\(\s*model\s*,\s*[\"\']([a-z_0-9]+)", src))
    # Helpers that take the whole model and read columns inside themselves.
    for helper in ("_user_rights_or_legacy", "_json_loads"):
        fn = getattr(__import__(
            "infrastructure.persistence.account_models", fromlist=[helper]
        ), helper, None)
        if fn is not None:
            hsrc = inspect.getsource(fn)
            read |= set(re.findall(r"model\.([a-z_0-9]+)", hsrc))
            read |= set(re.findall(r"getattr\(\s*model\s*,\s*[\"\']([a-z_0-9]+)", hsrc))

    unread = columns - read - _NOT_DOMAIN_OWNED - _INTENTIONALLY_NOT_READ
    assert not unread, f"db_to_account never reads: {sorted(unread)}"


def test_the_intentionally_unread_columns_are_still_written():
    """The complement: a column we refuse to READ must still be WRITTEN.

    margin_level and is_enabled are served from elsewhere on purpose, but
    external SQL consumers (reports, the manager terminal's own queries) read the
    columns, so they must stay correct in the database.
    """
    import inspect
    import re

    from infrastructure.persistence.account_models import account_to_db

    src = inspect.getsource(account_to_db)
    written = set(re.findall(r"^\s{8}([a-z_0-9]+)=", src, re.M))
    for col in _INTENTIONALLY_NOT_READ:
        assert col in written, col


def test_account_model_column_count_matches_the_live_neon_schema():
    """67 columns, exactly what the reconstructed migration 009 put on Neon.

    Pinned to a number on purpose. The live production schema is the contract;
    if this drifts, `create_all` and `alembic upgrade head` stop describing the
    same database and the p1 migration proof is the only thing that would notice.
    """
    from infrastructure.persistence.account_models import AccountModel
    from infrastructure.persistence.manager_models import ClientModel

    assert len(AccountModel.__table__.columns) == 67
    assert len(ClientModel.__table__.columns) == 32


def test_every_client_model_column_round_trips():
    from infrastructure.persistence.account_models import client_to_db, db_to_client
    from infrastructure.persistence.manager_models import ClientModel

    c = Client(
        full_name="A Person",
        middle_name="M",
        state="MH",
        id_number="PASS-123",
        lead_source="web",
        lead_campaign="2026-q3",
        country="IN",
        city="Pune",
        zip_code="411001",
        address="1 Main St",
    )
    back = db_to_client(client_to_db(c))
    for f in dataclasses.fields(Client):
        if f.name in ("created_at", "updated_at"):
            continue
        assert getattr(back, f.name) == getattr(c, f.name), f.name


# ---------------------------------------------------------------------------
# 2. The rights mask is the ONE writer of is_enabled
# ---------------------------------------------------------------------------


def test_rights_is_a_stored_field_and_is_enabled_is_not():
    fields = {f.name for f in dataclasses.fields(Account)}
    assert "rights" in fields
    assert "is_enabled" not in fields, (
        "is_enabled must stay an InitVar/property. As a stored field it is a "
        "second fact about USER_RIGHT_ENABLED, and the two can disagree."
    )


def test_is_enabled_is_a_view_of_the_enabled_bit_both_ways():
    a = Account(login=1)
    assert a.is_enabled is True
    assert a.rights & UserRight.ENABLED

    a.is_enabled = False
    assert not (a.rights & UserRight.ENABLED)
    a.is_enabled = True
    assert a.rights & UserRight.ENABLED

    b = Account(login=2, is_enabled=False)
    assert b.is_enabled is False
    assert not (b.rights & UserRight.ENABLED)


def test_constructor_is_enabled_only_touches_the_one_bit():
    """An explicit is_enabled must not clobber the rest of a supplied mask."""
    mask = UserRight.ENABLED | UserRight.EXPERT | UserRight.TECHNICAL
    a = Account(login=3, rights=mask, is_enabled=False)
    assert not (a.rights & UserRight.ENABLED)
    assert a.rights & UserRight.EXPERT
    assert a.rights & UserRight.TECHNICAL


def test_default_rights_are_the_sdks_user_right_default():
    """0x163 - the five boxes MT5's Limits tab shows ticked on a fresh account.

    Not ENABLED|PASSWORD (0x3): that was the spec's guess, and it silently
    stripped trailing stops, Expert Advisors and daily reports from every account
    this platform created.
    """
    assert int(MT5_USER_RIGHT_DEFAULT) == 0x163
    assert Account(login=1).rights == MT5_USER_RIGHT_DEFAULT


def test_from_flags_refuses_bits_outside_the_sdk_enum():
    with pytest.raises(ValueError):
        UserRight.from_flags(0x40000)
    assert UserRight.from_flags(None) is UserRight.NONE
    assert UserRight.OBSOLETE not in MT5_USER_RIGHT_ALL


def test_trading_disabled_is_the_inverted_sense_and_blocks_trading():
    """SDK: USER_RIGHT_TRADE_DISABLED is INVERTED - set means trading is OFF.

    The guide also requires that a disabled account is NOT stopped out, because
    stop-out is the broker's own internal risk tool.
    """
    a = Account(login=4, rights=UserRight.ENABLED | UserRight.TRADE_DISABLED)
    assert a.is_enabled is True          # may still connect
    assert a.trading_disabled is True
    assert a.may_trade is False
    assert a.can_trade() is False


def test_investor_session_can_never_trade():
    a = Account(login=5, rights=MT5_USER_RIGHT_DEFAULT | UserRight.INVESTOR)
    assert a.is_investor_session is True
    assert a.can_trade() is False


def test_technical_bit_is_the_one_the_partial_index_exposes():
    """Migration 009's index is `WHERE (rights & 65536) <> 0`."""
    assert int(UserRight.TECHNICAL) == 65536
    assert Account(login=6, rights=UserRight.TECHNICAL).is_technical is True
    assert Account(login=7).is_technical is False


# ---------------------------------------------------------------------------
# 3. The group engine owns all 44 ConfigGroups fields
# ---------------------------------------------------------------------------


def test_every_configgroups_wire_field_has_a_domain_path():
    """No ConfigGroups field may be left unmapped and quarantined.

    Quarantine keeps an import re-exportable, but it means the entity can neither
    read nor write the field - so /schema advertises a control nothing can set.
    """
    from infrastructure.mt5 import fieldmap

    unmapped = [f.mt5 for f in fieldmap.GROUP_FIELDS if not f.domain]
    assert not unmapped, f"ConfigGroups fields with no domain path: {unmapped}"
    assert len(fieldmap.GROUP_FIELDS) == 44


def test_group_declares_the_mt5_scalar_fields():
    names = {f.name for f in dataclasses.fields(Group)}
    for expected in (
        "permissions_flags", "auth_mode", "auth_password_min", "auth_otp_mode",
        "company", "company_page", "company_email", "company_support_page",
        "company_support_email", "company_catalog", "company_deposit_url",
        "company_withdrawal_url", "reports_mode", "reports_flags", "reports_email",
        "news_category", "news_langs", "mail_mode", "trade_transfer_mode",
        "trade_interestrate", "trade_virtual_credit", "demo_leverage",
        "demo_deposit", "demo_trades_clean", "limit_history",
        "limit_positions_volume",
    ):
        assert expected in names, expected


def test_trade_flags_covers_the_full_sdk_bitspace():
    """The live export carries TradeFlags=215 and the SDK defines bits to 0x800.

    Missing members made `int(TradeFlags(x)) != x`, so a group's flags changed on
    a read/write cycle - the same silent-corruption shape as D18.
    """
    for bit in (0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80, 0x100, 0x200, 0x400, 0x800):
        assert int(TradeFlags(bit)) == bit
    assert int(TradeFlags(215)) == 215


def test_group_permission_helpers_read_the_flags():
    g = Group(name="demo\\Standard", permissions_flags=PermissionsFlags.ENABLE_CONNECTION)
    assert g.clients_may_connect() is True
    assert g.forces_password_reset() is False
    g.permissions_flags |= PermissionsFlags.RESET_PASSWORD | PermissionsFlags.FORCED_OTP_USAGE
    assert g.forces_password_reset() is True
    assert g.forces_otp() is True


def test_effective_limit_orders_stricter_wins_and_null_is_unlimited():
    """Guide, Limits tab: falls back to the group; when both set, stricter wins.

    NULL is not 0 - 0 means "no orders allowed", NULL means "no limit".
    """
    a = Account(login=8)
    assert a.limit_orders is None
    assert a.effective_limit_orders(200) == 200          # inherit the group
    a.limit_orders = 50
    assert a.effective_limit_orders(200) == 50           # account is stricter
    a.limit_orders = 500
    assert a.effective_limit_orders(200) == 200          # group is stricter
    a.limit_orders = 0
    assert a.effective_limit_orders(200) == 0            # 0 is a real limit
    assert Account(login=9).effective_limit_orders(None) is None


def test_display_name_composes_the_three_parts():
    """IMTUser::Name is composed; MT5 stores first/middle/last separately."""
    assert Account(login=10, first_name="John", middle_name="Q", last_name="Public").display_name() == "John Q Public"
    assert Account(login=11, first_name="John", last_name="Public").display_name() == "John Public"
    assert Account(login=12).display_name() == ""


# ---------------------------------------------------------------------------
# 4. D18 — an imported group survives an edit
# ---------------------------------------------------------------------------


@requires_fixtures
def test_all_live_groups_import_with_every_enum_in_range():
    """No group may need _enum_from_wire's fallback.

    The fallback logs and substitutes the 0 member, which is honest but lossy. If
    a future MT5 build adds an enum member we have not transcribed, this fails
    loudly against the real reference data instead of quietly importing a wrong
    value into 20 groups.
    """
    import logging

    from infrastructure.config.loader import groups_from_mt5

    logger = logging.getLogger("infrastructure.config.loader")
    messages: list = []

    class _Capture(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())

    handler = _Capture()
    logger.addHandler(handler)
    try:
        groups = groups_from_mt5(FIXTURES / "Groups TCTrader-Live.json")
    finally:
        logger.removeHandler(handler)

    assert len(groups) == 20
    outside = [m for m in messages if "transcribed range" in m]
    assert not outside, f"enum values fell back to a default: {outside}"
    # and no decimal field was unparseable either
    assert not [m for m in messages if "using 0" in m], messages


@requires_fixtures
@pytest.mark.asyncio
async def test_d18_saving_an_imported_group_preserves_its_mt5_baseline():
    """One innocuous edit must not cost the group its imported identity.

    Before the fix, `SqlGroupRepository.save()` rebuilt the row from the entity
    alone and merged it, NULLing mt5_source / mt5_scale / mt5_extra. Setting
    `limit_orders = 500` on demo\\Standard erased Company="TC Trader",
    CompanyPage, PermissionsFlags, DemoLeverage, DemoDeposit and both nested
    arrays - and with them the byte-identical re-export that is this project's
    signature guarantee.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from infrastructure.config.loader import groups_from_mt5
    from infrastructure.persistence.config_mappers import group_mt5_record, group_to_db
    from infrastructure.persistence.database import Base
    from infrastructure.persistence.repositories.group_repository import SqlGroupRepository

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    repo = SqlGroupRepository(async_sessionmaker(engine, expire_on_commit=False))

    imported = groups_from_mt5(FIXTURES / "Groups TCTrader-Live.json")
    group, extra, scale, source = imported[0]
    await repo.save_model(group_to_db(group, mt5_extra=extra, mt5_scale=scale, mt5_source=source))

    before = group_mt5_record(await repo.find_row_by_name(group.name))

    entity = await repo.find_by_name(group.name)
    entity.limit_orders = 500                      # the only intended change
    await repo.save(entity)                        # the path UpdateGroupHandler takes

    after = group_mt5_record(await repo.find_row_by_name(group.name))

    changed = {k for k in before if str(before[k]) != str(after.get(k))}
    assert changed == {"LimitOrders"}, (
        f"save() changed more than the edit: {sorted(changed)}"
    )
    assert after["Company"] == "TC Trader"
    assert after["CompanyPage"] == "MT5-COMBA-01-STANDARD"
    assert after["PermissionsFlags"] == "2"
    assert after["DemoLeverage"] == "100"
    assert after["DemoDeposit"] == "10000.00"
    # the nested arrays survive because the baseline is still attached
    assert len(after["Commissions"]) == len(before["Commissions"])
    assert len(after["Symbols"]) == len(before["Symbols"])
    await engine.dispose()


@requires_fixtures
def test_imported_group_entity_carries_the_servers_real_values():
    """The loader must populate all 44 fields, not 17 of them.

    This is the drift the duplicated `_seeder_group` test helper hid: it set 17
    fields, and while the other 27 were quarantined nothing noticed.
    """
    from infrastructure.config.loader import groups_from_mt5

    groups = {g.name: g for g, *_ in groups_from_mt5(FIXTURES / "Groups TCTrader-Live.json")}
    std = groups["demo\\Standard"]
    assert std.company == "TC Trader"
    assert std.company_page == "MT5-COMBA-01-STANDARD"
    assert int(std.permissions_flags) == 2
    assert int(std.trade_flags) == 215
    assert std.auth_password_min == 8
    assert std.auth_mode is AuthMode.STANDARD
    assert std.mail_mode is MailMode.FULL
    assert std.reports_mode is ReportsMode.DISABLED
    assert std.trade_transfer_mode is TransferMode.DISABLED
    assert std.limit_history is HistoryLimit.ALL
    assert std.demo_leverage == 100
    assert std.demo_deposit == Decimal("10000.00")
    assert std.limit_positions_volume == Decimal("0.00")
    assert std.margin.margin_call_level == Decimal("10.00")
    assert std.margin.stop_out_level == Decimal("1.00")

    real = groups["real\\real"]
    assert real.margin.margin_call_level == Decimal("50.00")
    assert real.margin.stop_out_level == Decimal("30.00")
