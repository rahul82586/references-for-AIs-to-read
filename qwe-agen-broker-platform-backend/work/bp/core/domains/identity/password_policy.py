"""MT5's password rule, as one pure module.

Administrator guide, Accounts → Creating/Editing an account, Passwords box:

    Four character classes - lowercase, uppercase, digit and a symbol
    ('# @ ! ...'), e.g. '1Ar#pqkj'. The minimum length comes from the GROUP
    setting (AuthPasswordMin) with a platform floor of 8; the maximum is 16.
    Changing a password resets the account's connection to the trade server.

Pure by design: no DB, no DI, no infrastructure imports at module load. Callers
pass the group's ``auth_password_min`` in; handlers own the "reset the
connection" side effect. The optional hash/verify wrappers take any hasher with
``hash_password``/``verify_password`` (the platform's Argon2PasswordHasher has
exactly those), and the no-argument convenience form lazy-imports it so this
module never drags infrastructure into the domain at import time.
"""
from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from typing import List, Optional

#: MT5's platform bounds. The group may raise the minimum; nothing may raise the
#: maximum past 16 or lower it past 8.
PASSWORD_MIN_LENGTH_FLOOR = 8
PASSWORD_MAX_LENGTH = 16

#: The symbol class. MT5's own examples use '#@!'; we accept any non-alphanumeric
#: printable character, which is a superset and never rejects a password MT5
#: would accept.
_SYMBOLS = "#@!$%^&*()-_=+[]{};:,.<>/?~|\\`'\" " + string.punctuation
_SYMBOL_SET = frozenset(c for c in _SYMBOLS if not c.isalnum())

#: Default generated-password length: comfortably inside 8..16 with all classes.
DEFAULT_GENERATED_LENGTH = 12


class PasswordPolicyError(ValueError):
    """A password MT5 would refuse. ``reasons`` carries EVERY violation, so the
    UI can show them all at once instead of one per submit."""

    def __init__(self, reasons: List[str]) -> None:
        self.reasons = list(reasons)
        super().__init__("invalid password: " + "; ".join(self.reasons))


@dataclass(frozen=True)
class PasswordPolicy:
    """The effective policy for one group.

    ``min_length`` is the group's AuthPasswordMin, clamped into MT5's 8..16
    window at construction - a group exported with AuthPasswordMin 6 still gets
    the platform floor of 8, and a corrupt 40 becomes 16 rather than making
    every password invalid.
    """

    min_length: int = PASSWORD_MIN_LENGTH_FLOOR
    max_length: int = PASSWORD_MAX_LENGTH

    def __post_init__(self) -> None:
        lo = max(PASSWORD_MIN_LENGTH_FLOOR, min(int(self.min_length or 0), PASSWORD_MAX_LENGTH))
        hi = max(lo, min(int(self.max_length or PASSWORD_MAX_LENGTH), PASSWORD_MAX_LENGTH))
        object.__setattr__(self, "min_length", lo)
        object.__setattr__(self, "max_length", hi)

    @classmethod
    def for_group(cls, auth_password_min: Optional[int]) -> "PasswordPolicy":
        """Build from a group's AuthPasswordMin (None/0 -> the floor of 8)."""
        return cls(min_length=int(auth_password_min or PASSWORD_MIN_LENGTH_FLOOR))

    # -- validation ----------------------------------------------------------

    def violations(self, password: str) -> List[str]:
        """Every rule this password breaks, in the order the UI should show them."""
        reasons: List[str] = []
        text = password if isinstance(password, str) else ""
        if len(text) < self.min_length:
            reasons.append(f"shorter than the minimum of {self.min_length} characters")
        if len(text) > self.max_length:
            reasons.append(f"longer than the maximum of {PASSWORD_MAX_LENGTH} characters")
        if not any(c.islower() for c in text):
            reasons.append("no lowercase letter")
        if not any(c.isupper() for c in text):
            reasons.append("no uppercase letter")
        if not any(c.isdigit() for c in text):
            reasons.append("no digit")
        if not any(c in _SYMBOL_SET for c in text):
            reasons.append("no symbol (e.g. # @ !)")
        if text and text.isascii() is False:
            # MT5 accepts what the terminal sends, but a non-ASCII password is
            # near-guaranteed to be a copy/paste accident (invisible characters,
            # smart quotes). Refusing is cheaper than a locked-out client.
            reasons.append("contains non-ASCII characters")
        return reasons

    def validate(self, password: str) -> str:
        """The password, or PasswordPolicyError listing every violation."""
        reasons = self.violations(password)
        if reasons:
            raise PasswordPolicyError(reasons)
        return password

    # -- generation ----------------------------------------------------------

    def generate(self, length: int = DEFAULT_GENERATED_LENGTH) -> str:
        """A cryptographically random password that satisfies this policy.

        Guarantees one character of each class, then shuffles - so the shape
        never leaks 'first char is always uppercase' to anyone watching a
        password field. Uses ``secrets``, never ``random``.
        """
        length = max(self.min_length, min(int(length), self.max_length))
        if length < 4:  # pragma: no cover - unreachable: min_length >= 8
            raise PasswordPolicyError(["cannot fit four character classes"])
        lowers = string.ascii_lowercase
        uppers = string.ascii_uppercase
        digits = string.digits
        symbols = "".join(sorted(_SYMBOL_SET - set("'\"\\`")))  # shell-hostile set minus the worst
        alphabet = lowers + uppers + digits + symbols
        while True:
            chars = [
                secrets.choice(lowers),
                secrets.choice(uppers),
                secrets.choice(digits),
                secrets.choice(symbols),
            ]
            chars += [secrets.choice(alphabet) for _ in range(length - 4)]
            candidate = "".join(chars)
            # Fisher-Yates via secrets: do not use random.shuffle.
            for i in range(len(candidate) - 1, 0, -1):
                j = secrets.randbelow(i + 1)
                chars[i], chars[j] = chars[j], chars[i]
            candidate = "".join(chars)
            if not self.violations(candidate):
                return candidate


def default_policy() -> PasswordPolicy:
    """The platform floor policy, for callers with no group context yet."""
    return PasswordPolicy()


# ---------------------------------------------------------------------------
# Hash / verify wrappers - thin, so there is exactly ONE place that knows the
# hasher's method names (the platform's Argon2PasswordHasher exposes
# hash_password/verify_password; some test doubles expose hash/verify).
# ---------------------------------------------------------------------------

def _resolve_hasher(hasher):
    if hasher is not None:
        return hasher
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    return Argon2PasswordHasher()


def hash_password(password: str, hasher=None) -> str:
    """Argon2-hash a plaintext password. The plaintext is never stored or logged."""
    resolved = _resolve_hasher(hasher)
    fn = getattr(resolved, "hash_password", None) or getattr(resolved, "hash", None)
    if fn is None:
        raise TypeError("hasher exposes neither hash_password() nor hash()")
    return fn(password)


def verify_password(password: str, password_hash: str, hasher=None) -> bool:
    """Constant-time check against a stored hash. An EMPTY stored hash is a
    refusal, not a match - an account with no provisioned password cannot log in
    (M6's fail-closed rule, restated here so the identity plane cannot regress it)."""
    if not password_hash:
        return False
    resolved = _resolve_hasher(hasher)
    fn = getattr(resolved, "verify_password", None) or getattr(resolved, "verify", None)
    if fn is None:
        raise TypeError("hasher exposes neither verify_password() nor verify()")
    try:
        return bool(fn(password, password_hash))
    except Exception:
        # A malformed stored hash (e.g. the seeder's PLAINTEXT-REPLACE-ME marker)
        # must fail closed, not raise a 500 out of the login path.
        return False
