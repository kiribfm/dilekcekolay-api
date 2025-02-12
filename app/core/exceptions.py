from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class LegalAssistantException(HTTPException):
    """Base exception for Legal Assistant API"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class AuthenticationError(LegalAssistantException):
    """Authentication related errors"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(LegalAssistantException):
    """Authorization related errors"""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class ValidationError(LegalAssistantException):
    """Data validation errors"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class DatabaseError(LegalAssistantException):
    """Database related errors"""
    def __init__(self, detail: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class AIServiceError(LegalAssistantException):
    """AI service related errors"""
    def __init__(self, detail: str = "AI service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )

class PremiumRequiredError(LegalAssistantException):
    """Premium feature access errors"""
    def __init__(self, detail: str = "Premium subscription required"):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail
        )

class RateLimitError(LegalAssistantException):
    """Rate limiting errors"""
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"}
        )

# Error messages
ERROR_MESSAGES = {
    # Auth errors
    "INVALID_CREDENTIALS": "Invalid email or password",
    "TOKEN_EXPIRED": "Token has expired",
    "TOKEN_INVALID": "Invalid token",
    "USER_NOT_FOUND": "User not found",
    "EMAIL_EXISTS": "Email already registered",
    "INACTIVE_USER": "User is inactive",
    
    # Premium errors
    "PREMIUM_REQUIRED": "This feature requires premium subscription",
    "PREMIUM_EXPIRED": "Premium subscription has expired",
    
    # Validation errors
    "INVALID_EMAIL": "Invalid email format",
    "WEAK_PASSWORD": "Password is too weak",
    "INVALID_DATE": "Invalid date format",
    
    # Service errors
    "AI_SERVICE_ERROR": "AI service is temporarily unavailable",
    "PDF_GENERATION_ERROR": "Failed to generate PDF",
    "DATABASE_ERROR": "Database operation failed",
    
    # Rate limiting
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please try again later",
}

def get_error_message(error_code: str) -> str:
    """
    Get error message by error code.
    
    Args:
        error_code: Error message code
    
    Returns:
        str: Error message
    """
    return ERROR_MESSAGES.get(error_code, "An unexpected error occurred") 