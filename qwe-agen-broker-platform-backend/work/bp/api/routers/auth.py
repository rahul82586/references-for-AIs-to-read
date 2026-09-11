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
    """Authenticate client login and issue a JWT access token.

    M6: the password is REQUIRED and verified. Before this, the route parsed
    login_id out of the body and issued a token for it - the `password` field
    the LoginRequest schema declared required was never read, and when no
    login_id was supplied it defaulted to "100001". Any caller who could reach
    the endpoint owned any account they could name.

    Every failure returns the SAME generic 401: an attacker must not be able to
    distinguish "no such login" from "wrong password" from "disabled" from
    "password not provisioned". The specific reason goes to the server log.
    """
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    generic_failure = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    login_id = None
    password = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            login_id = data.get("login_id") or data.get("username")
            password = data.get("password")
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            login_id = form.get("username") or form.get("login_id")
            password = form.get("password")
        except Exception:
            pass

    if not login_id:
        login_id = request.query_params.get("username")
    if not password:
        password = request.query_params.get("password")

    if not login_id or not password:
        logger.info("login refused: login_id and password are both required")
        raise generic_failure

    try:
        account_repo = get_account_repo()
    except RuntimeError:
        account_repo = None
    if account_repo is None:
        # No repository means no account can be authenticated. Refusing is the
        # only safe answer; the old code minted a token anyway.
        logger.error("login refused: no account repository is wired")
        raise generic_failure

    try:
        account = await account_repo.find_by_login(login_id)
    except Exception as e:
        logger.warning(f"Account lookup error during login: {e}")
        raise generic_failure

    if account is None:
        logger.info("login refused: unknown login_id %s", login_id)
        raise generic_failure
    if not getattr(account, "is_enabled", True):
        logger.info("login refused: account %s is disabled", login_id)
        raise generic_failure

    stored_hash = getattr(account, "password_hash", "") or ""
    if not stored_hash:
        logger.warning(
            "login refused: account %s has no password provisioned; set one via "
            "POST /api/v1/admin/accounts/set-password", login_id,
        )
        raise generic_failure

    try:
        password_ok = Argon2PasswordHasher().verify_password(password, stored_hash)
    except Exception as e:
        logger.error("password verification errored for %s: %s", login_id, e)
        raise generic_failure
    if not password_ok:
        logger.info("login refused: wrong password for %s", login_id)
        raise generic_failure

    access_token = create_access_token(data={"sub": str(login_id), "role": "client"})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400
    )
