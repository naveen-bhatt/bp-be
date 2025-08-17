"""CORS middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def add_cors_middleware(app: FastAPI) -> None:
    """
    Add CORS middleware to FastAPI application.
    
    Args:
        app: FastAPI application instance.
    """
    # Ensure we have CORS origins
    cors_origins = settings.cors_origins_list
    if not cors_origins:
        # Fallback to default origins if none are configured
        cors_origins = [
            "http://localhost:3000",
            "https://bluepansy.in", 
            "https://beta.bluepansy.in", 
            "https://qa.bluepansy.in", 
            "https://dev.bluepansy.in"
        ]
        logger.warning(f"No CORS origins configured, using fallback: {cors_origins}")
    
    logger.info(f"Configuring CORS with origins: {cors_origins}")
    logger.info("CORS middleware will handle OPTIONS preflight requests automatically")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-Cart-Token",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Total-Count",
            "X-Page-Count",
        ],
    )