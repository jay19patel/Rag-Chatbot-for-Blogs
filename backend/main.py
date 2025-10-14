from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import logging

from app.database import create_db_and_tables
from app.routes.api import router as api_router
from app.utility.middleware import setup_middleware, limiter
from app.config import settings
# Import models to ensure they are registered with SQLModel
from app.models_schema import User, UserSession


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting application...")
    logger.info(f"Application: {settings.app_name}")

    # Create database tables
    logger.info("Creating database tables...")
    create_db_and_tables()
    logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Production-ready FastAPI authentication system with Google OAuth, role-based access control, and security features",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(api_router)


# Health check endpoint with rate limiting
@app.get("/health")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
