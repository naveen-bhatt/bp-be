"""Authentication controller."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import DatabaseSession, CurrentUserId, AnonymousUserId
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, 
    RefreshTokenRequest, SocialLoginRequest, AnonymousTokenResponse
)
from app.schemas.user import UserPublic
from app.schemas.common import SuccessResponse

from app.services.auth_service import AuthService
# TODO: Import social auth service when implemented
# from app.services.social_auth_service import SocialAuthService


def create_anonymous_user(
    db: DatabaseSession
) -> AnonymousTokenResponse:
    """
    Create an anonymous user for guest sessions.
    
    Args:
        db: Database session.
        
    Returns:
        AnonymousTokenResponse: Anonymous user token data.
        
    Raises:
        HTTPException: If anonymous user creation fails.
    """
    try:
        auth_service = AuthService(db)
        token_data = auth_service.create_anonymous_user()
        
        return AnonymousTokenResponse(**token_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create anonymous user: {str(e)}"
        )


def register(
    request: RegisterRequest,
    anonymous_user_id: AnonymousUserId,
    db: DatabaseSession
) -> TokenResponse:
    """
    Register a user by converting an anonymous user.
    
    Args:
        request: User registration data with email and password.
        anonymous_user_id: User ID extracted from anonymous token in Authorization header.
        db: Database session.
        
    Returns:
        TokenResponse: JWT tokens for the registered user.
        
    Raises:
        HTTPException: If registration fails.
    """
    try:
        auth_service = AuthService(db)
        tokens = auth_service.register(
            user_id=anonymous_user_id,
            email=request.email,
            password=request.password
        )
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=1800  # 30 minutes in seconds
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


def login(
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


def refresh_token(
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
    try:
        # Create auth service
        auth_service = AuthService(db)
        
        # Refresh tokens
        tokens = auth_service.refresh_access_token(request.refresh_token)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=1800  # 30 minutes in seconds
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from security module
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        # logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


def social_login(
    request: SocialLoginRequest,
    anonymous_user_id: AnonymousUserId,
    db: DatabaseSession
) -> TokenResponse:
    """
    Social login by converting an anonymous user.
    
    Args:
        request: Social login data with provider info.
        anonymous_user_id: User ID extracted from anonymous token in Authorization header.
        db: Database session.
        
    Returns:
        TokenResponse: JWT tokens for the user.
        
    Raises:
        HTTPException: If social login fails.
    """
    try:
        # For now, we'll use a mock email from the provider
        # In a real implementation, you would verify the id_token/code with the provider
        mock_email = f"user_{anonymous_user_id[:8]}@{request.provider}.com"
        
        auth_service = AuthService(db)
        tokens = auth_service.social_register(
            user_id=anonymous_user_id,
            email=mock_email,
            provider=request.provider
        )
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=1800  # 30 minutes in seconds
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Social login failed: {str(e)}"
        )


def get_current_user(
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


def logout(
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