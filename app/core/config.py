from pydantic_settings import BaseSettings
from typing import Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    """
    Uygulama ayarları.
    Çevre değişkenlerinden yüklenir.
    """
    # Temel ayarlar
    PROJECT_NAME: str = "Dilekçematik API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Güvenlik
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: list = ["api.dilekce.com"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Veritabanı
    SQLALCHEMY_DATABASE_URI: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # OpenAI
    OPENAI_API_KEY: str
    AI_MODEL_BASIC: str = "gpt-3.5-turbo"
    AI_MODEL_PREMIUM: str = "gpt-4"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "https://dilekce.com",
        "https://www.dilekce.com"
    ]
    
    # Dosya sistemi
    UPLOAD_DIR: str = "/var/www/dilekce/uploads"
    TEMP_DIR: str = "/var/www/dilekce/temp"
    PDF_DIR: str = "/var/www/dilekce/pdfs"
    LOG_DIR: str = "/var/log/dilekce"
    
    # Test ayarları
    TESTING: bool = False
    TEST_DB_URL: Optional[str] = None

    class Config:
        """Pydantic config"""
        env_file = ".env.prod"
        case_sensitive = True

    def get_db_url(self) -> str:
        """Ortama göre veritabanı URL'ini döndürür"""
        if self.TESTING and self.TEST_DB_URL:
            return self.TEST_DB_URL
        return self.SQLALCHEMY_DATABASE_URI

    def ensure_directories(self) -> None:
        """Gerekli dizinleri oluşturur"""
        directories = [
            self.UPLOAD_DIR,
            self.TEMP_DIR,
            self.PDF_DIR,
            self.LOG_DIR
        ]
        for directory in directories:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, mode=0o755)
                except Exception as e:
                    raise Exception(f"Directory creation failed: {str(e)}")

    def get_cors_origins(self) -> list:
        """CORS origin listesini döndürür"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

@lru_cache()
def get_settings() -> Settings:
    """Settings singleton instance döndürür"""
    settings = Settings()
    settings.ensure_directories()
    return settings

# Global settings instance
settings = get_settings() 