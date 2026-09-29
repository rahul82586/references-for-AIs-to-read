#!/usr/bin/env python3
"""Generate the identity-plane YAML data files from the authoritative sources.

Run from the bp root:

    python3 scripts/dev/extract_identity_yaml.py <repo_root> <decoded_fixtures_dir>

Sources (never hand-type these tables):
  * ``<repo_root>/mt5 sdk single md file/MT5 SDK in formated md format/Configuration-Interfaces.md``
      -> IMTConManager::EnManagerRights   -> config/identity/manager_rights.yaml
  * ``<repo_root>/mt5 sdk single md file/MT5 SDK in formated md format/Database-Interfaces.md``
      -> IMTUser::EnUsersRights           -> config/identity/account_rights.yaml
  * ``<decoded_fixtures>/Clients and accounts TCTrader-Live.json`` (UTF-8 decoded)
      -> Server[0].ConfigManagers         -> config/identity/role_presets_builtin.yaml
                                             + tests/fixtures/managers_rights_tctrader_live.json

Idempotent: rerunning regenerates identical files. The preset test in
tests/unit/domains/identity/test_role_presets.py asserts the builtin presets equal
the live export bit for bit, so a bad regeneration fails the suite instead of
silently redefining who is an administrator.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SDK_DIR = "mt5 sdk single md file/MT5 SDK in formated md format"

# ---------------------------------------------------------------------------
# Manager rights (EnManagerRights)
# ---------------------------------------------------------------------------

#: plane = UI grouping for the ~100-right checkbox tree. Prefix rules first,
#: explicit overrides second. Informational only - authorisation reads indices.
_PLANE_PREFIXES = (
    ("RIGHT_CFG_", "configuration"),
    ("RIGHT_SRV_", "server"),
    ("RIGHT_ACC_", "accounts"),
    ("RIGHT_TRADES_", "trades"),
    ("RIGHT_QUOTES", "quotes"),
    ("RIGHT_CLIENTS_", "clients"),
    ("RIGHT_DOCUMENTS_", "documents"),
    ("RIGHT_COMMENTS_", "comments"),
    ("RIGHT_PAYMENTS_", "payments"),
    ("RIGHT_SUBSCRIPTIONS_", "subscriptions"),
    ("RIGHT_FINTEZA_", "analytics"),
    ("RIGHT_GRP_", "groups"),
)
_PLANE_OVERRIDES = {
    "RIGHT_ADMIN": "connection",
    "RIGHT_MANAGER": "connection",
    "RIGHT_CONFIRM_ACTIONS": "connection",
    "RIGHT_ADMIN_COMPUTER": "server",
    "RIGHT_ACCOUNTANT": "funds",
    "RIGHT_PAYMENTS_PROCESS": "funds",
    "RIGHT_RISK_MANAGER": "risk",
    "RIGHT_REPORTS": "reports",
    "RIGHT_CHARTS": "history",
    "RIGHT_EMAIL": "mail",
    "RIGHT_NEWS": "news",
    "RIGHT_EXPORT": "export",
    "RIGHT_SYMBOL_DETAILS": "symbols",
    "RIGHT_TECHSUPPORT": "support",
    "RIGHT_MARKET": "market",
    "RIGHT_NOTIFICATIONS": "notifications",
    "RIGHT_LAST": "sentinel",
}


def _plane(name: str) -> str:
    if name in _PLANE_OVERRIDES:
        return _PLANE_OVERRIDES[name]
    for prefix, plane in _PLANE_PREFIXES:
        if name.startswith(prefix):
            return plane
    return "other"


def extract_manager_rights(sdk_root: Path) -> list[dict]:
    text = (sdk_root / "Configuration-Interfaces.md").read_text(encoding="utf-8", errors="replace")
    start = text.find("## IMTConManager::EnManagerRights")
    if start < 0:
        raise SystemExit("EnManagerRights section not found in Configuration-Interfaces.md")
    seg = text[start:start + 40000]
    seg = seg[: seg.find("\n## ", 10)]
    rows = re.findall(r"^(RIGHT_\w+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*$", seg, re.M)
    out = []
    for name, index, desc in rows:
        desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc).strip()
        out.append(
            {
                "index": int(index),
                "name": name,
                "plane": _plane(name),
                "sentinel": name == "RIGHT_LAST",
                "description": desc,
            }
        )
    out.sort(key=lambda r: r["index"])
    if not out:
        raise SystemExit("no EnManagerRights rows parsed")
    return out


# ---------------------------------------------------------------------------
# User rights (EnUsersRights)
# ---------------------------------------------------------------------------

#: UI semantics: which tab shows the flag and whether the checkbox sense is
#: inverted relative to the bit (MT5 stores TRADE_DISABLED, the UI shows
#: "Enable trading"). From the Administrator guide's Edit-Account tabs.
_USER_UI = {
    "USER_RIGHT_ENABLED": {"tab": "account", "label": "Enable this account", "inverted": False},
    "USER_RIGHT_PASSWORD": {"tab": "account", "label": "Allow to change password", "inverted": False},
    "USER_RIGHT_TRADE_DISABLED": {"tab": "limits", "label": "Enable trading", "inverted": True},
    "USER_RIGHT_INVESTOR": {"tab": None, "label": "investor-password session (internal)", "inverted": False},
    "USER_RIGHT_CONFIRMED": {"tab": "security", "label": "Certificate confirmed", "inverted": False},
    "USER_RIGHT_TRAILING": {"tab": "limits", "label": "Enable trailing stops", "inverted": False},
    "USER_RIGHT_EXPERT": {"tab": "limits", "label": "Enable algo trading by Expert Advisors", "inverted": False},
    "USER_RIGHT_OBSOLETE": {"tab": None, "label": "obsolete, unused", "inverted": False},
    "USER_RIGHT_REPORTS": {"tab": "limits", "label": "Enable daily reports", "inverted": False},
    "USER_RIGHT_READONLY": {"tab": None, "label": "read-only session (internal)", "inverted": False},
    "USER_RIGHT_RESET_PASS": {"tab": "account", "label": "Change password at next login", "inverted": False},
    "USER_RIGHT_OTP_ENABLED": {"tab": "account", "label": "Enable one-time password", "inverted": False},
    "USER_RIGHT_SPONSORED_HOSTING": {"tab": "limits", "label": "Enable sponsored VPS hosting", "inverted": False},
    "USER_RIGHT_API_ENABLED": {"tab": "limits", "label": "Enable API connections (obsolete)", "inverted": False},
    "USER_RIGHT_PUSH_NOTIFICATION": {"tab": None, "label": "Push notifications", "inverted": False},
    "USER_RIGHT_TECHNICAL": {"tab": "limits", "label": "Show to regular managers", "inverted": True},
    "USER_RIGHT_EXCLUDE_REPORTS": {"tab": "limits", "label": "Include in server reports", "inverted": True},
}


def extract_user_rights(sdk_root: Path) -> list[dict]:
    text = (sdk_root / "Database-Interfaces.md").read_text(encoding="utf-8", errors="replace")
    start = text.find("## IMTUser::EnUsersRights")
    if start < 0:
        raise SystemExit("EnUsersRights section not found in Database-Interfaces.md")
    seg = text[start:start + 15000]
    seg = seg[: seg.find("\n## ", 10)]
    rows = re.findall(r"^(USER_RIGHT_\w+)\s*\|\s*(0x[0-9A-Fa-f]+)\s*\|\s*(.*?)\s*$", seg, re.M)
    out = []
    for name, flag, desc in rows:
        desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc).strip()
        ui = _USER_UI.get(name, {"tab": None, "label": name, "inverted": False})
        out.append(
            {
                "name": name,
                "flag": flag.lower(),
                "bit": int(flag, 16),
                "tab": ui["tab"],
                "label": ui["label"],
                "inverted": ui["inverted"],
                "description": desc,
            }
        )
    if not out:
        raise SystemExit("no EnUsersRights rows parsed")
    return out


# ---------------------------------------------------------------------------
# Builtin role presets, decoded from the live export
# ---------------------------------------------------------------------------

PRESET_DESCRIPTIONS = {
    "Administrator": "Every assignable right, exactly the 110-bit mask of the live export's login 1000/2000/3000 administrators (indices 0-109; 110-112 payments and 128 RIGHT_LAST stay unset, as on the real server).",
    "Manager": "The live export's login 208011 'M Manager', bit for bit: 39 rights - the manager terminal, account/trade reads, own-group editing - with no ADMIN, no ACCOUNTANT, no DEALER, no RISK.",
    "Dealer": "Manager plus dealing: RIGHT_QUOTES (31), RIGHT_TRADES_DEALER (37), RIGHT_TRADES_SUPERVISOR (42).",
    "Accountant": "Manager plus RIGHT_ACCOUNTANT (24) - may move client funds.",
    "RiskManager": "Manager plus RIGHT_RISK_MANAGER (32) - aggregate and coverage positions.",
}


def decode_export_managers(fixtures: Path) -> list[dict]:
    path = fixtures / "Clients and accounts TCTrader-Live.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    managers = data["Server"][0]["ConfigManagers"]
    out = []
    for m in managers:
        rights = m["Rights"]
        indices = [i for i, v in enumerate(rights) if str(v).strip() == "1"]
        out.append({"login": str(m["Login"]), "rights_count": len(indices), "rights_indices": indices})
    return out


def build_presets(managers: list[dict], rights_by_index: dict[int, dict]) -> list[dict]:
    by_login = {m["login"]: m for m in managers}
    admin = by_login["1000"]["rights_indices"]
    manager = by_login["208011"]["rights_indices"]
    sets = {
        "Administrator": sorted(admin),
        "Manager": sorted(manager),
        "Dealer": sorted(set(manager) | {31, 37, 42}),
        "Accountant": sorted(set(manager) | {24}),
        "RiskManager": sorted(set(manager) | {32}),
    }
    presets = []
    for name, indices in sets.items():
        presets.append(
            {
                "name": name,
                "description": PRESET_DESCRIPTIONS[name],
                "builtin": True,
                "rights_indices": indices,
                "rights_names": [rights_by_index[i]["name"] for i in indices if i in rights_by_index],
            }
        )
    return presets


# ---------------------------------------------------------------------------
# YAML emission (hand-rolled: pyyaml would reflow the descriptions)
# ---------------------------------------------------------------------------


def _yq(s: str) -> str:
    """Quote a YAML scalar safely."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_manager_rights(path: Path, rights: list[dict]) -> None:
    lines = [
        "# MT5 IMTConManager::EnManagerRights - GENERATED FILE, do not edit by hand.",
        "# Regenerate: python3 scripts/dev/extract_identity_yaml.py <repo_root> <decoded_fixtures>",
        "# Source: the MT5 SDK, Configuration-Interfaces.md. The index IS the position in the",
        "# ConfigManagers Rights array (128 entries, \"0\"/\"1\" strings). RIGHT_LAST (128) is the",
        "# enum terminator: it is listed for completeness and must never be granted.",
        "rights:",
    ]
    for r in rights:
        lines.append(f"  - index: {r['index']}")
        lines.append(f"    name: {r['name']}")
        lines.append(f"    plane: {r['plane']}")
        if r["sentinel"]:
            lines.append("    sentinel: true")
        lines.append(f"    description: {_yq(r['description'])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_account_rights(path: Path, rights: list[dict]) -> None:
    lines = [
        "# MT5 IMTUser::EnUsersRights - GENERATED FILE, do not edit by hand.",
        "# Regenerate: python3 scripts/dev/extract_identity_yaml.py <repo_root> <decoded_fixtures>",
        "# The 16-bit account permission mask (accounts.rights column). `inverted: true` means",
        "# the Admin UI checkbox shows the opposite sense of the stored bit (MT5 stores",
        "# TRADE_DISABLED; the UI shows 'Enable trading').",
        "flags:",
    ]
    for r in rights:
        lines.append(f"  - name: {r['name']}")
        lines.append(f"    bit: {r['bit']}")
        lines.append(f"    flag: {r['flag']}")
        lines.append(f"    tab: {r['tab'] if r['tab'] else 'null'}")
        lines.append(f"    label: {_yq(r['label'])}")
        lines.append(f"    inverted: {'true' if r['inverted'] else 'false'}")
        lines.append(f"    description: {_yq(r['description'])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_presets(path: Path, presets: list[dict]) -> None:
    lines = [
        "# Builtin manager role presets - GENERATED FILE, do not edit by hand.",
        "# Regenerate: python3 scripts/dev/extract_identity_yaml.py <repo_root> <decoded_fixtures>",
        "# Administrator and Manager are DECODED FROM THE LIVE TCTrader-Live EXPORT (logins 1000",
        "# and 208011) - real-server answers, not guesses. tests/unit/domains/identity/",
        "# test_role_presets.py asserts that equality on every run.",
        "presets:",
    ]
    for p in presets:
        lines.append(f"  - name: {p['name']}")
        lines.append(f"    description: {_yq(p['description'])}")
        lines.append("    builtin: true")
        lines.append(f"    rights_indices: [{', '.join(str(i) for i in p['rights_indices'])}]")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    repo_root = Path(sys.argv[1])
    fixtures = Path(sys.argv[2])
    bp = Path(__file__).resolve().parents[2]

    sdk = repo_root / SDK_DIR
    rights = extract_manager_rights(sdk)
    users = extract_user_rights(sdk)
    managers = decode_export_managers(fixtures)
    by_index = {r["index"]: r for r in rights}
    presets = build_presets(managers, by_index)

    ident = bp / "config" / "identity"
    ident.mkdir(parents=True, exist_ok=True)
    write_manager_rights(ident / "manager_rights.yaml", rights)
    write_account_rights(ident / "account_rights.yaml", users)
    write_presets(ident / "role_presets_builtin.yaml", presets)
    # user-saved presets start empty; the API appends (MT5's Save As / Delete)
    saved = ident / "role_presets.yaml"
    if not saved.exists():
        saved.write_text(
            "# User-saved manager role presets (MT5 Permissions tab: Save As / Delete).\n"
            "# Builtin presets live in role_presets_builtin.yaml and cannot be deleted.\n"
            "presets: []\n",
            encoding="utf-8",
        )

    fx = bp / "tests" / "fixtures"
    fx.mkdir(parents=True, exist_ok=True)
    (fx / "managers_rights_tctrader_live.json").write_text(json.dumps(managers, indent=1) + "\n", encoding="utf-8")

    print(f"manager rights: {len(rights)} (sentinel: RIGHT_LAST=128)")
    print(f"user rights:    {len(users)}")
    print(f"presets:        {', '.join(p['name'] + '=' + str(len(p['rights_indices'])) for p in presets)}")
    print(f"fixture:        {len(managers)} managers from the live export")


if __name__ == "__main__":
    main()
