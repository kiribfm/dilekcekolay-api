from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    """Temel kullanıcı şeması"""
    email: EmailStr = Field(..., description="Kullanıcı email adresi")
    full_name: str = Field(..., min_length=2, max_length=100, description="Ad Soyad")

    @validator('full_name')
    def validate_full_name(cls, v):
        """Ad Soyad doğrulama"""
        if not all(part.isalpha() or part.isspace() for part in v):
            raise ValueError("Ad Soyad sadece harf ve boşluk içerebilir")
        return v.title()

class UserCreate(UserBase):
    """Kullanıcı oluşturma şeması"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Şifre (en az 8 karakter)"
    )

    @validator('password')
    def validate_password(cls, v):
        """Şifre karmaşıklık kontrolü"""
        if not any(c.isupper() for c in v):
            raise ValueError("Şifre en az bir büyük harf içermelidir")
        if not any(c.islower() for c in v):
            raise ValueError("Şifre en az bir küçük harf içermelidir")
        if not any(c.isdigit() for c in v):
            raise ValueError("Şifre en az bir rakam içermelidir")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Şifre en az bir özel karakter içermelidir")
        return v

class UserUpdate(BaseModel):
    """Kullanıcı güncelleme şeması"""
    email: Optional[EmailStr] = Field(None, description="Yeni email adresi")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = Field(None, description="Kullanıcı durumu")

    @validator('password')
    def validate_password(cls, v):
        """Şifre karmaşıklık kontrolü"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Şifre en az 8 karakter olmalıdır")
        if not any(c.isupper() for c in v):
            raise ValueError("Şifre en az bir büyük harf içermelidir")
        if not any(c.islower() for c in v):
            raise ValueError("Şifre en az bir küçük harf içermelidir")
        if not any(c.isdigit() for c in v):
            raise ValueError("Şifre en az bir rakam içermelidir")
        return v

class User(UserBase):
    """Kullanıcı yanıt şeması"""
    id: int
    is_active: bool = Field(default=True, description="Kullanıcı aktif mi")
    is_premium: bool = Field(default=False, description="Premium üyelik durumu")
    premium_until: Optional[datetime] = Field(None, description="Premium üyelik bitiş tarihi")
    created_at: datetime = Field(..., description="Kayıt tarihi")

    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserInDB(User):
    """Veritabanı kullanıcı şeması"""
    hashed_password: str = Field(..., description="Hash'lenmiş şifre")

    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
