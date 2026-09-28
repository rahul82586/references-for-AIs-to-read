"""
Field-schema query - the descriptor lists the admin UI renders its forms FROM.

Why this exists (IDENTITY-BUILD-PLAN rule 6): if the frontend hardcodes field
lists, every backend change is a two-repo change and the 0/1 bitmask problem
(the live MT5 export marks booleans as "0"/"1" strings the UI cannot interpret)
reaches the browser. Instead `GET /api/v1/admin/<object>/schema` serves this:
names, types, units, enums (EXPANDED from the domain enums at read time, so the
YAML cannot drift from the code), the MT5 tab each field belongs to, the
EnManagerRights bit that gates editing it, and - honestly - whether the field
is modelled/writable TODAY or still row-level quarantine that only round-trips.

The YAML files live in config/schemas/ and are plain data; this module is the
only reader. Unknown object names raise rather than returning an empty schema:
a UI that renders zero fields because of a typo is worse than a 404.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

_CACHE: Dict[str, Dict[str, Any]] = {}


class UnknownSchemaError(KeyError):
    """No descriptor file for that object."""


def _schemas_dir() -> Path:
    override = os.environ.get("BROKER_SCHEMA_DIR")
    if override:
        return Path(override)
    # application/queries/get_field_schema.py -> parents[2] is the bp root
    return Path(__file__).resolve().parents[2] / "config" / "schemas"


def _enum_members(name: str) -> Optional[List[Dict[str, Any]]]:
    """Expand a domain enum name into [{value, name}] - from the CODE, so the
    schema endpoint can never disagree with what the domain accepts."""
    from core.domains.accounts import enums as account_enums

    enum_cls = getattr(account_enums, name, None)
    if enum_cls is None:
        return None
    out = []
    for member in enum_cls:
        value = member.value
        out.append({"name": member.name, "value": int(value) if isinstance(value, int) else str(value)})
    return out


def get_field_schema(object_name: str) -> Dict[str, Any]:
    """The descriptor list for one object ('group' today; account/client/manager
    arrive with their create paths in plan steps 5-8)."""
    if object_name in _CACHE:
        return _CACHE[object_name]

    import yaml

    path = _schemas_dir() / f"{object_name}_fields.yaml"
    if not path.exists():
        raise UnknownSchemaError(
            f"no field schema for {object_name!r} (looked for {path}); "
            f"available: {sorted(p.name.split('_')[0] for p in _schemas_dir().glob('*_fields.yaml'))}"
        )
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    fields: List[Dict[str, Any]] = []
    for entry in raw.get("fields") or []:
        field = dict(entry)
        enum_name = field.get("enum")
        if enum_name:
            members = _enum_members(str(enum_name))
            if members is not None:
                field["enum_values"] = members
        fields.append(field)

    schema = {
        "object": raw.get("object", object_name),
        "wire_section": raw.get("wire_section"),
        "fields": fields,
    }
    _CACHE[object_name] = schema
    return schema


def reset_schema_cache() -> None:
    """Test hook."""
    _CACHE.clear()
