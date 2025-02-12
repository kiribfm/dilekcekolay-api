"""
API package for Legal Assistant.
All API versions and their endpoints are organized here.
"""

from app.api.v1.api import api_router as v1_router

__all__ = ["v1_router"]

