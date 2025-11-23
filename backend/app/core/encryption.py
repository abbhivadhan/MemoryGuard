"""
Utilities for field-level encryption of sensitive data.
"""
from __future__ import annotations

import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import String, TypeDecorator

from app.core.config import settings

logger = logging.getLogger(__name__)

_fallback_key: Optional[bytes] = None


def _resolve_key(explicit_key: Optional[str]) -> bytes:
    """
    Resolve encryption key from explicit value or settings, falling back to generated key.
    """
    global _fallback_key

    candidate = explicit_key or settings.DATA_ENCRYPTION_KEY or settings.IMAGING_ENCRYPTION_KEY

    if candidate:
        return candidate.encode() if isinstance(candidate, str) else candidate

    if _fallback_key is None:
        _fallback_key = Fernet.generate_key()
        logger.warning(
            "DATA_ENCRYPTION_KEY not provided; using ephemeral key. "
            "Encrypted fields will not survive restarts. Configure DATA_ENCRYPTION_KEY for production."
        )

    return _fallback_key


class FieldEncryptionManager:
    """
    Simple helper around Fernet symmetric encryption for string fields.
    """

    def __init__(self, key: Optional[str] = None):
        resolved_key = _resolve_key(key)
        self._cipher = Fernet(resolved_key)

    def encrypt(self, value: str) -> str:
        """
        Encrypt a string value, returning a base64-encoded string suitable for DB storage.
        """
        if value is None:
            return value
        if not isinstance(value, str):
            value = str(value)
        token = self._cipher.encrypt(value.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt(self, value: str) -> str:
        """
        Decrypt a previously encrypted string value.
        """
        if value is None:
            return value
        try:
            decrypted = self._cipher.decrypt(value.encode("utf-8"))
            return decrypted.decode("utf-8")
        except (InvalidToken, ValueError) as exc:
            # Existing plaintext values should remain readable; log and return original.
            logger.warning("Failed to decrypt field; returning original value. Error: %s", exc)
            return value


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy type decorator that transparently encrypts/decrypts string columns.
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 512, key: Optional[str] = None, **kwargs):
        self._manager = FieldEncryptionManager(key=key)
        super().__init__(length=length, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return self._manager.encrypt(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return self._manager.decrypt(value)


__all__ = ["FieldEncryptionManager", "EncryptedString"]



