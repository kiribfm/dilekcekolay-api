from datetime import timedelta, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from app.core.config import settings
from app.db.database import get_db
from app.db import models
from app.schemas.user import UserCreate, User, UserUpdate
from app.schemas.token import Token
from app.core.exceptions import (
    AuthenticationError,
    ValidationError,
    DatabaseError,
    get_error_message
)
from app.core.logger import auth_logger

router = APIRouter()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Veritabanından email ile kullanıcı bulur"""
    return db.query(models.User).filter(models.User.email == email).first()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Yeni kullanıcı kaydı oluşturur.
    
    Args:
        user: Kullanıcı bilgileri
        db: Veritabanı oturumu
    
    Returns:
        Oluşturulan kullanıcı bilgileri
    
    Raises:
        HTTPException: Email zaten kayıtlı veya veritabanı hatası
    """
    if get_user_by_email(db, user.email):
        auth_logger.warning("Registration attempt with existing email", email=user.email)
        raise ValidationError(detail=get_error_message("EMAIL_EXISTS"))
    
    try:
        db_user = models.User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            full_name=user.full_name,
            is_premium=False
        )
        db.add(db_user)
        db.commit()
        auth_logger.info("User registered successfully", user_id=db_user.id)
        return db_user
    except Exception as e:
        db.rollback()
        auth_logger.error("Registration failed", error=str(e))
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR"))

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı girişi yapar ve token döndürür.
    
    Args:
        form_data: Giriş bilgileri
        db: Veritabanı oturumu
    
    Returns:
        Access token bilgileri
    
    Raises:
        HTTPException: Geçersiz kimlik bilgileri
    """
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        auth_logger.warning("Login failed", email=form_data.username)
        raise AuthenticationError(detail=get_error_message("INVALID_CREDENTIALS"))
    
    auth_logger.info("User logged in successfully", user_id=user.id)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/premium/activate", response_model=User)
async def activate_premium(
    duration_days: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Premium üyeliği aktifleştirir.
    
    Args:
        duration_days: Premium süre (gün)
        current_user: Aktif kullanıcı
        db: Veritabanı oturumu
    
    Returns:
        Güncellenmiş kullanıcı bilgileri
    
    Raises:
        HTTPException: Geçersiz süre
    """
    if duration_days < 1:
        auth_logger.warning(
            "Invalid premium duration attempt",
            user_id=current_user.id,
            duration=duration_days
        )
        raise ValidationError(detail=get_error_message("INVALID_DURATION"))
    
    try:
        current_user.is_premium = True
        current_user.premium_until = datetime.utcnow() + timedelta(days=duration_days)
        db.commit()
        db.refresh(current_user)
        auth_logger.info(
            "Premium activated successfully",
            user_id=current_user.id,
            duration_days=duration_days,
            premium_until=current_user.premium_until
        )
        return current_user
    except Exception as e:
        db.rollback()
        auth_logger.error(
            "Premium activation failed",
            user_id=current_user.id,
            error=str(e)
        )
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR"))

@router.get("/me", response_model=User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Aktif kullanıcının bilgilerini döndürür"""
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı bilgilerini günceller.
    
    Args:
        user_update: Güncellenecek bilgiler
        current_user: Aktif kullanıcı
        db: Veritabanı oturumu
    
    Returns:
        Güncellenmiş kullanıcı bilgileri
    """
    try:
        updates = {}
        if user_update.password:
            current_user.hashed_password = get_password_hash(user_update.password)
            updates["password"] = True
        if user_update.email:
            if get_user_by_email(db, user_update.email):
                auth_logger.warning(
                    "Update attempt with existing email",
                    user_id=current_user.id,
                    new_email=user_update.email
                )
                raise ValidationError(detail=get_error_message("EMAIL_EXISTS"))
            current_user.email = user_update.email
            updates["email"] = True
        if user_update.full_name:
            current_user.full_name = user_update.full_name
            updates["full_name"] = True
        
        db.commit()
        db.refresh(current_user)
        auth_logger.info(
            "User profile updated",
            user_id=current_user.id,
            updated_fields=list(updates.keys())
        )
        return current_user
    except ValidationError:
        raise
    except Exception as e:
        db.rollback()
        auth_logger.error(
            "Profile update failed",
            user_id=current_user.id,
            error=str(e)
        )
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR")) 