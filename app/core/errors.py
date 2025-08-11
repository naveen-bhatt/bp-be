"""Global error handlers and custom exceptions."""

from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .logging import get_logger

logger = get_logger(__name__)


class BusinessLogicError(Exception):
    """Base exception for business logic errors."""
    
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(BusinessLogicError):
    """Exception raised when a resource is not found."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, "NOT_FOUND")


class DuplicateError(BusinessLogicError):
    """Exception raised when trying to create a duplicate resource."""
    
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message, "DUPLICATE")


class InsufficientStockError(BusinessLogicError):
    """Exception raised when product stock is insufficient."""
    
    def __init__(self, product_name: str, requested: int, available: int):
        message = f"Insufficient stock for {product_name}. Requested: {requested}, Available: {available}"
        super().__init__(message, "INSUFFICIENT_STOCK")


class PaymentError(BusinessLogicError):
    """Exception raised for payment processing errors."""
    
    def __init__(self, message: str):
        super().__init__(message, "PAYMENT_ERROR")


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
        },
    )


async def business_logic_exception_handler(
    request: Request, exc: BusinessLogicError
) -> JSONResponse:
    """Handle business logic exceptions."""
    logger.warning(f"Business logic error: {exc.code} - {exc.message}")
    
    status_code = 400
    if exc.code == "NOT_FOUND":
        status_code = 404
    elif exc.code == "DUPLICATE":
        status_code = 409
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.code,
            "message": exc.message,
        },
    )


async def database_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle database exceptions."""
    logger.error(f"Database error: {exc}")
    
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "error": "INTEGRITY_ERROR",
                "message": "Database integrity constraint violation",
            },
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "DATABASE_ERROR",
            "message": "An error occurred while processing your request",
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)