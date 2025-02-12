from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.exceptions import DatabaseError, get_error_message
from contextlib import contextmanager
from typing import Generator
from app.core.logger import db_logger

# SQLite için FOREIGN KEY desteği
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Engine oluştur
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Bağlantı kontrolü
    pool_size=5,  # Bağlantı havuzu boyutu
    max_overflow=10,  # Maksimum ek bağlantı
    echo=settings.ENVIRONMENT == "development"  # Development'ta SQL logları
)

# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class
Base = declarative_base()

def get_db() -> Generator:
    """
    Veritabanı oturumu sağlar.
    
    Yields:
        Session: Veritabanı oturumu
    
    Raises:
        DatabaseError: Veritabanı bağlantı hatası
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db_logger.error("Database session error", error=str(e))
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR"))
    finally:
        db.close()

@contextmanager
def transaction():
    """
    Transaction context manager.
    Otomatik commit/rollback sağlar.
    
    Example:
        with transaction() as session:
            session.add(user)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db() -> None:
    """
    Veritabanını başlatır.
    Tabloları oluşturur.
    """
    try:
        Base.metadata.create_all(bind=engine)
        db_logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        db_logger.error("Failed to initialize database", error=str(e))
        raise DatabaseError(detail=get_error_message("DATABASE_ERROR"))

def check_db_connection() -> bool:
    """
    Veritabanı bağlantısını kontrol eder.
    
    Returns:
        bool: Bağlantı durumu
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_logger.info("Database connection successful")
        return True
    except SQLAlchemyError as e:
        db_logger.error("Database connection failed", error=str(e))
        return False
