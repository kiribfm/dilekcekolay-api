from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge, generate_latest, Histogram
from fastapi.responses import PlainTextResponse
from app.core.config import settings
from sqlalchemy import text
from app.db.database import SessionLocal
from fastapi import FastAPI
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Metrik tanımlamaları
PETITION_COUNTER = Counter(
    "petition_total",
    "Total number of petitions generated",
    ["type", "model"]  # labels
)

USER_GAUGE = Gauge(
    "users_total",
    "Total number of users",
    ["type"]  # premium/normal label
)

REQUEST_COUNT = Counter(
    'http_request_total',
    'Total HTTP Request Count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Duration',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Total number of active users'
)

DB_CONNECTION_ERRORS = Counter(
    'db_connection_errors_total',
    'Database Connection Errors'
)

AI_SERVICE_ERRORS = Counter(
    'ai_service_errors_total',
    'AI Service Errors'
)

PREMIUM_USERS = Gauge(
    'premium_users_total',
    'Total number of premium users'
)

def init_monitoring(app: FastAPI) -> None:
    """
    Monitoring servislerini başlatır.
    
    Args:
        app: FastAPI uygulaması
    """
    # Sentry yapılandırması
    if settings.ENVIRONMENT == "production" and settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint"
                )
            ],
            traces_sample_rate=1.0,
            send_default_pii=False
        )

    Instrumentator().instrument(app).expose(app, include_in_schema=False)

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        db = SessionLocal()
        try:
            # Toplam dilekçe sayısı
            petition_count = db.execute(
                text("SELECT petition_type, COUNT(*) FROM petitions GROUP BY petition_type")
            ).fetchall()
            
            for p_type, count in petition_count:
                PETITION_COUNTER.labels(type=p_type, model="gpt-4").inc(count)
            
            # Kullanıcı sayıları
            user_stats = db.execute(
                text("""
                    SELECT 
                        is_premium,
                        COUNT(*) as count
                    FROM users
                    GROUP BY is_premium
                """)
            ).fetchall()
            
            for is_premium, count in user_stats:
                user_type = "premium" if is_premium else "normal"
                USER_GAUGE.labels(type=user_type).set(count)
                
            # Prometheus formatında metrikleri döndür
            return PlainTextResponse(generate_latest().decode())
            
        finally:
            db.close()

def record_metrics(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """
    Request metriklerini kaydeder.
    
    Args:
        method: HTTP metodu
        endpoint: Endpoint yolu
        status_code: HTTP durum kodu
        duration: İstek süresi
    """
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)

def update_user_metrics(active_count: int, premium_count: int) -> None:
    """
    Kullanıcı metriklerini günceller.
    
    Args:
        active_count: Aktif kullanıcı sayısı
        premium_count: Premium kullanıcı sayısı
    """
    ACTIVE_USERS.set(active_count)
    PREMIUM_USERS.set(premium_count)

def record_error(error_type: str) -> None:
    """
    Hata metriklerini kaydeder.
    
    Args:
        error_type: Hata tipi (db, ai_service)
    """
    if error_type == "db":
        DB_CONNECTION_ERRORS.inc()
    elif error_type == "ai_service":
        AI_SERVICE_ERRORS.inc() 