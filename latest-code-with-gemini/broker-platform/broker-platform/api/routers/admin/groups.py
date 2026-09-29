"""
Admin Group CRUD - the first complete write path of the identity plane.

Why Group first (IDENTITY-BUILD-PLAN step 4): it is the smallest of the four
objects, everything else hangs off it, and CreateGroupHandler already existed -
this router was WRITTEN before (POST /create) but never mounted: api/main.py
imported nothing from here, so the endpoint and its handler were unreachable
(bug F3, the same "handler complete, never registered" class as D2/D11).

Auth: require_right("RIGHT_CFG_GROUPS") - the admin key (bootstrap path) or a
manager JWT whose 128-bit mask carries right 16. The mask is enforced for real
here for the first time.

Error contract (ENDPOINTS.md §0): 400 = the domain refused (duplicate name,
contradicting type, margin_call <= stop_out, no changes, group has accounts);
404 = no such group; 503 = a repository is not wired on this server. A 200
always means the row really changed.

Mount order matters: this router must be included BEFORE admin_router so
GET /groups/schema resolves here instead of being swallowed by admin_router's
GET /groups/{group_name:path}.
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.admin_dependencies import require_right
from api.di_providers import (
    get_create_group_handler,
    get_delete_group_handler,
    get_update_group_handler,
)
from api.schemas.admin.groups import GroupCreateRequest, GroupUpdateRequest
from application.commands.create_group import CreateGroupCommand, CreateGroupHandler
from application.commands.update_group import (
    DeleteGroupCommand,
    DeleteGroupHandler,
    GroupNotFoundError,
    GroupRefusedError,
    UpdateGroupCommand,
    UpdateGroupHandler,
)
from application.queries.get_field_schema import UnknownSchemaError, get_field_schema
from core.domains.identity.group_type import InvalidGroupNameError

router = APIRouter(
    prefix="/api/v1/admin/groups",
    tags=["Admin - Groups"],
    dependencies=[Depends(require_right("RIGHT_CFG_GROUPS"))],
)


def _summary(group: Any) -> Dict[str, Any]:
    # Reuse the admin plane's serializer so a group reads IDENTICALLY from
    # GET /admin/groups/{name} and from a create/update response. Two
    # serializers for one object is how the planes drift (F6's lesson); when
    # step 8 lands the shared serializer module, both import it from there.
    from api.routers.admin.admin_router import _group_summary

    return _group_summary(group)


def _lookup_name(raw: str) -> str:
    """Accept the forward-slash form (URLs cannot carry backslashes) and
    translate to MT5's separator, exactly like admin_router's group detail route."""
    return raw.replace("/", chr(92))


@router.get("/schema")
async def group_schema() -> Dict[str, Any]:
    """The 44 MT5 ConfigGroups field descriptors (+ our additions) that the UI
    renders its Group form from: names, types, units, expanded enums, tab, the
    gating right, and what is modelled/writable TODAY."""
    try:
        return get_field_schema("group")
    except UnknownSchemaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/create", status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_group(
    request: GroupCreateRequest,
    handler: CreateGroupHandler = Depends(get_create_group_handler),
) -> Dict[str, Any]:
    """Create a group. The account type is DERIVED from the name (MT5 rule);
    an explicit contradicting type is refused except contest-on-demo."""
    command = CreateGroupCommand(
        name=_lookup_name(request.name),  # accept real/vip in the body too; MT5 names never contain '/'
        account_type=request.account_type,  # str or None; the handler validates
        currency=request.currency,
        leverage_default=request.leverage_default,
        leverage_max=request.leverage_max,
        margin_call_level=request.margin_call_level,
        stop_out_level=request.stop_out_level,
        trade_allowed=request.trade_allowed,
    )
    try:
        group = await handler.handle(command)
    except (GroupRefusedError, InvalidGroupNameError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"status": "created", "group_id": group.id, "name": group.name, "group": _summary(group)}


@router.put("/{name:path}")
async def update_group(
    name: str,
    request: GroupUpdateRequest,
    handler: UpdateGroupHandler = Depends(get_update_group_handler),
) -> Dict[str, Any]:
    """Partial update. Refuses: unknown group (404), currency change while the
    group has accounts, margin_call <= stop_out, and a request that changes
    nothing (MT_RET_REQUEST_NO_CHANGES)."""
    command = UpdateGroupCommand(name=_lookup_name(name), **request.model_dump(exclude_unset=True))
    try:
        group = await handler.handle(command)
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (GroupRefusedError, InvalidGroupNameError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"status": "updated", "name": group.name, "group": _summary(group)}


@router.delete("/{name:path}")
async def delete_group(
    name: str,
    handler: DeleteGroupHandler = Depends(get_delete_group_handler),
) -> Dict[str, Any]:
    """Delete an EMPTY group. Refuses while it has accounts - including when
    the account count cannot be verified (fail closed)."""
    try:
        deleted = await handler.handle(DeleteGroupCommand(name=_lookup_name(name)))
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (GroupRefusedError, InvalidGroupNameError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"status": "deleted", "name": deleted}
