from cryptography.fernet import Fernet
import os

def get_encryption_key():
    key = os.getenv("PAI_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("Encryption key not set in PAI_ENCRYPTION_KEY")
    return key.encode()

def encrypt_api_key(api_key):
    f = Fernet(get_encryption_key())
    return f.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted):
    f = Fernet(get_encryption_key())
    return f.decrypt(encrypted.encode()).decode()