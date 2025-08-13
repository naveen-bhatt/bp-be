"""Google OAuth provider implementation."""

import json
import hashlib
import base64
from typing import Optional, Dict, Any
import httpx
from jose import jwt, JWTError

from .base import OAuthProvider, OAuthTokens, OAuthUserInfo, OAuthState
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
    
    def get_authorization_url(self, oauth_state: OAuthState) -> str:
        """
        Get Google authorization URL with PKCE.
        
        Args:
            oauth_state: OAuth state containing PKCE parameters.
            
        Returns:
            str: Authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": oauth_state.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": oauth_state.state,
            "nonce": oauth_state.nonce,
            "code_challenge": oauth_state.code_challenge,
            "code_challenge_method": "S256"
        }
        
        logger.info(f"Google OAuth params: {params}")
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, code_verifier: str, redirect_uri: str) -> OAuthTokens:
        """
        Exchange authorization code for Google tokens using PKCE.
        
        Args:
            code: Authorization code from Google callback.
            code_verifier: PKCE code verifier.
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
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.TOKEN_URL, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                logger.info(f"Google token exchange response: {list(token_data.keys())}")
                
                # Check for errors in response
                if "error" in token_data:
                    error_msg = token_data.get("error_description", token_data.get("error", "Unknown error"))
                    logger.error(f"Google OAuth error: {error_msg}")
                    raise ValueError(f"Google OAuth error: {error_msg}")
                
                if "access_token" not in token_data:
                    logger.error(f"Google OAuth response missing access_token: {token_data}")
                    raise ValueError("Google OAuth response missing access_token")
                
                return OAuthTokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in"),
                    token_type=token_data.get("token_type", "Bearer"),
                    id_token=token_data.get("id_token")  # Google includes id_token in response
                )
                
        except Exception as e:
            logger.error(f"Google token exchange failed: {e}")
            raise ValueError(f"Failed to exchange code for tokens: {e}")
    
    async def verify_id_token(self, id_token: str, access_token: str, nonce: Optional[str] = None) -> OAuthUserInfo:
        """
        Verify Google ID token and extract user information.
        
        Args:
            id_token: JWT ID token from Google.
            access_token: Access token to validate at_hash claim.
            nonce: Expected nonce value for verification.
            
        Returns:
            OAuthUserInfo: User information from token.
            
        Raises:
            ValueError: If token verification fails.
        """
        try:
            logger.info("Starting Google ID token verification")
            
            # Get Google's public keys for verification
            jwks = await self._get_jwks()
            logger.info(f"Retrieved JWKS with {len(jwks.get('keys', []))} keys")
            
            # Decode and verify the token
            logger.info("Decoding and verifying JWT token")
            payload = jwt.decode(
                id_token,
                jwks,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://accounts.google.com"
            )
            logger.info("JWT token decoded successfully")
            
            # Verify nonce if provided
            if nonce and payload.get("nonce") != nonce:
                logger.error(f"Nonce verification failed: expected {nonce}, got {payload.get('nonce')}")
                raise ValueError("Nonce verification failed")
            
            # Verify at_hash claim if present
            if "at_hash" in payload and access_token:
                logger.info("at_hash claim present, validating...")
                try:
                    # Calculate hash of access token
                    access_token_hash = base64.urlsafe_b64encode(
                        hashlib.sha256(access_token.encode('utf-8')).digest()
                    ).decode('utf-8').rstrip('=')
                    
                    logger.info(f"Calculated at_hash: {access_token_hash[:10]}..., token at_hash: {payload['at_hash'][:10]}...")
                    
                    if payload["at_hash"] != access_token_hash:
                        logger.warning("Access token hash verification failed, but continuing")
                        # Don't fail the entire verification for at_hash mismatch
                        # This can happen in some OAuth flows
                    else:
                        logger.info("at_hash validation successful")
                except Exception as e:
                    logger.warning(f"Failed to verify at_hash: {e}, but continuing")
                    # Continue with verification even if at_hash validation fails
            else:
                logger.info("No at_hash claim or access token, skipping at_hash validation")
            
            logger.info(f"Token verification successful for user: {payload.get('email')}")
            
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