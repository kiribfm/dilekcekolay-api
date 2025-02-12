from fastapi import APIRouter
from app.api.v1.endpoints import auth, petitions
from typing import List

# API router tanımı
api_router = APIRouter()

# Router konfigürasyonları
ROUTER_CONFIGS: List[dict] = [
    {
        "router": auth.router,
        "prefix": "/auth",
        "tags": ["auth"],
        "responses": {401: {"description": "Unauthorized"}},
    },
    {
        "router": petitions.router,
        "prefix": "/petitions",
        "tags": ["petitions"],
        "responses": {
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden - Premium required"}
        },
    }
]

# Router'ları otomatik olarak ekle
for config in ROUTER_CONFIGS:
    api_router.include_router(**config) 