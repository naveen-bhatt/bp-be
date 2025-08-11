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
    logger.info(f"Configuring CORS with origins: {settings.cors_origins_list}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
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