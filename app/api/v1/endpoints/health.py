from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db, check_db_connection
from app.core.logger import api_logger
from typing import Dict

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Sistem sağlık durumunu kontrol eder.
    
    Returns:
        Dict: Servis durumları
    """
    try:
        # Database bağlantısını kontrol et
        db_status = "healthy" if check_db_connection() else "unhealthy"
        
        # Disk alanını kontrol et
        import shutil
        total, used, free = shutil.disk_usage("/")
        disk_usage = (used / total) * 100
        disk_status = "healthy" if disk_usage < 90 else "warning"
        
        api_logger.info(
            "Health check performed",
            db_status=db_status,
            disk_usage=f"{disk_usage:.1f}%"
        )
        
        return {
            "status": "ok",
            "database": db_status,
            "disk": disk_status,
            "disk_usage": f"{disk_usage:.1f}%"
        }
        
    except Exception as e:
        api_logger.error("Health check failed", error=str(e))
        return {
            "status": "error",
            "message": str(e)
        } 