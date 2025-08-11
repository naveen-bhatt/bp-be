"""Authentication context middleware."""

from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import verify_token
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and attach user context from JWT tokens."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and extract user context from JWT token.
        
        Args:
            request: Incoming HTTP request.
            call_next: Next middleware or endpoint handler.
            
        Returns:
            Response: HTTP response.
        """
        # Initialize user context
        request.state.user_id = None
        request.state.is_authenticated = False
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.split(" ")[1]
                payload = verify_token(token, "access")
                
                # Extract user information from token
                user_id = payload.get("sub")
                if user_id:
                    request.state.user_id = user_id
                    request.state.is_authenticated = True
                    
                    logger.debug(f"Authenticated user: {user_id}")
                    
            except Exception as e:
                # Don't fail the request if token is invalid
                # Let the dependency injection handle authorization
                logger.debug(f"Invalid token in middleware: {e}")
        
        # Process request
        response = await call_next(request)
        return response


def get_current_user_from_state(request: Request) -> Optional[str]:
    """
    Get current user ID from request state.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        Optional[str]: User ID if authenticated, None otherwise.
    """
    return getattr(request.state, "user_id", None)


def is_authenticated(request: Request) -> bool:
    """
    Check if current request is authenticated.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        bool: True if authenticated, False otherwise.
    """
    return getattr(request.state, "is_authenticated", False)