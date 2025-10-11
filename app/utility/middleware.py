from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from typing import Callable
import time
import logging

from app.config import settings


logger = logging.getLogger(__name__)


# ============================================================================
# Rate Limiting
# ============================================================================

limiter = Limiter(key_func=get_remote_address)


# ============================================================================
# CSRF Protection Middleware
# ============================================================================

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware for state-changing operations.
    Protects POST, PUT, DELETE, PATCH requests.
    """

    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.csrf_cookie_name = "csrf_token"
        self.csrf_header_name = "X-CSRF-Token"
        self.csrf_token_age = 3600  # 1 hour

    async def dispatch(self, request: Request, call_next: Callable):
        # Apply CSRF protection only on unsafe methods
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            csrf_cookie = request.cookies.get(self.csrf_cookie_name)
            csrf_header = request.headers.get(self.csrf_header_name)

            if not csrf_cookie or not csrf_header:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token missing"}
                )

            try:
                token_data = self.serializer.loads(csrf_header, max_age=self.csrf_token_age)
                if token_data != csrf_cookie:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Invalid CSRF token"}
                    )
            except (BadSignature, SignatureExpired):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid or expired CSRF token"}
                )

        response = await call_next(request)
        return response


# ============================================================================
# Security Headers Middleware
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


# ============================================================================
# Request Logging Middleware
# ============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.2f}s"
        )

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        return response


# ============================================================================
# CORS Configuration
# ============================================================================

def setup_cors(app):
    """Setup CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-CSRF-Token"],
    )


# ============================================================================
# Setup All Middleware
# ============================================================================

def setup_middleware(app):
    """Setup all middleware for the application"""

    # CORS
    setup_cors(app)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request Logging
    app.add_middleware(RequestLoggingMiddleware)

    # Rate Limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CSRF Protection (add last so it runs first in the chain)
    app.add_middleware(CSRFProtectionMiddleware, secret_key=settings.csrf_secret_key)

