from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """Access token şeması"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token tipi")
    expires_at: datetime = Field(..., description="Token geçerlilik süresi")

class TokenData(BaseModel):
    """Token payload şeması"""
    email: str = Field(..., description="Kullanıcı email adresi")
    exp: datetime = Field(..., description="Token son geçerlilik tarihi")
    iat: datetime = Field(..., description="Token oluşturma tarihi")
    type: str = Field(..., description="Token tipi")
    is_premium: bool = Field(default=False, description="Premium üyelik durumu")
    premium_until: Optional[datetime] = Field(None, description="Premium üyelik bitiş tarihi")

    class Config:
        """Pydantic config"""
        json_encoders = {
            datetime: lambda v: int(v.timestamp())  # Unix timestamp formatı
        }

    def is_expired(self) -> bool:
        """Token'ın süresi dolmuş mu kontrol eder"""
        return datetime.utcnow() > self.exp

    def is_valid_type(self, expected_type: str = "access_token") -> bool:
        """Token tipini kontrol eder"""
        return self.type == expected_type

    def is_premium_active(self) -> bool:
        """Premium üyelik durumunu kontrol eder"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return False
        return datetime.utcnow() < self.premium_until

class TokenResponse(BaseModel):
    """Token yanıt şeması"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token tipi")
    expires_in: int = Field(..., description="Token geçerlilik süresi (saniye)")
    user_id: int = Field(..., description="Kullanıcı ID")
    is_premium: bool = Field(default=False, description="Premium üyelik durumu")

    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": 1,
                "is_premium": False
            }
        } 