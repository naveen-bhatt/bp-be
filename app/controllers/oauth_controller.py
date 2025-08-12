"""OAuth controller for social login endpoints."""

from typing import Optional
from fastapi import HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from app.core.dependencies import DatabaseSession, AnonymousUserId
from app.core.oauth_storage import get_oauth_storage
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.oauth.base import OAuthState
from app.providers.oauth.google import GoogleOAuthProvider
from app.services.auth_service import AuthService
from app.schemas.auth import TokenResponse

logger = get_logger(__name__)


def google_start(
    request: Request,
    anonymous_user_id: Optional[AnonymousUserId] = None
) -> RedirectResponse:
    """
    Start Google OAuth flow.
    
    Args:
        request: FastAPI request object.
        anonymous_user_id: Optional anonymous user ID from token.
        
    Returns:
        RedirectResponse: Redirect to Google OAuth.
        
    Raises:
        HTTPException: If OAuth initialization fails.
    """
    try:
        logger.info("Starting Google OAuth flow")
        
        # Check if Google OAuth is configured
        if not settings.google_client_id or not settings.google_client_secret:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
            )
        
        # Build redirect URI
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/api/v1/auth/google/callback"
        
        # Generate OAuth state with PKCE
        oauth_state = OAuthState.generate(
            redirect_uri=redirect_uri,
            anonymous_user_id=anonymous_user_id
        )
        
        # Store state for callback verification
        oauth_storage = get_oauth_storage()
        oauth_storage.store_state(oauth_state)
        
        # Create Google provider
        google_provider = GoogleOAuthProvider(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        
        # Get authorization URL
        auth_url = google_provider.get_authorization_url(oauth_state)
        
        logger.info(f"Redirecting to Google OAuth: {auth_url[:100]}...")
        return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        logger.error(f"Google OAuth start failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Google OAuth: {str(e)}"
        )


async def google_callback(
    request: Request,
    db: DatabaseSession,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
) -> TokenResponse:
    """
    Handle Google OAuth callback.
    
    Args:
        request: FastAPI request object.
        db: Database session.
        code: Authorization code from Google.
        state: State parameter for CSRF protection.
        error: Error from Google OAuth.
        
    Returns:
        TokenResponse: JWT tokens for authenticated user.
        
    Raises:
        HTTPException: If OAuth callback processing fails.
    """
    try:
        logger.info("Processing Google OAuth callback")
        
        # Check for OAuth errors
        if error:
            logger.warning(f"Google OAuth error: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google OAuth error: {error}"
            )
        
        if not code or not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing code or state parameter"
            )
        
        # Retrieve and validate stored state
        oauth_storage = get_oauth_storage()
        oauth_state = oauth_storage.get_state(state)
        
        if not oauth_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter"
            )
        
        # Create Google provider
        google_provider = GoogleOAuthProvider(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        
        # Exchange code for tokens
        logger.info("Exchanging code for tokens")
        oauth_tokens = await google_provider.exchange_code_for_tokens(
            code=code,
            code_verifier=oauth_state.code_verifier,
            redirect_uri=oauth_state.redirect_uri
        )
        
        # Get user info - prefer ID token verification if available
        if oauth_tokens.id_token:
            # Verify ID token with nonce
            user_info = await google_provider.verify_id_token(
                oauth_tokens.id_token, 
                oauth_state.nonce
            )
        else:
            # Fallback to userinfo endpoint
            user_info = await google_provider.get_user_info(oauth_tokens.access_token)
        
        logger.info(f"Google OAuth successful for user: {user_info.email}")
        
        # Create auth service and handle user registration/login
        auth_service = AuthService(db)
        
        if oauth_state.anonymous_user_id:
            # Convert anonymous user to social user
            tokens = auth_service.social_register(
                user_id=oauth_state.anonymous_user_id,
                email=user_info.email,
                provider="google"
            )
        else:
            # TODO: Handle case where no anonymous user exists
            # For now, create a new anonymous user and convert it
            anonymous_user_data = auth_service.create_anonymous_user()
            tokens = auth_service.social_register(
                user_id=anonymous_user_data["user_id"],
                email=user_info.email,
                provider="google"
            )
        
        logger.info(f"Social login successful for user: {user_info.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=1800  # 30 minutes in seconds
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )
