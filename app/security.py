from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from sqlmodel import Session, select

from app.config import settings
from app.database import get_db
from app.models import User, PrivacyLog, UserRole

# Encryption Suite
cipher_suite = Fernet(settings.ENCRYPTION_KEY)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Encryption Utils ---
def encrypt_phi(data: str) -> str:
    if not data: return ""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_phi(token: str) -> str:
    if not token: return ""
    try:
        return cipher_suite.decrypt(token.encode()).decode()
    except:
        return "[DATA CORRUPTION ERROR]"

# --- Auth Utils ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    
    user = session.exec(select(User).where(User.email == email)).first()
    if not user: raise HTTPException(status_code=401)
    return user

def audit_log(session: Session, actor: User, action: str, target: str, purpose: str, consult_id: Optional[int] = None):
    log = PrivacyLog(
        consultation_id=consult_id,
        actor_id=actor.id,
        actor_name=f"{actor.full_name} ({actor.role.value})",
        action=action,
        target_data=target,
        purpose=purpose
    )
    session.add(log)
    session.commit()