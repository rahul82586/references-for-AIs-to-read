"""Manager role presets - MT5's "Role" picker, as data.

Administrator guide, Manager → Permissions tab:

    "Role - here you can select one of predefined sets of permissions. Using
     buttons Save As and Delete you can save and delete your own sets of
     permissions."

So a "role" is a SAVED PRESET FILE, not a built-in enum. Picking one simply
loads its bits into the manager's rights mask; the mask stays the only source
of truth (``ManagerAccount.role_preset`` is a cosmetic label for the UI).

The five builtin presets ship as generated data in
``config/identity/role_presets_builtin.yaml``:

* **Administrator** and **Manager** are DECODED FROM THE LIVE TCTrader-Live
  export - login 1000's exact 110-bit array and login 208011's exact 39-bit
  array. Real-server answers, not guesses.
* **Dealer** / **Accountant** / **RiskManager** are the Manager preset plus the
  role-defining bits (37+42+31 / 24 / 32).

User-saved presets live in ``config/identity/role_presets.yaml`` and are
managed through the API (Save As / Delete); builtins cannot be deleted.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from core.domains.identity.rights import ManagerRightsMask, _config_dir, _load_yaml


class PresetNotFoundError(KeyError):
    """No preset with that name. Refuse, never fall back to a default set."""


@dataclass(frozen=True)
class RolePreset:
    """A named, reusable set of manager rights."""

    name: str
    description: str
    rights: ManagerRightsMask
    #: Builtin presets ship with the code and cannot be deleted; saved ones can.
    builtin: bool = False

    @property
    def count(self) -> int:
        return self.rights.count


def _presets_from(raw: List[dict], *, builtin: bool) -> List[RolePreset]:
    out: List[RolePreset] = []
    for entry in raw or []:
        indices = entry.get("rights_indices")
        names = entry.get("rights") or entry.get("rights_names")
        if indices is not None:
            mask = ManagerRightsMask.from_indices(indices)
        elif names is not None:
            mask = ManagerRightsMask.from_names(names)
        else:
            raise ValueError(
                f"role preset {entry.get('name')!r} carries neither rights_indices nor "
                "rights names; refusing to load an empty-by-accident preset"
            )
        out.append(
            RolePreset(
                name=str(entry["name"]),
                description=str(entry.get("description", "")),
                rights=mask,
                builtin=bool(entry.get("builtin", builtin)),
            )
        )
    return out


_BUILTINS: Optional[Dict[str, RolePreset]] = None


def builtin_presets() -> Dict[str, RolePreset]:
    """The five shipped presets, keyed by name (loaded once)."""
    global _BUILTINS
    if _BUILTINS is None:
        raw = _load_yaml("role_presets_builtin.yaml").get("presets") or []
        _BUILTINS = {p.name: p for p in _presets_from(raw, builtin=True)}
    return dict(_BUILTINS)


def saved_presets(config_dir: Optional[Path] = None) -> Dict[str, RolePreset]:
    """User-saved presets (MT5's Save As). A missing/empty file is normal."""
    directory = Path(config_dir) if config_dir else _config_dir()
    path = directory / "role_presets.yaml"
    if not path.exists():
        return {}
    import yaml

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return {p.name: p for p in _presets_from(data.get("presets") or [], builtin=False)}


def all_presets(config_dir: Optional[Path] = None) -> Dict[str, RolePreset]:
    """Builtins plus saved. A saved preset may SHADOW a builtin name only by
    explicit operator action - MT5 keeps them in one picker; we prefer the saved
    one so Save As over 'Dealer' means what the operator did."""
    merged = builtin_presets()
    merged.update(saved_presets(config_dir))
    return merged


def get_preset(name: str, config_dir: Optional[Path] = None) -> RolePreset:
    try:
        return all_presets(config_dir)[name]
    except KeyError:
        raise PresetNotFoundError(
            f"no role preset named {name!r}; available: {sorted(all_presets(config_dir))}"
        ) from None


def save_preset(name: str, rights: ManagerRightsMask, description: str = "",
                config_dir: Optional[Path] = None) -> RolePreset:
    """MT5's Save As. Writes to role_presets.yaml. Refuses to shadow a builtin
    name unless the file already holds that name (explicit re-save)."""
    if name in builtin_presets() and name not in saved_presets(config_dir):
        raise ValueError(
            f"{name!r} is a builtin preset; builtins cannot be overwritten. "
            "Choose another name (MT5 behaves the same way: its defaults are not editable)."
        )
    directory = Path(config_dir) if config_dir else _config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    current = saved_presets(directory)
    current[name] = RolePreset(name=name, description=description, rights=rights, builtin=False)
    _write_saved(directory, current)
    return current[name]


def delete_preset(name: str, config_dir: Optional[Path] = None) -> None:
    """MT5's Delete. Builtins cannot be deleted; an unknown name raises."""
    directory = Path(config_dir) if config_dir else _config_dir()
    current = saved_presets(directory)
    if name in builtin_presets() and name not in current:
        raise ValueError(f"{name!r} is a builtin preset and cannot be deleted")
    if name not in current:
        raise PresetNotFoundError(f"no saved preset named {name!r}")
    del current[name]
    _write_saved(directory, current)


def _write_saved(directory: Path, presets: Dict[str, RolePreset]) -> None:
    lines = [
        "# User-saved manager role presets (MT5 Permissions tab: Save As / Delete).",
        "# Builtin presets live in role_presets_builtin.yaml and cannot be deleted.",
        "presets:",
    ]
    for preset in presets.values():
        lines.append(f"  - name: {preset.name}")
        desc = preset.description.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'    description: "{desc}"')
        lines.append("    builtin: false")
        lines.append(
            "    rights_indices: [" + ", ".join(str(i) for i in sorted(preset.rights.indices)) + "]"
        )
    if not presets:
        lines[-1] = "presets: []"
    (directory / "role_presets.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def reset_preset_cache() -> None:
    """Test hook: drop the cached builtins."""
    global _BUILTINS
    _BUILTINS = None
