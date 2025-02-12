from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import time
from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter(
    'http_request_count',
    'HTTP Request Count',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Request metrikleri için middleware.
    - Request sayısı
    - Response süreleri
    - Status code dağılımı
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        # Metrikleri kaydet
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Güvenlik başlıkları için middleware.
    - XSS koruması
    - Content güvenliği
    - Frame koruması
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Güvenlik başlıkları
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self';"
            )
        
        return response

def setup_middlewares(app: FastAPI) -> None:
    """
    Uygulama middleware'lerini yapılandırır.
    
    Args:
        app: FastAPI uygulaması
    """
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Güvenlik
    if settings.SECURITY_HEADERS:
        app.add_middleware(SecurityHeadersMiddleware)
        
        if settings.ENVIRONMENT == "production":
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["api.yourdomain.com"]  # Production domain'i
            )
    
    # Metrikler
    app.add_middleware(MetricsMiddleware) 