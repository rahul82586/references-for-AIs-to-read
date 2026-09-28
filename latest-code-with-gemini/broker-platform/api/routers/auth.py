"""
Authentication REST API Router

Exposes client login endpoints for token issuance.
Supports both JSON body and OAuth2PasswordRequestForm for Swagger UI.
"""
from typing import Optional
import logging
from fastapi import APIRouter, Body, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from api.auth.jwt_handler import create_access_token
from api.di_providers import get_account_repo
from api.schemas.account import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "login_id": {"type": "string", "example": "887914"},
                            "password": {"type": "string", "example": "Password123!"},
                        },
                        "required": ["login_id", "password"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "example": "887914"},
                            "password": {"type": "string", "example": "Password123!"},
                        },
                        "required": ["username", "password"],
                    }
                },
            }
        }
    },
)
async def login(
    request: Request
):
    """Authenticate client login and issue a JWT access token."""
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    generic_failure = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    login_id = None
    password = None

    if not login_id or not password:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                data = await request.json()
                if isinstance(data, dict):
                    login_id = login_id or data.get("login") or data.get("login_id") or data.get("username")
                    password = password or data.get("password")
            except Exception:
                pass
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            try:
                form = await request.form()
                login_id = login_id or form.get("login") or form.get("username") or form.get("login_id")
                password = password or form.get("password")
            except Exception:
                pass

    if not login_id:
        login_id = request.query_params.get("username")
    if not password:
        password = request.query_params.get("password")

    logger.info(f"login attempt for login_id={login_id!r}, password_present={bool(password)}")

    if not login_id or not password:
        logger.info("login refused: login_id and password are both required")
        raise generic_failure

    # 1. Try Account Repository (Client Login)
    account = None
    try:
        account_repo = get_account_repo()
        if account_repo is not None:
            account = await account_repo.find_by_login(login_id)
    except Exception as e:
        logger.warning(f"Account lookup error during login: {e}")

    if account is not None:
        if not getattr(account, "is_enabled", True):
            logger.info("login refused: account %s is disabled", login_id)
            raise generic_failure

        stored_hash = getattr(account, "password_hash", "") or ""
        if not stored_hash:
            logger.warning("login refused: account %s has no password provisioned", login_id)
            raise generic_failure

        try:
            password_ok = Argon2PasswordHasher().verify_password(password, stored_hash)
        except Exception as e:
            logger.error("password verification errored for %s: %s", login_id, e)
            raise generic_failure

        if not password_ok:
            logger.info("login refused: wrong password for client %s", login_id)
            raise generic_failure

        access_token = create_access_token(data={"sub": str(login_id), "role": "client", "is_manager": False})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400
        )

    # 2. Try Manager Repository (Manager / Admin Login)
    manager = None
    try:
        from api.di_providers import get_manager_repo
        manager_repo = get_manager_repo()
        if manager_repo is not None:
            manager = await manager_repo.find_by_login(str(login_id))
    except Exception as e:
        logger.warning(f"Manager lookup error during login: {e}")

    if manager is not None:
        if not getattr(manager, "is_active", True):
            logger.info("login refused: manager %s is disabled", login_id)
            raise generic_failure

        stored_hash = getattr(manager, "password_hash", "") or ""
        if not stored_hash:
            logger.warning("login refused: manager %s has no password hash", login_id)
            raise generic_failure

        try:
            password_ok = Argon2PasswordHasher().verify_password(password, stored_hash)
        except Exception as e:
            logger.error("password verification errored for manager %s: %s", login_id, e)
            raise generic_failure

        if not password_ok:
            logger.info("login refused: wrong password for manager %s", login_id)
            raise generic_failure

        role_str = getattr(manager.role, "value", str(manager.role)).lower() if hasattr(manager, "role") else "manager"
        access_token = create_access_token(data={
            "sub": str(manager.login),
            "role": role_str,
            "is_manager": True
        })
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400
        )

    logger.info("login refused: unknown account/manager login_id %s", login_id)
    raise generic_failure
