"""
Admin API Key Authorization Dependencies

Verifies header-based X-Admin-API-Key authentication for Eclipse Theia Admin UI and Backoffice services.

M5: no default key. The pre-M5 fallback ("ADMIN_SECRET_KEY_12345") meant a
deployment that forgot to set the variable was protected by a string that is
public in this repository's history. Now: unset key = every admin request is
refused (fail closed, 503), never silently accepted.
"""
import os
from typing import Optional
from fastapi import Header, HTTPException, status

#: Read at import; api/main.py loads .env before routers are imported.
ADMIN_API_KEY_ENV: Optional[str] = os.getenv("ADMIN_API_KEY")


async def verify_admin_api_key(
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key")
) -> str:
    """Validate X-Admin-API-Key header for admin endpoints."""
    if not ADMIN_API_KEY_ENV:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY is not configured on this server",
        )
    if not x_admin_api_key or x_admin_api_key != ADMIN_API_KEY_ENV:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Admin-API-Key header"
        )
    return x_admin_api_key

from api.auth.dependencies import get_current_user
get_current_manager = get_current_user

from api.auth.jwt_handler import verify_token as verify_manager_token


# ---------------------------------------------------------------------------
# Identity plane (step 3): rights-based authorisation
# ---------------------------------------------------------------------------
#
# Until now the 128-bit rights mask was stored correctly and enforced nowhere:
# `grep rights api/ application/` found four hits, all inside the list-managers
# serializer COUNTING bits for display. require_right() is the line that turns
# stored bits into actual authorisation.
#
# Two credential paths, deliberately:
#   * X-Admin-API-Key (exact match) - the bootstrap/break-glass path. It is the
#     only admin auth that exists until CreateManagerHandler provisions real
#     staff logins, and it grants everything (a server-side secret is already
#     total trust).
#   * Authorization: Bearer <manager JWT> - the token AuthService.login_manager
#     issues (is_manager claim). The manager's mask decides, per right.
#
# Everything else is REFUSED, in the project's fail-closed style:
#   * a client token on the admin plane -> 403, not a silently fabricated
#     identity (F2's lesson: get_current_user invents account 100001; this
#     dependency never invents anything);
#   * unknown / inactive manager login -> 401, indistinguishable (no login
#     enumeration, matching M6's login contract);
#   * must_change_password -> 403 until changed. MT5 stores this flag and
#     blocks; we stored it and ignored it - not anymore;
#   * allowed_ips configured and the client IP outside it -> 403
#     (MT_RET_AUTH_MANAGER_IPBLOCK, 1012).

import ipaddress
from dataclasses import dataclass
from typing import Any, List, Optional

from fastapi import Request


@dataclass
class AdminPrincipal:
    """Who the admin plane resolved for this request. Never fabricated:
    kind='admin_key' means the server-side key matched; kind='manager' means a
    real ManagerAccount row was loaded and its mask checked."""

    kind: str  # "admin_key" | "manager"
    login: Optional[str] = None
    name: str = ""
    rights: Optional[Any] = None  # ManagerRightsMask for kind == "manager"
    manager: Optional[Any] = None  # the ManagerAccount itself


def _ip_entry_matches(addr, entry) -> bool:
    """Does one allow-list entry cover `addr`?

    Three spellings, because MT5's own model and ours do not agree:

    * ``IMTConManagerAccess`` is a **From/To range** - the IP Access List tab has
      two columns, "From" and "To", and the guide's use case is "limit managers'
      access, for example, to the dealing room only". A CIDR cannot express
      10.0.0.5-10.0.0.9, so ranges are accepted both as the wire dict
      ``{"From": …, "To": …}`` and as the string ``"from-to"``.
    * CIDR (``10.0.0.0/24``), which is what this platform stored before and what
      an operator is most likely to type.
    * A single address, which ``ip_network`` handles as a /32.

    An unparseable entry grants NOTHING - it is skipped, not treated as "allow".
    A malformed allow-list must never widen access; that is the fail-closed rule
    the rest of this module follows.
    """
    lo = hi = None
    if isinstance(entry, dict):
        lo = entry.get("From", entry.get("from"))
        hi = entry.get("To", entry.get("to"))
        if lo is None and hi is None:
            return False
    else:
        text = str(entry).strip()
        if not text:
            return False
        if "-" in text and "/" not in text:
            parts = text.split("-", 1)
            lo, hi = parts[0].strip(), parts[1].strip()
        else:
            # A CIDR or a bare address. `ip_address` rejects "10.0.0.0/24", so
            # this branch must go through `ip_network`, which handles BOTH a
            # network and a single host (/32). Treating a CIDR as an address was
            # the regression that made every prefix allow-list silently refuse.
            try:
                return addr in ipaddress.ip_network(text, strict=False)
            except ValueError:
                return False

    try:
        low = ipaddress.ip_address(str(lo).strip())
    except ValueError:
        return False
    try:
        high = ipaddress.ip_address(str(hi).strip())
    except ValueError:
        # "From" without a usable "To": treat it as a single address or a network.
        try:
            return addr in ipaddress.ip_network(str(lo).strip(), strict=False)
        except ValueError:
            return False
    if low.version != high.version or low.version != addr.version:
        return False
    if high < low:
        low, high = high, low          # a reversed range is an operator typo, not a grant
    return low <= addr <= high


def _ip_allowed(client_ip: Optional[str], allowed: List[Any]) -> bool:
    """Allow-list match over CIDRs, single addresses and From/To ranges.

    An EMPTY list means unrestricted - MT5's own semantics, and what all nine
    live managers carry (``Access: []``).
    """
    if not allowed:
        return True
    if not client_ip:
        return False
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(_ip_entry_matches(addr, entry) for entry in allowed)


def require_right(right_name: str):
    """FastAPI dependency factory: the caller must hold `right_name`.

    The right is resolved AT FACTORY TIME (import/startup), so a typo in a
    route definition crashes the boot instead of failing every request later -
    refuse rather than fake, applied to our own code.
    """
    from core.domains.identity.rights import (
        ManagerRightsMask,
        UnknownRightError,
        get_manager_rights,
    )

    try:
        required = get_manager_rights().resolve(right_name)
    except (UnknownRightError, FileNotFoundError) as exc:
        raise RuntimeError(
            f"require_right({right_name!r}): {exc}"
        ) from exc

    async def dependency(
        request: Request,
        x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key"),
        authorization: Optional[str] = Header(None),
    ) -> AdminPrincipal:
        # --- path 1: the server-side admin key -----------------------------
        if x_admin_api_key is not None:
            if not ADMIN_API_KEY_ENV:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="ADMIN_API_KEY is not configured on this server",
                )
            if x_admin_api_key != ADMIN_API_KEY_ENV:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid X-Admin-API-Key header",
                )
            return AdminPrincipal(kind="admin_key")

        # --- path 2: a manager JWT ------------------------------------------
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()
            try:
                payload = verify_manager_token(token)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            if not payload.get("is_manager"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="client tokens cannot access the admin plane",
                )

            from api.di_providers import get_manager_repo

            repo = get_manager_repo()
            if repo is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "the manager repository is not registered in the DI container; "
                        "manager-right authorisation is not wired on this server"
                    ),
                )
            manager = await repo.find_by_login(str(payload.get("sub", "")))
            # An unknown or inactive manager is ONE answer, exactly like M6's
            # login: no enumeration, and never a fabricated identity (anti-F2).
            if manager is None or not manager.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            if manager.must_change_password:
                # MT_RET_AUTH_RESET_PASSWORD (1026): "Master password must be
                # changed." Stored since M2, enforced for the first time here.
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="password change required before this action (MT_RET_AUTH_RESET_PASSWORD)",
                )
            client_ip = request.client.host if request.client else None
            if not _ip_allowed(client_ip, list(manager.allowed_ips or [])):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP address is not valid for this manager (MT_RET_AUTH_MANAGER_IPBLOCK)",
                )
            rights = manager.rights
            if not isinstance(rights, ManagerRightsMask):
                # A legacy raw-array manager (in-memory double predating step 3).
                rights = ManagerRightsMask.from_array(list(rights or []))
            if not rights.has(required):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"manager {manager.login} does not hold {required.name} "
                        f"(right {required.index}); MT_RET_ERR_PERMISSIONS"
                    ),
                )
            return AdminPrincipal(
                kind="manager",
                login=str(manager.login),
                name=manager.name or "",
                rights=rights,
                manager=manager,
            )

        # --- nothing usable --------------------------------------------------
        if not ADMIN_API_KEY_ENV:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ADMIN_API_KEY is not configured on this server",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Admin-API-Key or a manager Bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    dependency.__name__ = f"require_right_{right_name.lower()}"
    return dependency
