"""Authentication controller."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import DatabaseSession, CurrentUserId
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, 
    RefreshTokenRequest, SocialLoginRequest
)
from app.schemas.user import UserPublic
from app.schemas.common import SuccessResponse

# TODO: Import services when implemented
# from app.services.auth_service import AuthService
# from app.services.social_auth_service import SocialAuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: DatabaseSession
) -> TokenResponse:
    """
    Register a new user.
    
    Args:
        request: User registration data.
        db: Database session.
        
    Returns:
        TokenResponse: JWT tokens for the new user.
        
    Raises:
        HTTPException: If registration fails.
    """
    # TODO: Implement with AuthService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Register endpoint not yet implemented"
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: DatabaseSession
) -> TokenResponse:
    """
    Login with email and password.
    
    Args:
        request: Login credentials.
        db: Database session.
        
    Returns:
        TokenResponse: JWT tokens for the user.
        
    Raises:
        HTTPException: If login fails.
    """
    # TODO: Implement with AuthService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login endpoint not yet implemented"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DatabaseSession
) -> TokenResponse:
    """
    Refresh access token.
    
    Args:
        request: Refresh token data.
        db: Database session.
        
    Returns:
        TokenResponse: New JWT tokens.
        
    Raises:
        HTTPException: If token refresh fails.
    """
    # TODO: Implement with AuthService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh endpoint not yet implemented"
    )


@router.post("/social", response_model=TokenResponse)
async def social_login(
    request: SocialLoginRequest,
    db: DatabaseSession
) -> TokenResponse:
    """
    Social login with OAuth provider.
    
    Args:
        request: Social login data.
        db: Database session.
        
    Returns:
        TokenResponse: JWT tokens for the user.
        
    Raises:
        HTTPException: If social login fails.
    """
    # TODO: Implement with SocialAuthService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Social login endpoint not yet implemented"
    )


@router.get("/me", response_model=UserPublic)
async def get_current_user(
    current_user_id: CurrentUserId,
    db: DatabaseSession
) -> UserPublic:
    """
    Get current user information.
    
    Args:
        current_user_id: Current user ID from JWT.
        db: Database session.
        
    Returns:
        UserPublic: Current user data.
        
    Raises:
        HTTPException: If user not found.
    """
    # TODO: Implement with UserRepository
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get current user endpoint not yet implemented"
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user_id: CurrentUserId,
    db: DatabaseSession
) -> SuccessResponse:
    """
    Logout user (for future token blacklisting).
    
    Args:
        current_user_id: Current user ID from JWT.
        db: Database session.
        
    Returns:
        SuccessResponse: Logout confirmation.
    """
    # TODO: Implement token blacklisting if needed
    return SuccessResponse(message="Successfully logged out")