"""
Trading212 Smart Bot - Security Utilities
Encryption/decryption for API keys and sensitive data
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from loguru import logger

from app.core.config import settings


def get_encryption_key() -> bytes:
    """Derive encryption key from settings"""
    # In production, use a proper secrets manager
    salt = b'trading212_smart_bot_salt_v1'  # Should be randomly generated and stored
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(settings.ENCRYPTION_KEY.encode()))
    return key


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt API key using Fernet symmetric encryption
    
    Args:
        api_key: Plain text API key
    
    Returns:
        Encrypted API key (base64 encoded)
    """
    try:
        f = Fernet(get_encryption_key())
        encrypted = f.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Error encrypting API key: {e}")
        raise


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt API key
    
    Args:
        encrypted_key: Encrypted API key (base64 encoded)
    
    Returns:
        Decrypted plain text API key
    """
    try:
        f = Fernet(get_encryption_key())
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Error decrypting API key: {e}")
        raise


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    from passlib.hash import bcrypt
    return bcrypt.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    from passlib.hash import bcrypt
    return bcrypt.verify(password, hashed)


def generate_license_key(tier: str = "pro") -> str:
    """
    Generate a license key for one-time purchase
    
    Format: T212-{TIER}-{RANDOM}-{CHECKSUM}
    """
    import random
    import hashlib
    
    tier_codes = {
        "basic": "BASIC",
        "pro": "PRO",
        "enterprise": "ENT"
    }
    
    tier_code = tier_codes.get(tier.lower(), "PRO")
    random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    
    # Generate checksum
    checksum_input = f"T212-{tier_code}-{random_part}"
    checksum = hashlib.md5(checksum_input.encode()).hexdigest()[:8].upper()
    
    return f"{checksum_input}-{checksum}"


# Test encryption
if __name__ == "__main__":
    test_key = "t212_test_api_key_12345"
    encrypted = encrypt_api_key(test_key)
    print(f"Original: {test_key}")
    print(f"Encrypted: {encrypted}")
    decrypted = decrypt_api_key(encrypted)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_key == decrypted}")
