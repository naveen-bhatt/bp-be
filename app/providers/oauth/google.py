"""Google OAuth provider implementation."""

import json
from typing import Optional, Dict, Any
import httpx
from jose import jwt, JWTError

from .base import OAuthProvider, OAuthTokens, OAuthUserInfo
from app.core.logging import get_logger

logger = get_logger(__name__)


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider implementation."""
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize Google OAuth provider."""
        super().__init__(client_id, client_secret)
        self._jwks_cache: Optional[Dict[str, Any]] = None
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "google"
    
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Get Google authorization URL.
        
        Args:
            redirect_uri: Redirect URI for callback.
            state: Optional state parameter for CSRF protection.
            
        Returns:
            str: Authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, redirect_uri: Optional[str] = None) -> OAuthTokens:
        """
        Exchange authorization code for Google tokens.
        
        Args:
            code: Authorization code from Google callback.
            redirect_uri: Redirect URI used in authorization.
            
        Returns:
            OAuthTokens: Access and refresh tokens.
            
        Raises:
            ValueError: If code exchange fails.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri or "urn:ietf:wg:oauth:2.0:oob"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.TOKEN_URL, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                
                return OAuthTokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in"),
                    token_type=token_data.get("token_type", "Bearer")
                )
                
        except Exception as e:
            logger.error(f"Google token exchange failed: {e}")
            raise ValueError(f"Failed to exchange code for tokens: {e}")
    
    async def verify_id_token(self, id_token: str) -> OAuthUserInfo:
        """
        Verify Google ID token and extract user information.
        
        Args:
            id_token: JWT ID token from Google.
            
        Returns:
            OAuthUserInfo: User information from token.
            
        Raises:
            ValueError: If token verification fails.
        """
        try:
            # Get Google's public keys for verification
            jwks = await self._get_jwks()
            
            # Decode and verify the token
            payload = jwt.decode(
                id_token,
                jwks,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://accounts.google.com"
            )
            
            return OAuthUserInfo(
                email=payload["email"],
                provider_account_id=payload["sub"],
                name=payload.get("name"),
                avatar_url=payload.get("picture"),
                verified=payload.get("email_verified", False)
            )
            
        except JWTError as e:
            logger.error(f"Google ID token verification failed: {e}")
            raise ValueError(f"Invalid ID token: {e}")
        except Exception as e:
            logger.error(f"Google ID token processing failed: {e}")
            raise ValueError(f"Failed to process ID token: {e}")
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Get user information using Google access token.
        
        Args:
            access_token: Google access token.
            
        Returns:
            OAuthUserInfo: User information.
            
        Raises:
            ValueError: If user info retrieval fails.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.USERINFO_URL, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                
                return OAuthUserInfo(
                    email=user_data["email"],
                    provider_account_id=user_data["id"],
                    name=user_data.get("name"),
                    avatar_url=user_data.get("picture"),
                    verified=user_data.get("verified_email", False)
                )
                
        except Exception as e:
            logger.error(f"Google user info retrieval failed: {e}")
            raise ValueError(f"Failed to get user info: {e}")
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokens:
        """
        Refresh Google access token.
        
        Args:
            refresh_token: Google refresh token.
            
        Returns:
            OAuthTokens: New access tokens.
            
        Raises:
            ValueError: If token refresh fails.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.TOKEN_URL, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                
                return OAuthTokens(
                    access_token=token_data["access_token"],
                    expires_in=token_data.get("expires_in"),
                    token_type=token_data.get("token_type", "Bearer")
                )
                
        except Exception as e:
            logger.error(f"Google token refresh failed: {e}")
            raise ValueError(f"Failed to refresh token: {e}")
    
    async def _get_jwks(self) -> Dict[str, Any]:
        """Get Google's JWKS for token verification."""
        if not self._jwks_cache:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(self.JWKS_URL)
                    response.raise_for_status()
                    self._jwks_cache = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch Google JWKS: {e}")
                raise ValueError(f"Failed to fetch verification keys: {e}")
        
        return self._jwks_cache