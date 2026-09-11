"""
TOTP 2FA Service implementation using pyotp.
"""
import pyotp
from typing import Optional
from core.ports.interfaces import ITwoFactorService


class TOTPService(ITwoFactorService):
    """
    Time-based One-Time Password (TOTP) adapter for Google Authenticator / Authy.
    """

    def generate_secret(self) -> str:
        """Generates a cryptographically random base32 secret."""
        return pyotp.random_base32()

    def get_provisioning_uri(
        self,
        secret: str,
        account_name: str,
        issuer_name: str = "BrokerPlatform"
    ) -> str:
        """Generates the otpauth:// URI for rendering QR codes."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=account_name, issuer_name=issuer_name)

    def verify_code(self, secret: str, code: str) -> bool:
        """
        Verifies a 6-digit TOTP code against the secret.
        Allows a 30-second clock skew window (valid_window=1).
        """
        if not secret or not code:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code.strip(), valid_window=1)
