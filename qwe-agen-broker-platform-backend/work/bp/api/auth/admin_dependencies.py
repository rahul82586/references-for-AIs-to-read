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
