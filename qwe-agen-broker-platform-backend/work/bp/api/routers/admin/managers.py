"""Admin Manager plane - create, read, update, and the rights/preset catalogues.

Plan step 7. Gated by **RIGHT_CFG_MANAGERS** (index 17, "Configuration of
manager rights") - the SDK's own right for this section, not RIGHT_ACC_MANAGER
(which is "Editing accounts"). An operator who may edit accounts should not
therefore be able to grant themselves more rights; MT5 keeps the two bits apart
for exactly that reason, and so does this router.

ROUTE ORDER MATTERS. `/rights`, `/presets` and `/schema` are declared BEFORE
`/{login}`, or a GET for the catalogue resolves as a manager whose login is
literally "rights". This is the same trap M15 hit with `/groups/schema` being
swallowed by `/groups/{group_name:path}`, and it is why the whole router is
mounted before `admin_router` in api/main.py.

Error contract (ENDPOINTS.md §0): 400 the domain refused (not a managers group,
unknown right name, prohibition-only scope, empty mask, no changes); 404 no such
manager/account; 503 a repository is not wired. A 200 means the row really
changed.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth.admin_dependencies import require_right
from api.di_providers import (
    get_create_manager_handler,
    get_update_manager_handler,
)

router = APIRouter(
    prefix="/api/v1/admin/managers",
    tags=["Admin - Managers"],
    dependencies=[Depends(require_right("RIGHT_CFG_MANAGERS"))],
)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ManagerCreateRequest(BaseModel):
    """MT5's manager dialog: Common, Permissions, Reports, IP Access List.

    There is NO login allocation: a manager is created on the basis of an
    EXISTING account whose group name contains "manager", and that account's
    login becomes the manager login.
    """

    login: int = Field(..., description="An existing account's login, in a managers\\... group")
    #: Rights by NAME. Never indices - the SDK leaves 68/69 and 113-127
    #: unassigned and 128 is the never-grantable RIGHT_LAST sentinel.
    rights: Optional[List[str]] = None
    preset: Optional[str] = Field(
        None, description="Administrator | Manager | Dealer | Accountant | RiskManager | a saved preset"
    )
    #: MT5's own mask syntax, order significant (first match wins).
    group_scope: Optional[List[str]] = Field(
        None, description='e.g. ["!managers*", "*"] - a prohibition-only list is refused'
    )
    name: str = ""
    mailbox: str = Field("", description="Empty means the manager cannot send internal mail")
    request_limit_logs: int = 0
    request_limit_reports: int = 0
    password: Optional[str] = Field(
        None,
        description="Omit to mirror the account's existing credential. Supplied: "
                    "validated against the GROUP's AuthPasswordMin, written to the "
                    "account, mirrored here, and returned exactly once.",
    )
    allowed_ips: Optional[List[Any]] = Field(
        None,
        description='CIDR ("10.0.0.0/24"), single address, or an MT5 From/To '
                    'range ("10.0.0.5-10.0.0.9" or {"From":..,"To":..}). '
                    "Empty/omitted = unrestricted, which is what all nine live managers carry.",
    )
    is_2fa_enabled: bool = False
    totp_secret: Optional[str] = None
    role_label: Optional[str] = Field(
        None, description="Cosmetic only. Authorisation never reads it."
    )


class ManagerUpdateRequest(BaseModel):
    """Partial update. An empty update is refused (MT_RET_REQUEST_NO_CHANGES)."""

    rights: Optional[List[str]] = None
    preset: Optional[str] = None
    grant: Optional[List[str]] = None
    revoke: Optional[List[str]] = None
    group_scope: Optional[List[str]] = None
    name: Optional[str] = None
    mailbox: Optional[str] = None
    request_limit_logs: Optional[int] = None
    request_limit_reports: Optional[int] = None
    allowed_ips: Optional[List[Any]] = None
    is_active: Optional[bool] = None
    must_change_password: Optional[bool] = None
    is_2fa_enabled: Optional[bool] = None
    totp_secret: Optional[str] = None


class PresetSaveRequest(BaseModel):
    """MT5's "Save As". Builtins cannot be overwritten or deleted."""

    name: str
    description: str = ""
    rights: Optional[List[str]] = None
    from_login: Optional[int] = Field(
        None, description="Save the mask of an existing manager under a new name"
    )


# ---------------------------------------------------------------------------
# Serialisation - ONE shape, used by every route in this router
# ---------------------------------------------------------------------------


def _manager_payload(manager: Any, *, include_scope_analysis: bool = False) -> Dict[str, Any]:
    """The manager with its rights DECODED TO NAMES and grouped by plane.

    A UI cannot render 128 checkboxes from a bitmask, and it must not be given
    the bitmask to decode either: that is how the 0/1 problem reaches the
    browser. So the names, the SDK index, the plane and the description all come
    from the server, and the array form is included only for export fidelity.
    """
    from core.domains.identity.group_scope import analyse_scope
    from core.domains.identity.rights import get_manager_rights

    registry = get_manager_rights()
    mask = manager.rights
    held = set(mask.indices)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for right in registry.all():
        if right.index not in held:
            continue
        grouped.setdefault(right.plane or "other", []).append(
            {"index": right.index, "name": right.name, "description": right.description}
        )

    payload: Dict[str, Any] = {
        "login": int(manager.login),
        "name": manager.name,
        "mailbox": manager.mailbox,
        "server_id": int(manager.server_id or 1),
        "is_active": bool(manager.is_active),
        "must_change_password": bool(manager.must_change_password),
        "is_2fa_enabled": bool(manager.is_2fa_enabled),
        # COSMETIC. Present so the UI can show a label; authorisation reads the
        # mask, and nothing may infer permissions from this string.
        "role_label": manager.role.value if hasattr(manager.role, "value") else str(manager.role),
        "role_preset": manager.role_preset,
        "rights_count": mask.count,
        "rights_names": mask.to_names(),
        "rights_by_plane": grouped,
        # The unassigned indices the live admins carry 1s at (68/69). Preserved
        # on every round trip so a re-export stays byte-identical; surfaced here
        # so an operator can see the mask is not exactly a union of named rights.
        "rights_unnamed_indices": mask.unnamed_indices(),
        "group_scope": [
            e.get("Group") if isinstance(e, dict) else str(e)
            for e in (manager.group_scope or [])
        ],
        "request_limit_logs": int(manager.request_limit_logs or 0),
        "request_limit_reports": int(manager.request_limit_reports or 0),
        "allowed_ips": list(manager.allowed_ips or []),
        "last_login": manager.last_login.isoformat() if manager.last_login else None,
        "created_at": manager.created_at.isoformat() if manager.created_at else None,
    }
    if include_scope_analysis:
        analysis = analyse_scope(manager.group_scope)
        payload["group_scope_unreachable_rules"] = analysis.unreachable
        payload["group_scope_allows_all"] = analysis.allows_all
    return payload


# ---------------------------------------------------------------------------
# Catalogues - declared BEFORE /{login}
# ---------------------------------------------------------------------------


@router.get("/rights")
async def manager_rights_catalogue() -> Dict[str, Any]:
    """Every named right, with index, plane and description, grouped by plane.

    This drives the UI's permission checkbox tree, so adding a right is a
    backend-only change. The registry is GENERATED from the SDK's
    IMTConManager::EnManagerRights by scripts/dev/extract_identity_yaml.py - it
    is never hand-typed, and RIGHT_LAST (128) is excluded because it is the enum
    terminator, not a grantable permission.
    """
    from core.domains.identity.rights import get_manager_rights

    registry = get_manager_rights()
    everything = registry.all()
    grantable = {r.index for r in registry.grantable()}
    planes: Dict[str, List[Dict[str, Any]]] = {}
    sentinels: List[Dict[str, Any]] = []
    for right in everything:
        entry = {
            "index": right.index,
            "name": right.name,
            "description": right.description,
            "grantable": right.index in grantable,
            "plane": right.plane or "other",
        }
        # A sentinel is the enum's terminator, not a permission. It is reported
        # separately and kept OUT of the plane tree, so the UI cannot render a
        # checkbox for it: ticking RIGHT_LAST would be a meaningless grant that
        # the mask refuses anyway, and a checkbox that can never do anything is
        # worse than no checkbox.
        if right.sentinel or right.index not in grantable:
            sentinels.append(entry)
            continue
        planes.setdefault(right.plane or "other", []).append(entry)
    for entries in planes.values():
        entries.sort(key=lambda r: r["index"])
    return {
        "total": len(everything),
        "grantable": len(registry.grantable()),
        "listed": sum(len(v) for v in planes.values()),
        "mask_width": 128,
        "planes": planes,
        "sentinels": sentinels,
        "note": (
            "Indices 2-9, 68-69, 89-95 and 113-127 are unassigned in the SDK. "
            "The live administrators carry 1s at 68/69; the mask preserves them "
            "so a re-export stays byte-identical. Index 128 is RIGHT_LAST, the "
            "enum terminator, and is never grantable."
        ),
    }


@router.get("/presets")
async def list_presets() -> Dict[str, Any]:
    """The Role picker. Administrator and Manager are decoded from YOUR live export."""
    from core.domains.identity.role_presets import all_presets

    presets = all_presets()
    return {
        "count": len(presets),
        "presets": [
            {
                "name": p.name,
                "description": p.description,
                "builtin": p.builtin,
                "deletable": not p.builtin,
                "rights_count": p.count,
                "rights_names": p.rights.to_names(),
            }
            for p in sorted(presets.values(), key=lambda x: (not x.builtin, x.name))
        ],
        "note": (
            "A preset is a LABEL: applying one loads its bits into the manager's "
            "mask, and the mask stays the only authorisation truth. Builtins ship "
            "with the code and cannot be overwritten or deleted (MT5 behaves the "
            "same way); saved presets are data in config/identity/role_presets.yaml."
        ),
    }


@router.post("/presets", status_code=status.HTTP_201_CREATED)
async def save_preset(body: PresetSaveRequest) -> Dict[str, Any]:
    """MT5's "Save As"."""
    from core.domains.identity.rights import ManagerRightsMask, UnknownRightError
    from core.domains.identity.role_presets import save_preset as _save

    if not body.name.strip():
        raise HTTPException(status_code=400, detail="a preset needs a name")

    # `is not None`, not truthiness: an explicitly EMPTY list is a request to
    # save a preset with no rights, which must be refused as empty rather than
    # mis-read as "no rights supplied, so use from_login".
    if body.rights is not None:
        try:
            mask = ManagerRightsMask.from_names(body.rights)
        except UnknownRightError as exc:
            raise HTTPException(status_code=400, detail=f"unknown right: {exc}")
    elif body.from_login is not None:
        from api.di_providers import get_manager_repo

        repo = get_manager_repo()
        source = await repo.find_by_login(str(body.from_login))
        if source is None:
            raise HTTPException(
                status_code=404, detail=f"no manager with login {body.from_login}"
            )
        mask = source.rights
    else:
        raise HTTPException(
            status_code=400,
            detail="supply either `rights` (named) or `from_login` (copy a manager's mask)",
        )

    if mask.count == 0:
        raise HTTPException(status_code=400, detail="refusing to save an empty preset")
    try:
        saved = _save(body.name.strip(), mask, body.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "name": saved.name,
        "description": saved.description,
        "builtin": saved.builtin,
        "rights_count": saved.count,
        "rights_names": saved.rights.to_names(),
    }


@router.delete("/presets/{name}")
async def delete_preset(name: str) -> Dict[str, Any]:
    """MT5's "Delete". Builtins cannot be deleted."""
    from core.domains.identity.role_presets import PresetNotFoundError
    from core.domains.identity.role_presets import delete_preset as _delete

    try:
        _delete(name)
    except PresetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"deleted": name}


@router.get("/schema")
async def manager_schema() -> Dict[str, Any]:
    """The field descriptors the UI renders the manager form FROM."""
    from application.queries.get_field_schema import UnknownSchemaError, get_field_schema

    try:
        return get_field_schema("manager")
    except UnknownSchemaError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


# ---------------------------------------------------------------------------
# Create / read / update
# ---------------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_manager(body: ManagerCreateRequest) -> Dict[str, Any]:
    """Create a staff login on the basis of an existing managers-group account."""
    from application.commands.create_manager import (
        AccountNotFoundError,
        CreateManagerCommand,
        ManagerRefusedError,
    )

    handler = get_create_manager_handler()
    try:
        command = CreateManagerCommand(**body.model_dump(exclude_none=True))
    except TypeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        result = await handler.handle(command)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ManagerRefusedError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    payload = _manager_payload(result.manager, include_scope_analysis=True)
    payload.update({
        "based_on_account": result.account_login,
        "based_on_group": result.group_name,
        "preset_applied": result.preset_applied,
        "group_scope_unreachable_rules": result.unreachable_scope_rules,
    })
    if result.password:
        # THE ONLY PLACE THE PLAINTEXT EXISTS. Not logged, not published, not
        # stored, and no endpoint returns it again.
        payload["password"] = result.password
        payload["warning"] = (
            "This password is shown exactly once and cannot be retrieved again. "
            "Save it now; the manager must change it at first login."
        )
    return payload


@router.get("/{login}")
async def get_manager(login: str) -> Dict[str, Any]:
    """One manager, with its rights decoded to names and grouped by plane."""
    from api.di_providers import get_manager_repo
    from application.commands.create_manager import ManagerNotFoundError

    manager = await get_manager_repo().find_by_login(str(login))
    if manager is None:
        raise HTTPException(status_code=404, detail=f"no manager with login {login}")
    return _manager_payload(manager, include_scope_analysis=True)


@router.put("/{login}")
async def update_manager(login: str, body: ManagerUpdateRequest) -> Dict[str, Any]:
    """Update rights, scope, limits or IP allow-list. Refuses a no-op."""
    from application.commands.create_manager import (
        ManagerNotFoundError,
        ManagerRefusedError,
        UpdateManagerCommand,
    )

    handler = get_update_manager_handler()
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(
            status_code=400,
            detail="the request changes nothing (MT_RET_REQUEST_NO_CHANGES, 10025)",
        )
    try:
        saved = await handler.handle(UpdateManagerCommand(login=int(login), **data))
    except ManagerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ManagerRefusedError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        # int(login) on a non-numeric path segment
        raise HTTPException(status_code=400, detail=f"login must be an integer: {exc}")
    return _manager_payload(saved, include_scope_analysis=True)
