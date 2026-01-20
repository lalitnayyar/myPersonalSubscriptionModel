"""Encryption service for secure credential storage."""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""

    _fernet = None

    @classmethod
    def _get_fernet(cls):
        """Get or create Fernet instance."""
        if cls._fernet is None:
            key = cls._derive_key()
            cls._fernet = Fernet(key)
        return cls._fernet

    @classmethod
    def _derive_key(cls):
        """Derive encryption key from config."""
        password = current_app.config.get('ENCRYPTION_KEY', 'default-key').encode()
        # Use a fixed salt for consistency (in production, consider user-specific salts)
        salt = b'subscriptionm_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    @classmethod
    def encrypt(cls, plaintext):
        """Encrypt a string."""
        if not plaintext:
            return None
        try:
            fernet = cls._get_fernet()
            encrypted = fernet.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception:
            return None

    @classmethod
    def decrypt(cls, ciphertext):
        """Decrypt a string."""
        if not ciphertext:
            return None
        try:
            fernet = cls._get_fernet()
            decrypted = fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception:
            return None


def encrypt_credential(value):
    """Helper function to encrypt a credential."""
    return EncryptionService.encrypt(value)


def decrypt_credential(value):
    """Helper function to decrypt a credential."""
    return EncryptionService.decrypt(value)
