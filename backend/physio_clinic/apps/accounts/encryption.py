# backend/physio_clinic/apps/accounts/encryption.py
"""
Field-level encryption for sensitive patient data.
Uses Fernet (AES-128-CBC + HMAC-SHA256). Supports multiple comma-separated
keys via MultiFernet for zero-downtime key rotation (first key encrypts,
all keys are tried on decrypt).
"""
import logging
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

logger = logging.getLogger('physio_clinic')

_fernet = None


def get_fernet():
    global _fernet
    if _fernet is not None:
        return _fernet

    raw = getattr(settings, 'ENCRYPTION_KEY', '') or ''
    keys = [k.strip() for k in raw.split(',') if k.strip()]

    if not keys:
        if settings.DEBUG:
            logger.warning('ENCRYPTION_KEY not set — patient data will NOT be encrypted (DEBUG only).')
            return None
        # Never allow a production/staging boot with encryption silently disabled.
        raise ImproperlyConfigured(
            'ENCRYPTION_KEY must be set when DEBUG=False. '
            'Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )

    _fernet = MultiFernet([Fernet(k.encode()) for k in keys])
    return _fernet


def encrypt(value: str) -> str:
    if not value:
        return value
    f = get_fernet()
    if f is None:
        return value
    return f.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt(token: str) -> str:
    if not token:
        return token
    f = get_fernet()
    if f is None:
        return token
    try:
        return f.decrypt(token.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        # Don't silently return '' — that looks identical to "no data" and
        # has previously meant a wrong/rotated key quietly destroyed data on
        # the next save. Surface it instead.
        logger.error('Decryption failed for a PatientProfile field — wrong or rotated ENCRYPTION_KEY?')
        raise


class EncryptedField(models.TextField):
    def from_db_value(self, value, expression, connection):
        return decrypt(value) if value else value

    def to_python(self, value):
        # IMPORTANT: do not decrypt here. Django calls to_python() during
        # full_clean() (e.g. from the admin) on values that are already
        # plaintext in memory — decrypting them a second time returned ''
        # and silently blanked patient data on save.
        return value

    def get_prep_value(self, value):
        return encrypt(value) if value else value