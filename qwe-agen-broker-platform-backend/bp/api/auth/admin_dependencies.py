"""
Admin API Key Authorization Dependencies

Verifies header-based X-Admin-API-Key authentication for Eclipse Theia Admin UI and Backoffice services.
"""
import os
from typing import Optional
from fastapi import Header, HTTPException, status

ADMIN_API_KEY_ENV = os.getenv("ADMIN_API_KEY", "ADMIN_SECRET_KEY_12345")


async def verify_admin_api_key(
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key")
) -> str:
    """Validate X-Admin-API-Key header for admin endpoints."""
    if not x_admin_api_key or x_admin_api_key != ADMIN_API_KEY_ENV:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Admin-API-Key header"
        )
    return x_admin_api_key

from api.auth.dependencies import get_current_user
get_current_manager = get_current_user

from api.auth.jwt_handler import verify_token as verify_manager_token
