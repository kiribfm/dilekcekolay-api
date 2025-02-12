from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middleware import setup_middlewares
from app.core.monitoring import init_monitoring
from app.api import v1_router
from app.db.database import engine
from app.db import models
from prometheus_fastapi_instrumentator import Instrumentator
import os
from app.api.v1.endpoints import health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    Startup ve shutdown işlemlerini yönetir.
    """
    # Startup
    print("Uygulama başlatılıyor...")
    if not settings.TESTING:
        try:
            print("Veritabanı kontrol ediliyor...")
            models.Base.metadata.create_all(bind=engine)
            print("Veritabanı tabloları hazır!")
        except Exception as e:
            print(f"Veritabanı hatası: {str(e)}")
    yield
    # Shutdown
    print("Uygulama kapatılıyor...")

def create_app() -> FastAPI:
    """
    FastAPI uygulamasını oluşturur ve yapılandırır.
    
    Returns:
        FastAPI: Yapılandırılmış FastAPI uygulaması
    """
    # FastAPI app oluştur
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan
    )

    # Middleware'leri ayarla
    setup_middlewares(app)
    init_monitoring(app)
    Instrumentator().instrument(app).expose(app)

    # CORS ayarları
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Test ortamı yapılandırması
    if os.getenv("TESTING") == "true":
        settings.POSTGRES_SERVER = "localhost"
        settings.POSTGRES_PORT = 5433
        settings.POSTGRES_DB = "legal_assistant_test"

    # Router'ları ekle
    app.include_router(v1_router, prefix=settings.API_V1_STR)
    app.include_router(
        health.router,
        prefix="/health",
        tags=["health"]
    )

    return app

# Ana uygulama instance'ı
app = create_app()

@app.get("/")
async def root():
    """Ana endpoint - API durumunu kontrol eder"""
    return {
        "message": "Legal AI API'ye Hoş Geldiniz",
        "version": settings.VERSION,
        "status": "active"
    }

# Development sunucusu
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
