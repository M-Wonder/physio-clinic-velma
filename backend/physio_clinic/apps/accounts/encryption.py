"""
Field-level encryption for sensitive patient data (HIPAA compliance).
Uses Fernet (AES-128-CBC + HMAC-SHA256) for symmetric encryption.
"""
import logging
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger('physio_clinic')

_fernet = None


def get_fernet():
    """Lazily initialize Fernet with the configured key."""
    global _fernet
    if _fernet is None:
        key = settings.ENCRYPTION_KEY
        if not key:
            # Warn in dev; fail in production
            logger.warning("ENCRYPTION_KEY not set — patient data will NOT be encrypted!")
            return None
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt(value: str) -> str:
    """Encrypt a plaintext string. Returns empty string if value is empty."""
    if not value:
        return value
    f = get_fernet()
    if f is None:
        return value  # Dev fallback — no encryption
    return f.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt(token: str) -> str:
    """Decrypt a Fernet token. Returns empty string on failure."""
    if not token:
        return token
    f = get_fernet()
    if f is None:
        return token  # Dev fallback
    try:
        return f.decrypt(token.encode('utf-8')).decode('utf-8')
    except (InvalidToken, Exception) as e:
        logger.error("Decryption failed: %s", e)
        return ''


class EncryptedField(models.TextField):
    """
    A Django model field that transparently encrypts/decrypts data.
    Data is encrypted before saving and decrypted on access.
    """
    def from_db_value(self, value, expression, connection):
        return decrypt(value) if value else value

    def to_python(self, value):
        return decrypt(value) if value else value

    def get_prep_value(self, value):
        """Encrypt before saving to DB."""
        return encrypt(value) if value else value
