from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.db import models
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    get_error_message
)
from app.core.logger import auth_logger

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Şifre doğrulama.

    Args:
        plain_password: Ham şifre
        hashed_password: Hash'lenmiş şifre

    Returns:
        bool: Şifre doğru mu
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Şifreyi hash'ler.

    Args:
        password: Ham şifre

    Returns:
        str: Hash'lenmiş şifre
    """
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Access token oluşturur.

    Args:
        data: Token payload
        expires_delta: Geçerlilik süresi

    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access_token"
    })
    
    auth_logger.info("Creating access token", user_email=data.get("sub"))
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Token'dan kullanıcıyı bulur.

    Args:
        token: JWT token
        db: Veritabanı oturumu

    Returns:
        User: Kullanıcı modeli

    Raises:
        AuthenticationError: Geçersiz token
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            auth_logger.warning("Token missing email claim")
            raise AuthenticationError(detail=get_error_message("INVALID_TOKEN"))
        
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            auth_logger.warning("User not found", email=email)
            raise AuthenticationError(detail=get_error_message("USER_NOT_FOUND"))
        
        auth_logger.info("User authenticated", user_id=user.id)
        return user
        
    except JWTError as e:
        auth_logger.error("JWT decode error", error=str(e))
        raise AuthenticationError(detail=get_error_message("INVALID_TOKEN"))

async def check_premium_status(user: models.User, db: Session) -> models.User:
    """
    Premium durumunu kontrol eder.

    Args:
        user: Kullanıcı modeli
        db: Veritabanı oturumu

    Returns:
        User: Güncellenmiş kullanıcı modeli
    """
    try:
        if user.is_premium and user.premium_until:
            if user.premium_until < datetime.utcnow():
                user.is_premium = False
                user.premium_until = None
                db.commit()
                auth_logger.info("Premium status expired", user_id=user.id)
            else:
                auth_logger.info("Premium status active", user_id=user.id)
        return user
    except Exception as e:
        auth_logger.error("Premium status check failed", user_id=user.id, error=str(e))
        db.rollback()
        return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Aktif kullanıcı kontrolü.
    
    Args:
        current_user: Aktif kullanıcı
    
    Returns:
        User: Aktif kullanıcı
    
    Raises:
        AuthenticationError: Kullanıcı inaktif
    """
    if not current_user.is_active:
        raise AuthenticationError(detail=get_error_message("INACTIVE_USER"))
    return current_user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> models.User:
    """Aktif ve premium durumu güncel kullanıcıyı döndürür"""
    return await check_premium_status(current_user, db) 