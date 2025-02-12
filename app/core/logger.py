import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
from app.core.config import settings

# Log dizini oluştur
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log formatı
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class CustomLogger:
    """Özelleştirilmiş logger sınıfı"""

    def __init__(self, name: str, log_level: Optional[str] = None):
        """
        Logger'ı başlatır.

        Args:
            name: Logger adı
            log_level: Log seviyesi
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level or settings.LOG_LEVEL)

        # Formatı ayarla
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        # Dosya handler'ı
        log_file = os.path.join(LOG_DIR, f"{name}_{datetime.now().strftime('%Y%m')}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler'ı (development ortamında)
        if settings.ENVIRONMENT == "development":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def info(self, message: str, **kwargs) -> None:
        """Info seviyesinde log"""
        self.logger.info(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs) -> None:
        """Error seviyesinde log"""
        self.logger.error(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        """Warning seviyesinde log"""
        self.logger.warning(self._format_message(message, **kwargs))

    def debug(self, message: str, **kwargs) -> None:
        """Debug seviyesinde log"""
        self.logger.debug(self._format_message(message, **kwargs))

    def _format_message(self, message: str, **kwargs) -> str:
        """
        Log mesajını formatlar.

        Args:
            message: Ana mesaj
            **kwargs: Ek bilgiler

        Returns:
            str: Formatlanmış mesaj
        """
        if kwargs:
            extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} - {extra_info}"
        return message

# Uygulama loggerları
api_logger = CustomLogger("api")
auth_logger = CustomLogger("auth")
db_logger = CustomLogger("db")
ai_logger = CustomLogger("ai")

def setup_logging() -> None:
    """
    Genel logging ayarlarını yapar.
    Uygulama başlangıcında çağrılmalıdır.
    """
    # Root logger'ı yapılandır
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT
    )

    # 3rd party kütüphanelerin log seviyelerini ayarla
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    # Başlangıç mesajı
    api_logger.info(
        "Application started",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION
    ) 