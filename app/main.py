"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.db import check_database_connection
from app.core.errors import register_exception_handlers
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.auth_context import AuthContextMiddleware
from app.middleware.cors import add_cors_middleware
from app.controllers.router import include_routes
from app.schemas.common import HealthResponse

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v0.1.0")
    logger.info(f"Environment: {settings.environment}")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Failed to connect to database")
        raise RuntimeError("Database connection failed")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Production-ready FastAPI backend with clean architecture",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan
)

# Add middleware (order matters!)
# CORS middleware must be added FIRST to handle OPTIONS preflight requests
add_cors_middleware(app)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AuthContextMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Include API routes
include_routes(app)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(request: Request) -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Application health status.
    """
    database_status = "healthy" if check_database_connection() else "unhealthy"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database=database_status,
        version="0.1.0"
    )


@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint.
    
    Returns:
        dict: Welcome message.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "0.1.0",
        "environment": settings.environment,
        "docs_url": "/docs" if settings.is_development else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="info"
    )