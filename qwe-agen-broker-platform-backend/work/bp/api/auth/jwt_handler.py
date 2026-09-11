"""
JWT Token Handler

Encodes and decodes JSON Web Tokens (JWT) for authenticating client API calls and WebSockets.

Architectural Rule: Pure authentication utility.

M5: the signing key comes from the environment. The pre-M5 module-level constant
was a hardcoded string committed to the repository; it is now a fail-hard lookup,
so a missing or placeholder SECRET_KEY raises at first use with the fix named,
instead of silently signing tokens everyone can forge.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import jwt

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

#: The pre-M5 hardcoded secret. Kept only so it can be recognised and refused.
_FORBIDDEN_KEY = "BROKER_PLATFORM_SECRET_KEY_CHANGE_IN_PRODUCTION"


def _secret_key() -> str:
    """Read the JWT signing key from the environment, or refuse to operate."""
    key = os.environ.get("SECRET_KEY")
    if not key or key == _FORBIDDEN_KEY:
        raise RuntimeError(
            "SECRET_KEY is not set (or is the old hardcoded placeholder). Set it in .env: "
            "python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if len(key) < 32:
        raise RuntimeError("SECRET_KEY must be at least 32 characters")
    return key


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _secret_key(), algorithm=ALGORITHM)


def verify_token(token: str) -> Dict:
    """Decode and verify a JWT token. Raises ValueError on failure or expiration."""
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])
        login_id: str = payload.get("sub")
        if not login_id:
            raise ValueError("Invalid token payload: missing sub claim")
        return payload
    except RuntimeError:
        raise  # configuration errors must not be masked as token errors
    except Exception as e:
        raise ValueError(f"Could not validate JWT token: {e}")
