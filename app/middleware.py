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

    def __init__(self, app, secret_key: str, exempt_paths: list = None):
        super().__init__(app)
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.exempt_paths = exempt_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/google/callback",
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip CSRF check for safe methods and exempt paths
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Check if path is exempt
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # For API endpoints (JSON), check X-CSRF-Token header
        if request.url.path.startswith("/api"):
            csrf_token = request.headers.get("X-CSRF-Token")
            if not csrf_token:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token missing"}
                )

            try:
                # Verify token (with 1 hour expiry)
                self.serializer.loads(csrf_token, max_age=3600)
            except (BadSignature, SignatureExpired):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Invalid or expired CSRF token"}
                )

        response = await call_next(request)
        return response

    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        return self.serializer.dumps("csrf_token")


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
    csrf_middleware = CSRFProtectionMiddleware(app, secret_key=settings.csrf_secret_key)
    app.add_middleware(
        lambda app: csrf_middleware.__class__(
            app,
            secret_key=settings.csrf_secret_key
        )
    )

    return csrf_middleware
