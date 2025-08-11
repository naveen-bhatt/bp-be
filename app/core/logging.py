"""Structured logging configuration."""

import logging
import sys
from typing import Dict, Any
from contextlib import contextmanager
from contextvars import ContextVar

from .config import settings

# Context variables for request tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
request_path_var: ContextVar[str] = ContextVar("request_path", default="")


class StructuredFormatter(logging.Formatter):
    """Custom formatter that adds structured context to log records."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured context."""
        # Add context variables to the record
        record.request_id = request_id_var.get("")
        record.request_path = request_path_var.get("")
        
        # Create structured log entry
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request context if available
        if record.request_id:
            log_data["request_id"] = record.request_id
        if record.request_path:
            log_data["request_path"] = record.request_path
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return str(log_data)


def configure_logging() -> None:
    """Configure application logging."""
    # Set log level based on environment
    log_level = logging.DEBUG if settings.is_development else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure structured formatter for production
    if settings.is_production:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


@contextmanager
def log_context(request_id: str = "", request_path: str = ""):
    """Context manager for setting log context variables."""
    request_id_token = request_id_var.set(request_id)
    request_path_token = request_path_var.set(request_path)
    
    try:
        yield
    finally:
        request_id_var.reset(request_id_token)
        request_path_var.reset(request_path_token)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)