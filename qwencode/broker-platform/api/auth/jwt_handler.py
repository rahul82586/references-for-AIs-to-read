"""
JWT Token Handler

Encodes and decodes JSON Web Tokens (JWT) for authenticating client API calls and WebSockets.

Architectural Rule: Pure authentication utility.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import jwt

SECRET_KEY = "BROKER_PLATFORM_SECRET_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Dict:
    """Decode and verify a JWT token. Raises ValueError on failure or expiration."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login_id: str = payload.get("sub")
        if not login_id:
            raise ValueError("Invalid token payload: missing sub claim")
        return payload
    except Exception as e:
        raise ValueError(f"Could not validate JWT token: {e}")
