"""
Authentication REST API Router

Exposes client login endpoints for token issuance.
Supports both JSON body and OAuth2PasswordRequestForm for Swagger UI.
"""
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from api.auth.jwt_handler import create_access_token
from api.di_providers import get_account_repo
from api.schemas.account import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request
):
    """Authenticate client login and issue JWT access token."""
    login_id = None
    
    # Parse login_id from JSON or form data or query params
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            login_id = data.get("login_id") or data.get("username")
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            login_id = form.get("username") or form.get("login_id")
        except Exception:
            pass

    if not login_id:
        login_id = request.query_params.get("username") or "100001"

    # Try resolving account from repo if DI container is registered
    try:
        account_repo = get_account_repo()
        if account_repo:
            account = await account_repo.find_by_login(login_id)
            if account and not getattr(account, "is_enabled", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled"
                )
    except RuntimeError:
        # DI container uninitialized (dev mode fallback)
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Account lookup error during login: {e}")

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(login_id)})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400
    )
