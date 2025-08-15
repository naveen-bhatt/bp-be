"""OAuth controller for social login endpoints."""

from typing import Optional
from fastapi import HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode, quote

from app.core.dependencies import DatabaseSession, AnonymousUserId
from app.core.oauth_storage import get_oauth_storage
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.oauth.base import OAuthState
from app.providers.oauth.google import GoogleOAuthProvider
from app.services.auth_service import AuthService

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
        
        logger.info(f"OAuth redirect URI: {redirect_uri}")
        logger.info(f"Request base URL: {request.base_url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
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
) -> RedirectResponse:
    """
    Handle Google OAuth callback.
    
    Args:
        request: FastAPI request object.
        db: Database session.
        code: Authorization code from Google.
        state: State parameter for CSRF protection.
        error: Error from Google OAuth.
        
    Returns:
        RedirectResponse: Redirect to frontend with authentication tokens.
        
    Raises:
        HTTPException: If OAuth callback processing fails.
    """
    try:
        logger.info("Processing Google OAuth callback")
        
        # Check for OAuth errors
        if error:
            logger.warning(f"Google OAuth error: {error}")
            # Redirect to frontend with error
            frontend_url = f"{settings.frontend_url}/auth/google/callback"
            error_params = {
                "success": "false",
                "error": error
            }
            error_redirect_url = f"{frontend_url}?{urlencode(error_params)}"
            return RedirectResponse(url=error_redirect_url, status_code=status.HTTP_302_FOUND)
        
        if not code or not state:
            logger.warning("Missing code or state parameter")
            # Redirect to frontend with error
            frontend_url = f"{settings.frontend_url}/auth/google/callback"
            error_params = {
                "success": "false",
                "error": "Missing OAuth parameters"
            }
            error_redirect_url = f"{frontend_url}?{urlencode(error_params)}"
            return RedirectResponse(url=error_redirect_url, status_code=status.HTTP_302_FOUND)
        
        # Retrieve and validate stored state
        oauth_storage = get_oauth_storage()
        oauth_state = oauth_storage.get_state(state)
        
        if not oauth_state:
            logger.warning("Invalid or expired state parameter")
            # Redirect to frontend with error
            frontend_url = f"{settings.frontend_url}/auth/google/callback"
            error_params = {
                "success": "false",
                "error": "Invalid or expired OAuth state"
            }
            error_redirect_url = f"{frontend_url}?{urlencode(error_params)}"
            return RedirectResponse(url=error_redirect_url, status_code=status.HTTP_302_FOUND)
        
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
        
        logger.info(f"Received tokens: access_token={'*' * 10 if oauth_tokens.access_token else 'None'}, id_token={'*' * 10 if oauth_tokens.id_token else 'None'}")
        
        # For now, always use the userinfo endpoint to avoid ID token verification issues
        # TODO: Fix ID token verification and re-enable it
        logger.info("Using userinfo endpoint for user data")
        
        if not oauth_tokens.access_token:
            logger.error("No access token received from Google")
            # Redirect to frontend with error
            frontend_url = f"{settings.frontend_url}/auth/google/callback"
            error_params = {
                "success": "false",
                "error": "No access token received from Google"
            }
            error_redirect_url = f"{frontend_url}?{urlencode(error_params)}"
            return RedirectResponse(url=error_redirect_url, status_code=status.HTTP_302_FOUND)
        
        user_info = await google_provider.get_user_info(oauth_tokens.access_token)
        
        logger.info(f"Google OAuth successful for user: {user_info.email}")
        
        # Create auth service and handle user registration/login
        auth_service = AuthService(db)
        
        # Check if user exists by email
        existing_user = auth_service.user_repo.get_by_email(user_info.email)
        
        if existing_user:
            logger.info(f"User exists with email: {user_info.email}")
            
            # Check if user has a social account for Google
            from app.repositories.social_repository import SocialRepository
            from app.models.social_account import SocialProvider
            
            social_repo = SocialRepository(db)
            social_account = social_repo.get_by_user_and_provider(
                user_id=str(existing_user.id),
                provider=SocialProvider.GOOGLE
            )
            
            if social_account:
                # User exists and has Google social account - LOGIN
                logger.info(f"User has Google social account, logging in: {user_info.email}")
                tokens = auth_service.social_login(
                    email=user_info.email,
                    provider="google",
                    provider_account_id=user_info.provider_account_id
                )
                logger.info(f"Social login successful for existing user: {user_info.email}")
            else:
                # User exists but no Google social account - ADD SOCIAL ACCOUNT
                logger.info(f"User exists but no Google social account, adding it: {user_info.email}")
                
                # Create social account for existing user
                social_repo.create(
                    user_id=str(existing_user.id),
                    provider=SocialProvider.GOOGLE,
                    provider_account_id=user_info.provider_account_id
                )
                
                # Login the user
                tokens = auth_service.social_login(
                    email=user_info.email,
                    provider="google",
                    provider_account_id=user_info.provider_account_id
                )
                logger.info(f"Added Google social account and logged in: {user_info.email}")
        else:
            # User doesn't exist - REGISTRATION
            logger.info(f"User not found, attempting registration: {user_info.email}")
            
            if oauth_state.anonymous_user_id:
                # Convert anonymous user to social user
                tokens = auth_service.social_register(
                    user_id=oauth_state.anonymous_user_id,
                    email=user_info.email,
                    provider="google",
                    provider_account_id=user_info.provider_account_id
                )
                logger.info(f"Converted anonymous user to social user: {user_info.email}")
            else:
                # Create a new anonymous user and convert it
                anonymous_user_data = auth_service.create_anonymous_user()
                tokens = auth_service.social_register(
                    user_id=anonymous_user_data["user_id"],
                    email=user_info.email,
                    provider="google",
                    provider_account_id=user_info.provider_account_id
                )
                logger.info(f"Created new social user: {user_info.email}")
        
        # Build frontend redirect URL with tokens
        frontend_url = f"{settings.frontend_url}/auth/google/callback"
        
        # Create query parameters for the frontend
        query_params = {
            "success": "true",
            "access_token": quote(tokens["access_token"], safe=''),
            "refresh_token": quote(tokens["refresh_token"], safe=''),
            "token_type": tokens["token_type"],
            "expires_in": str(tokens.get("expires_in", 1800)),
            "user_email": quote(user_info.email, safe='')
        }
        
        # Build the full redirect URL
        redirect_url = f"{frontend_url}?{urlencode(query_params)}"
        
        logger.info(f"Redirecting to frontend: {frontend_url}")
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )
