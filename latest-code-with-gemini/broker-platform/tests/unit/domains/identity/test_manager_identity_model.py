"""ManagerAccount declares its fields; the mappers round-trip the mask.

Before step 3, db_to_manager ATTACHED name/mailbox/rights/group_scope/etc. as
dynamic attributes after construction, so every consumer used getattr(...,
default) and a renamed field silently produced a default. These tests pin the
declared shape and the storage round trip (rights_json array AND the three
mask words, both directions).
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.domains.identity.models import ManagerAccount, ManagerRole
from core.domains.identity.rights import ManagerRightsMask
from core.domains.identity.role_presets import builtin_presets


def test_fields_are_declared_not_attached():
    manager = ManagerAccount(manager_id="1", login="1")
    # every MT5 ConfigManagers field exists on a default-constructed entity -
    # no getattr dance, no AttributeError, no silent defaults from consumers
    assert manager.name == ""
    assert manager.mailbox == ""
    assert manager.server_id == 1
    assert isinstance(manager.rights, ManagerRightsMask)
    assert manager.rights.count == 0
    assert manager.group_scope == []
    assert manager.request_limit_logs == 0
    assert manager.request_limit_reports == 0
    assert manager.must_change_password is False
    assert manager.role_preset is None
    # the class really declares them (a dynamic attach would not show here)
    declared = {f for f in ManagerAccount.__dataclass_fields__}
    for field_name in ("name", "mailbox", "server_id", "rights", "group_scope",
                       "request_limit_logs", "request_limit_reports",
                       "must_change_password", "role_preset"):
        assert field_name in declared, field_name


def test_legacy_constructor_signature_still_works():
    """The original positional/keyword signature is untouched (back-compat for
    auth_service tests and the seeder)."""
    manager = ManagerAccount(
        manager_id="mgr_01",
        login="admin_john",
        role=ManagerRole.SUPER_ADMIN,
        password_hash="x",
        totp_secret=None,
        is_2fa_enabled=True,
        allowed_ips=["10.0.0.0/8"],
    )
    assert manager.login == "admin_john"
    assert manager.role is ManagerRole.SUPER_ADMIN


def test_has_right_and_preset_application():
    manager = ManagerAccount(manager_id="1", login="1")
    assert not manager.has_right("RIGHT_CFG_GROUPS")

    manager.apply_preset(builtin_presets()["Manager"])
    assert manager.role_preset == "Manager"
    assert manager.rights.count == 39
    assert manager.has_right("RIGHT_TRADES_READ")
    assert not manager.has_right("RIGHT_CFG_GROUPS")  # the live M Manager lacks it

    manager.apply_preset(builtin_presets()["Administrator"])
    assert manager.has_right("RIGHT_CFG_GROUPS")
    manager.revoke("RIGHT_CFG_GROUPS")
    assert not manager.has_right("RIGHT_CFG_GROUPS")
    manager.grant("RIGHT_CFG_GROUPS")
    assert manager.has_right("RIGHT_CFG_GROUPS")


def test_group_scope_is_mt5_mask_semantics():
    manager = ManagerAccount(manager_id="1", login="1")
    # empty scope follows the platform default: everything
    assert manager.group_scope_patterns() == ["*"]
    assert manager.in_group_scope("real\\real")

    manager.group_scope = [{"Group": "demo*"}]
    assert manager.in_group_scope("demo\\Standard")
    assert manager.in_group_scope("demoforex")
    assert not manager.in_group_scope("real\\real")

    # the guide's own example: "!managers*,*" = everything except managers
    manager.group_scope = [{"Group": "!managers*,*"}]
    assert manager.in_group_scope("demo\\Standard")
    assert manager.in_group_scope("real\\real")
    assert not manager.in_group_scope("managers\\dealers")

    # nothing matched -> fail closed
    manager.group_scope = [{"Group": "demo*"}]
    assert not manager.in_group_scope("coverage\\house")


def test_strictest_report_limit_wins():
    """The guide's worked example, with the units right.

    CORRECTED in step 7. This test used to set `request_limit_reports=30` and
    expect days back. But `IMTConManager::LimitReports` is documented as
    "reports access limit **EnManagerLimit**" - an ORDINAL, 0=unlimited,
    1=1 month, 2=3 months, 3=6 months, 4/5/6=1/2/3 years. 30 is not a valid
    ordinal at all, and min()-ing an ordinal against a per-report DAY count
    compared two different units: "6 months" (ordinal 3) lost to 90 days, so a
    manager was silently restricted to 3 DAYS instead of 90.

    The ordinal is now converted before the comparison, and the guide's own
    example is asserted verbatim: 'Available reports' = 6 months, a report
    limited to 90 days -> 90.
    """
    six_months = ManagerAccount(manager_id="1", login="1", request_limit_reports=3)
    # the guide's example: 6 months (180 days) vs a 90-day report -> 90
    assert six_months.effective_report_window(90) == 90
    # a looser per-report limit -> the manager's own period is stricter
    assert six_months.effective_report_window(400) == 180
    assert six_months.effective_report_window(7) == 7
    # no per-report limit -> the manager's own period, in days
    assert six_months.effective_report_window(None) == 180
    assert six_months.effective_report_window(0) == 180

    unlimited = ManagerAccount(manager_id="2", login="2", request_limit_reports=0)
    assert unlimited.effective_report_window(90) == 90
    assert unlimited.effective_report_window(None) == 0

    with pytest.raises(ValueError):
        # 30 is what this test used to store: not an EnManagerLimit ordinal
        ManagerAccount(manager_id="3", login="3", request_limit_reports=30).effective_report_window(90)


def test_every_manager_limit_ordinal_maps_to_a_day_count():
    from core.domains.accounts.enums import LIMIT_PERIOD_DAYS, ManagerLimit

    assert {int(m.value) for m in ManagerLimit} == set(LIMIT_PERIOD_DAYS)
    assert LIMIT_PERIOD_DAYS[0] == 0                     # unlimited
    assert LIMIT_PERIOD_DAYS[1] < LIMIT_PERIOD_DAYS[6]   # monotonic
    days = [LIMIT_PERIOD_DAYS[i] for i in range(1, 7)]
    assert days == sorted(days)


def test_db_round_trip_preserves_the_mask_both_ways():
    from infrastructure.persistence.account_models import db_to_manager, manager_to_db
    from infrastructure.persistence.manager_models import ManagerModel

    presets = builtin_presets()
    original = ManagerAccount(
        manager_id="208011",
        login="208011",
        role=ManagerRole.READ_ONLY,
        password_hash="argon2:...",
        name="M Manager",
        mailbox="manager@example.com",
        server_id=2,
        rights=presets["Manager"].rights,
        group_scope=[{"Group": "demo*"}, {"Group": "!managers*,*"}],
        request_limit_logs=30,
        request_limit_reports=90,
        must_change_password=True,
    )
    row = manager_to_db(original)
    assert row.rights_json == original.rights.to_array()
    masks = original.rights.to_masks()
    assert (row.rights_mask_0, row.rights_mask_1, row.rights_mask_2) == masks

    restored = db_to_manager(row)
    assert restored.rights == original.rights
    assert restored.name == "M Manager"
    assert restored.mailbox == "manager@example.com"
    assert restored.server_id == 2
    assert restored.group_scope == original.group_scope
    assert restored.request_limit_logs == 30
    assert restored.request_limit_reports == 90
    assert restored.must_change_password is True

    # a row whose rights_json is empty falls back to the mask words
    row.rights_json = []
    assert db_to_manager(row).rights == original.rights

    # legacy callers may still hand manager_to_db a raw array
    legacy = ManagerAccount(manager_id="2", login="2")
    legacy.rights = ["1"] * 128
    assert manager_to_db(legacy).rights_json == ["1"] * 128
    assert db_to_manager(manager_to_db(legacy)).rights.count == 128


def test_manager_mt5_record_export_unchanged():
    """The wire record export must not notice any of this refactor."""
    from infrastructure.persistence.account_models import manager_mt5_record, manager_to_db

    manager = ManagerAccount(
        manager_id="1000", login="1000", role=ManagerRole.SUPER_ADMIN,
        password_hash="x", name="First Admin", mailbox="Administrator",
    )
    manager.rights = ManagerRightsMask.from_array(["1"] * 128)
    manager.group_scope = [{"Group": "*"}]
    record = manager_mt5_record(manager_to_db(manager))
    assert record["Login"] == "1000"
    assert record["Rights"] == ["1"] * 128
    assert record["Groups"] == [{"Group": "*"}]
    assert record["Name"] == "First Admin"
