"""
Argon2id Password Hasher implementation.
"""
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

logger = logging.getLogger(__name__)


class Argon2PasswordHasher:
    """
    Argon2id password hashing adapter conforming to OWASP recommendations.
    Uses time_cost=3, memory_cost=65536 (64MB), parallelism=4.
    """

    def __init__(self, time_cost: int = 3, memory_cost: int = 65536, parallelism: int = 4):
        self._ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism
        )

    def hash_password(self, password: str) -> str:
        """Hashes plain password using Argon2id."""
        return self._ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies plain password against stored hash."""
        try:
            return self._ph.verify(hashed_password, password)
        except (VerifyMismatchError, InvalidHashError):
            return False
        except Exception as e:
            logger.error(f"Unexpected password verification error: {e}")
            return False
