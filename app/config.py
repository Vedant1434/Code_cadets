import secrets
from cryptography.fernet import Fernet

class Settings:
    def __init__(self):
        self.SECRET_KEY: str = secrets.token_hex(32)
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
        self.DATABASE_URL: str = "sqlite:///./clinicvault.db"
        
        # Simulating a Key Management Service (KMS) for PHI encryption
        self.ENCRYPTION_KEY: bytes = Fernet.generate_key()

settings = Settings()