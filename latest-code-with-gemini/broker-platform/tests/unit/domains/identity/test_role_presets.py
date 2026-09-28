"""Role presets are decoded from the LIVE TCTrader-Live export, not invented.

The important test is the fixture equality: if RolePreset 'Administrator' does
not equal login 1000's Rights array bit for bit, the model is wrong - that is
a real MT5 server's answer. The fixture ships in tests/fixtures (rights arrays
only, nothing else from the export) so this runs everywhere; when
BROKER_MT5_FIXTURES points at the decoded export the test re-reads the source
file itself, so a fixture that ever drifts from the export fails here.
"""
from __future__ import annotations

import json
import os
import pathlib

import pytest

from core.domains.identity.rights import ManagerRightsMask
from core.domains.identity import role_presets

FIXTURE = pathlib.Path(__file__).resolve().parents[3] / "fixtures" / "managers_rights_tctrader_live.json"


def _fixture_managers():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return {m["login"]: m for m in data}


def _export_managers():
    """The same nine arrays straight from the decoded export, when available."""
    root = os.environ.get("BROKER_MT5_FIXTURES")
    if not root:
        return None
    path = pathlib.Path(root) / "Clients and accounts TCTrader-Live.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for m in data["Server"][0]["ConfigManagers"]:
        indices = [i for i, v in enumerate(m["Rights"]) if str(v).strip() == "1"]
        out[str(m["Login"])] = indices
    return out


def test_builtin_presets_equal_the_live_export_bit_for_bit():
    presets = role_presets.builtin_presets()
    managers = _fixture_managers()

    admin = presets["Administrator"]
    assert admin.rights.indices == frozenset(managers["1000"]["rights_indices"])
    assert admin.count == 110  # 110/128, exactly what the export's six admins carry

    manager = presets["Manager"]
    assert manager.rights.indices == frozenset(managers["208011"]["rights_indices"])
    assert manager.count == 39

    # The composed presets are Manager plus the role-defining bits only.
    assert presets["Dealer"].rights == manager.rights.grant(
        "RIGHT_QUOTES", "RIGHT_TRADES_DEALER", "RIGHT_TRADES_SUPERVISOR"
    )
    assert presets["Accountant"].rights == manager.rights.grant("RIGHT_ACCOUNTANT")
    assert presets["RiskManager"].rights == manager.rights.grant("RIGHT_RISK_MANAGER")
    for preset in presets.values():
        assert preset.builtin is True


def test_preset_semantics_match_the_export_role_analysis():
    """ACCOUNT-GROUP-CREATION-SPEC §1's decoded table, asserted not described."""
    presets = role_presets.builtin_presets()
    admin, manager = presets["Administrator"].rights, presets["Manager"].rights

    # An administrator holds every role bit...
    for right in ("RIGHT_ADMIN", "RIGHT_MANAGER", "RIGHT_TRADES_DEALER",
                  "RIGHT_ACCOUNTANT", "RIGHT_RISK_MANAGER"):
        assert admin.has(right), right
    # ...the live 'M Manager' holds MANAGER only, and is missing exactly the
    # bits the spec says it is missing.
    assert manager.has("RIGHT_MANAGER")
    for right in ("RIGHT_ADMIN", "RIGHT_ACCOUNTANT", "RIGHT_TRADES_MANAGER",
                  "RIGHT_RISK_MANAGER", "RIGHT_TRADES_DEALER", "RIGHT_ACC_DELETE"):
        assert not manager.has(right), right


@pytest.mark.skipif(_export_managers() is None, reason="BROKER_MT5_FIXTURES not set")
def test_shipped_fixture_still_equals_the_real_export():
    export = _export_managers()
    for login, entry in _fixture_managers().items():
        assert login in export
        assert sorted(entry["rights_indices"]) == sorted(export[login]), login


def test_all_nine_export_arrays_round_trip_through_the_mask():
    managers = _export_managers() or {
        login: m["rights_indices"] for login, m in _fixture_managers().items()
    }
    for login, indices in managers.items():
        array = ["0"] * 128
        for i in indices:
            array[i] = "1"
        mask = ManagerRightsMask.from_array(array)
        assert mask.to_array() == array, login
        assert mask.count == len(indices), login


def test_saved_presets_save_as_and_delete(tmp_path):
    """MT5's Save As / Delete: saved presets are data, builtins are untouchable."""
    rights = ManagerRightsMask.from_names(["RIGHT_MANAGER", "RIGHT_QUOTES"])
    saved = role_presets.save_preset("NightDesk", rights, "quotes + manager terminal", config_dir=tmp_path)
    assert saved.builtin is False

    loaded = role_presets.get_preset("NightDesk", config_dir=tmp_path)
    assert loaded.rights == rights
    assert loaded.description == "quotes + manager terminal"

    # a builtin name cannot be overwritten or deleted...
    with pytest.raises(ValueError):
        role_presets.save_preset("Administrator", rights, config_dir=tmp_path)
    with pytest.raises(ValueError):
        role_presets.delete_preset("Administrator", config_dir=tmp_path)
    # ...an unknown name cannot be deleted or fetched...
    with pytest.raises(role_presets.PresetNotFoundError):
        role_presets.delete_preset("NoSuchPreset", config_dir=tmp_path)
    with pytest.raises(role_presets.PresetNotFoundError):
        role_presets.get_preset("NoSuchPreset", config_dir=tmp_path)

    # re-saving an EXISTING saved preset is allowed (that is the Save As loop)
    role_presets.save_preset("NightDesk", rights.grant("RIGHT_REPORTS"), config_dir=tmp_path)
    assert role_presets.get_preset("NightDesk", config_dir=tmp_path).rights.has("RIGHT_REPORTS")

    role_presets.delete_preset("NightDesk", config_dir=tmp_path)
    assert "NightDesk" not in role_presets.saved_presets(tmp_path)
