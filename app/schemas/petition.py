from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class PetitionType(str, Enum):
    """Dilekçe tipleri"""
    CONSUMER_COMPLAINT = "consumer_complaint"
    LABOR_COMPLAINT = "labor_complaint"
    DIVORCE_PETITION = "divorce_petition"
    INHERITANCE_PETITION = "inheritance_petition"

    @classmethod
    def get_description(cls, petition_type: str) -> str:
        """Dilekçe tipi açıklamasını döndürür"""
        descriptions = {
            cls.CONSUMER_COMPLAINT: "Tüketici Şikayet Dilekçesi",
            cls.LABOR_COMPLAINT: "İş Hukuku Şikayet Dilekçesi",
            cls.DIVORCE_PETITION: "Boşanma Dilekçesi",
            cls.INHERITANCE_PETITION: "Miras Hukuku Dilekçesi"
        }
        return descriptions.get(petition_type, "Bilinmeyen Dilekçe Tipi")

class PetitionBase(BaseModel):
    """Temel dilekçe şeması"""
    petition_type: PetitionType = Field(..., description="Dilekçe tipi")
    full_name: str = Field(..., min_length=2, max_length=100, description="Ad Soyad")
    id_number: str = Field(..., min_length=11, max_length=11, description="TC Kimlik No")
    incident_date: str = Field(..., description="Olay Tarihi (YYYY-MM-DD)")
    incident_details: str = Field(..., min_length=10, description="Olay Detayları")

    @validator('id_number')
    def validate_id_number(cls, v):
        """TC Kimlik No doğrulama"""
        if not v.isdigit() or len(v) != 11:
            raise ValueError("Geçersiz TC Kimlik No formatı")
        return v

    @validator('incident_date')
    def validate_incident_date(cls, v):
        """Tarih formatı doğrulama"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError("Geçersiz tarih formatı. YYYY-MM-DD formatında olmalı")

class PetitionCreate(PetitionBase):
    """Dilekçe oluşturma şeması"""
    pass

class PetitionUpdate(BaseModel):
    """Dilekçe güncelleme şeması"""
    content: Optional[str] = Field(None, description="Dilekçe içeriği")
    status: Optional[str] = Field(None, description="Dilekçe durumu")

    @validator('status')
    def validate_status(cls, v):
        """Durum değeri doğrulama"""
        valid_statuses = {"draft", "submitted", "approved", "rejected"}
        if v not in valid_statuses:
            raise ValueError(f"Geçersiz durum. Geçerli değerler: {valid_statuses}")
        return v

class PetitionResponse(BaseModel):
    """Dilekçe yanıt şeması"""
    id: int
    petition_type: PetitionType
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    status: str = Field(default="draft")
    pdf_path: Optional[str] = None

    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PetitionRequest(BaseModel):
    """Dilekçe istek şeması"""
    petition_type: PetitionType
    data: dict = Field(..., description="Dilekçe verileri")

    @validator('data')
    def validate_data(cls, v):
        """Veri alanları doğrulama"""
        required_fields = {'full_name', 'id_number', 'incident_date', 'incident_details'}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f"Eksik alanlar: {missing_fields}")
        return v
