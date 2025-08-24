from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

from typing import Union

from app.core.config import settings

# This module provides encryption and decryption services using the Fernet symmetric encryption algorithm.
# It allows for encrypting and decrypting strings, rotating encryption keys, and manually setting a new key.

class BaseEncryption:
    
    def __init__(self, algo: str = "fernet", key: Union[str, None] = None):
        if algo.lower() != "fernet":
            raise ValueError("Only 'fernet' algorithm is supported in this implementation.")
        
        if key is None:
            key = settings.encryption_key
            
        self.key = key
        self.algo = algo.lower()
        self.create_cipher()
    
    def create_cipher(self, nonce = None):
        if self.algo == "fernet":
            self.cipher = Fernet(self.key)
            return self.cipher
        elif self.algo == "aes-gcm":
            nonce = get_random_bytes(16) if nonce is None else nonce
            self.cipher = AES.new(key=self.key.encode(), mode=AES.MODE_GCM, nonce=nonce)
            self.nonce = nonce
            return self.cipher
        elif self.algo == "aes-cbc":
            self.cipher = AES.new(key=self.key.encode(), mode=AES.MODE_ECB)
            return self.cipher
        
    
    def encrypt(self, data: str):
        """Encrypt the data using the factory keys"""
        cipher = self.cipher
        nonce = self.nonce
        if not cipher:
            raise ValueError("Cipher is failed to create.")
        # Check fo the data
        if not isinstance(data, str):
            raise ValueError("Data must be a string.")
        if not data:
            raise ValueError("Data cannot be empty.")
        if self.algo == "fernet":
            return cipher.encrypt(data.encode())
        elif self.algo == "aes-gcm":
            ciphertext, tag = cipher.encrypt_and_digest(data.encode())
            return ciphertext, nonce, tag
        elif self.algo == "aes-cbc":
            pass
    
    def decrypt(self, data: str, nonce: Union[bytes, None] = None, tag: Union[bytes, None] = None):
        """Decrypt the data using the factory keys"""
        cipher = self.create_cipher(nonce=nonce)
        if not cipher:
            raise ValueError("Cipher is failed to create.")
        # Check fo the data
        if not isinstance(data, str):
            raise ValueError("Data must be a string.")
        if not data:
            raise ValueError("Data cannot be empty.")
        if self.algo == "fernet":
            return cipher.decrypt(data.encode()).decode()
        elif self.algo == "aes-gcm":
            return cipher.decrypt_and_verify(data, nonce, tag).decode()
        elif self.algo == "aes-cbc":
            pass
         
        

class EcryptionService:
    def __init__(self, key: Union[str, None] = None, algo: str = "fernet"):
        if key is None:
            key = settings.encryption_key
            
        self.cipher = Fernet(key)
        self.key = key
        
    def encrypt(self, data: str) -> str:
        """Encrypt the data using the factory keys"""
        if not isinstance(data, str):
            raise ValueError("Data must be a string.")
        if not data:
            raise ValueError("Data cannot be empty.")
        encrypted_data = self.cipher.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt(self, data: str) -> str:
        """Decrypt the data using the factory keys"""
        if not isinstance(data, str):
            raise ValueError("Data must be a string.")
        if not data:
            raise ValueError("Data cannot be empty.")
        decrypted_byte_data = self.cipher.decrypt(data.encode())
        return decrypted_byte_data.decode()
    
    def rotate_key(self) -> str:
        """Rotate the new key for the factory"""
        new_key = Fernet.generate_key().decode()
        self.set_key(new_key)
        return new_key
    
    def set_key(self, key: str) -> None:
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not key:
            raise ValueError("Key cannot be empty")
        self.cipher = Fernet(key)
        self.key = key
    
    def change_manual_key(self, key: Union[str, None] = None) -> str:
        """Change the encryption key manually"""
        if key is None:
            key = self.rotate_key()
        else:
            self.set_key(key)
        return key   
        


class EncryptAESGCM(BaseEncryption):
    def __init__(self, key = None):
        self.algo = "aes-gcm"
        super().__init__("aes-gcm", key)
        
    
class EncryptFernet(BaseEncryption):
    def __init__(self, key = None):
        algo = "fernet"
        super().__init__(algo, key)
        
    
class EncryptAESCBC(BaseEncryption):
    def __init__(self, key = None):
        self.algo = "aes-cbc"
        super().__init__("aes-cbc", key)