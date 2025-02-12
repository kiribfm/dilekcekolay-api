import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.database import get_db
from app.schemas.petition import PetitionCreate, PetitionResponse, PetitionRequest
from app.core.ai_handler import AIHandler
from app.core.pdf_generator import PDFGenerator
from app.db import models
from app.core.security import get_current_user
from app.core.exceptions import (
    AIServiceError,
    PremiumRequiredError,
    DatabaseError,
    AuthorizationError,
    ValidationError,
    get_error_message
)
from app.core.logger import api_logger

router = APIRouter()

# Singleton instances
ai_handler = AIHandler()
pdf_generator = PDFGenerator()

# Constants
PDF_DIR = "temp_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def get_petition_by_id(db: Session, petition_id: int) -> models.Petition:
    """Veritabanından ID ile dilekçe bulur"""
    return db.query(models.Petition).filter(models.Petition.id == petition_id).first()

@router.post("/generate", response_model=PetitionResponse, status_code=status.HTTP_201_CREATED)
async def generate_petition(
    petition: PetitionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yeni dilekçe oluşturur ve veritabanına kaydeder.
    
    Args:
        petition: Dilekçe bilgileri
        current_user: Aktif kullanıcı
        db: Veritabanı oturumu
    
    Returns:
        Oluşturulan dilekçe
    
    Raises:
        HTTPException: AI servisi veya veritabanı hatası
    """
    if not current_user.is_premium:
        api_logger.warning("Non-premium user attempted to generate petition", user_id=current_user.id)
        raise PremiumRequiredError(detail=get_error_message("PREMIUM_REQUIRED"))
    
    try:
        api_logger.info("Starting petition generation", user_id=current_user.id, type=petition.petition_type)
        content = ai_handler.generate_petition(
            petition_type=petition.petition_type,
            data={
                "full_name": petition.full_name,
                "id_number": petition.id_number,
                "incident_date": petition.incident_date,
                "incident_details": petition.incident_details
            }
        )
        
        db_petition = models.Petition(
            petition_type=petition.petition_type,
            content=content,
            user_id=current_user.id
        )
        db.add(db_petition)
        db.commit()
        db.refresh(db_petition)
        
        api_logger.info("Petition generated successfully", petition_id=db_petition.id)
        return db_petition
    except Exception as e:
        db.rollback()
        api_logger.error("Petition generation failed", user_id=current_user.id, error=str(e))
        raise AIServiceError(detail=get_error_message("AI_SERVICE_ERROR"))

@router.get("/list", response_model=List[PetitionResponse])
async def list_petitions(
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının dilekçelerini listeler.
    
    Args:
        skip: Atlanacak kayıt sayısı
        limit: Maksimum kayıt sayısı
        current_user: Aktif kullanıcı
        db: Veritabanı oturumu
    
    Returns:
        Dilekçe listesi
    """
    try:
        api_logger.info(
            "Listing petitions",
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        petitions = db.query(models.Petition)\
            .filter(models.Petition.user_id == current_user.id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        api_logger.info(
            "Petitions listed successfully",
            user_id=current_user.id,
            count=len(petitions)
        )
        return petitions
    except Exception as e:
        api_logger.error(
            "Failed to list petitions",
            user_id=current_user.id,
            error=str(e)
        )
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR"))

@router.get("/{petition_id}/pdf")
async def get_petition_pdf(
    petition_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dilekçenin PDF versiyonunu oluşturur ve döndürür.
    
    Args:
        petition_id: Dilekçe ID
        current_user: Aktif kullanıcı
        db: Veritabanı oturumu
    
    Returns:
        PDF dosyası
    
    Raises:
        HTTPException: Dilekçe bulunamadı veya PDF oluşturma hatası
    """
    try:
        petition = get_petition_by_id(db, petition_id)
        if not petition:
            api_logger.warning("Petition not found", petition_id=petition_id)
            raise ValidationError(detail=get_error_message("PETITION_NOT_FOUND"))
        
        if petition.user_id != current_user.id:
            api_logger.warning(
                "Unauthorized petition access attempt",
                user_id=current_user.id,
                petition_id=petition_id
            )
            raise AuthorizationError(detail=get_error_message("UNAUTHORIZED_ACCESS"))
        
        api_logger.info("Generating PDF", petition_id=petition_id)
        pdf_path = os.path.join(PDF_DIR, f"dilekce_{petition_id}.pdf")
        
        try:
            pdf_generator.create_pdf(petition.content, pdf_path)
        except Exception:
            raise AIServiceError(detail=get_error_message("PDF_GENERATION_ERROR"))
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"dilekce_{petition_id}.pdf"
        )
    except Exception as e:
        api_logger.error("PDF generation failed", petition_id=petition_id, error=str(e))
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR")) 