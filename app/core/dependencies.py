"""Shared dependencies for FastAPI endpoints."""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .db import get_db
from .security import verify_token
from .logging import get_logger
import jwt

logger = get_logger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ):
        """
        Initialize pagination parameters.
        
        Args:
            page: Page number (1-based).
            per_page: Number of items per page.
            max_per_page: Maximum allowed items per page.
            
        Raises:
            HTTPException: If parameters are invalid.
        """
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be 1 or greater"
            )
        
        if per_page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Per page must be 1 or greater"
            )
        
        if per_page > max_per_page:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Per page cannot exceed {max_per_page}"
            )
        
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """
    Extract current user ID from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials.
        
    Returns:
        str: User ID from token.
        
    Raises:
        HTTPException: If token is invalid or user ID not found.
    """
    payload = verify_token(credentials.credentials, "access")
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_current_user_optional(
    request: Request
) -> Optional[str]:
    """
    Extract current user ID from JWT token if present.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        Optional[str]: User ID if token is valid, None otherwise.
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = verify_token(token, "access")
        return payload.get("sub")
    except Exception:
        return None


async def get_admin_user(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)]
) -> str:
    """
    Ensure current user is an admin.
    
    Args:
        current_user_id: Current user ID from token.
        db: Database session.
        
    Returns:
        str: User ID if user is admin.
        
    Raises:
        HTTPException: If user is not admin.
    """
    # Import here to avoid circular imports
    from app.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user_id)
    
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user_id


# Cart token dependency removed as we're using anonymous user tokens for all users


def get_anonymous_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract user ID from anonymous token.
    
    Args:
        credentials: HTTP Bearer token credentials.
        
    Returns:
        str: User ID from the anonymous token.
        
    Raises:
        HTTPException: If token is invalid or not anonymous.
    """
    try:
        # Decode token without verification to get payload
        token = credentials.credentials
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Check if it's an anonymous token
        if payload.get("user_type") != "anonymous":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is not an anonymous token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: missing user ID"
            )
        
        return user_id
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except Exception as e:
        logger.error(f"Error extracting anonymous user ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid anonymous token"
        )


# Type aliases for dependency injection
DatabaseSession = Annotated[Session, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
OptionalUserId = Annotated[Optional[str], Depends(get_current_user_optional)]
AdminUserId = Annotated[str, Depends(get_admin_user)]
AnonymousUserId = Annotated[str, Depends(get_anonymous_user_id)]
Pagination = Annotated[PaginationParams, Depends(PaginationParams)]