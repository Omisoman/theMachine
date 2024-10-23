import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from google.cloud import secretmanager
import base64

def get_secret(secret_name):
    """Retrieve the secret value from Google Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.getenv('PROJECT_ID')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def get_secure_key():
    """Retrieve the secure key from Secret Manager"""
    return get_secret('SECURE_KEY')

def derive_aes_key(secure_key):
    """Derive a 256-bit AES key from the secure key"""
    return hashlib.sha256(secure_key.encode()).digest()


# Token encryption (as you have it now)
def encrypt_data(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    if isinstance(data, str):
        data = data.encode('utf-8')  # Handle as a string

    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode('utf-8')


def decrypt_data(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))  # Decode back to bytes
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()  # Return decrypted bytes

# File encryption (binary handling for files)
def encrypt_file_data(file_data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    encrypted_data = encryptor.update(file_data) + encryptor.finalize()
    return iv + encrypted_data  # Return the IV and encrypted binary data

def decrypt_file_data(encrypted_file_data, key):
    iv = encrypted_file_data[:16]
    encrypted_file_data = encrypted_file_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_file_data) + decryptor.finalize()  # Return decrypted binary data

