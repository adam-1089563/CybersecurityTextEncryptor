import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_text(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(plaintext.encode())
    # Voeg salt en ciphertext samen, salt is geen geheim en kan samen met de ciphertext worden opgeslagen/verzonden
    return base64.urlsafe_b64encode(salt).decode() + ":" + token.decode()

def decrypt_text(ciphertext_with_salt: str, password: str) -> str:
    salt_b64, token = ciphertext_with_salt.split(":", 1)
    salt = base64.urlsafe_b64decode(salt_b64)
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()