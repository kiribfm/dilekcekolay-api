from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.schemas.petition import PetitionType
from datetime import datetime
from typing import Optional

class User(Base):
    """Kullanıcı modeli"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # İlişkiler
    petitions = relationship("Petition", back_populates="user", cascade="all, delete-orphan")

    def is_premium_active(self) -> bool:
        """Premium üyelik durumunu kontrol eder"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return False
        return self.premium_until > datetime.utcnow()

    def update_premium_status(self) -> None:
        """Premium durumunu günceller"""
        if self.is_premium and self.premium_until:
            if self.premium_until < datetime.utcnow():
                self.is_premium = False
                self.premium_until = None

    def to_dict(self) -> dict:
        """Kullanıcı bilgilerini sözlük olarak döndürür"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "premium_until": self.premium_until,
            "created_at": self.created_at
        }

class Petition(Base):
    """Dilekçe modeli"""
    __tablename__ = "petitions"

    id = Column(Integer, primary_key=True, index=True)
    petition_type = Column(SQLEnum(PetitionType), nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String, default="draft")  # draft, submitted, approved, rejected
    pdf_path = Column(String, nullable=True)

    # İlişkiler
    user = relationship("User", back_populates="petitions")

    def to_dict(self) -> dict:
        """Dilekçe bilgilerini sözlük olarak döndürür"""
        return {
            "id": self.id,
            "petition_type": self.petition_type.value,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "pdf_path": self.pdf_path
        }

    def update_status(self, new_status: str) -> None:
        """
        Dilekçe durumunu günceller.
        
        Args:
            new_status: Yeni durum
        """
        valid_statuses = {"draft", "submitted", "approved", "rejected"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def set_pdf_path(self, path: Optional[str]) -> None:
        """
        PDF dosya yolunu ayarlar.
        
        Args:
            path: PDF dosya yolu
        """
        self.pdf_path = path
        self.updated_at = datetime.utcnow() 