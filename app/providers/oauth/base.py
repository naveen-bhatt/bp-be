"""Base OAuth provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import secrets
import hashlib
import base64


@dataclass
class OAuthTokens:
    """OAuth token response."""
    
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    id_token: Optional[str] = None


@dataclass
class OAuthUserInfo:
    """OAuth user information."""
    
    email: str
    provider_account_id: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    verified: bool = False


@dataclass
class OAuthState:
    """OAuth state for PKCE flow."""
    
    state: str
    nonce: str
    code_verifier: str
    code_challenge: str
    redirect_uri: str
    anonymous_user_id: Optional[str] = None
    
    @classmethod
    def generate(cls, redirect_uri: str, anonymous_user_id: Optional[str] = None) -> 'OAuthState':
        """Generate new OAuth state with PKCE parameters."""
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(32)
        
        # Generate code_challenge from code_verifier using SHA256
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return cls(
            state=state,
            nonce=nonce,
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
            anonymous_user_id=anonymous_user_id
        )


class OAuthProvider(ABC):
    """Abstract base class for OAuth providers."""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize OAuth provider.
        
        Args:
            client_id: OAuth client ID.
            client_secret: OAuth client secret.
        """
        self.client_id = client_id
        self.client_secret = client_secret
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass
    
    @abstractmethod
    async def exchange_code_for_tokens(self, code: str, code_verifier: str, redirect_uri: str) -> OAuthTokens:
        """
        Exchange authorization code for access tokens using PKCE.
        
        Args:
            code: Authorization code from OAuth callback.
            code_verifier: PKCE code verifier.
            redirect_uri: Redirect URI used in authorization.
            
        Returns:
            OAuthTokens: Access and refresh tokens.
            
        Raises:
            ValueError: If code exchange fails.
        """
        pass
    
    @abstractmethod
    async def verify_id_token(self, id_token: str, access_token: str, nonce: Optional[str] = None) -> OAuthUserInfo:
        """
        Verify ID token and extract user information.
        
        Args:
            id_token: JWT ID token from OAuth provider.
            access_token: Access token to validate at_hash claim.
            nonce: Expected nonce value for verification.
            
        Returns:
            OAuthUserInfo: User information from token.
            
        Raises:
            ValueError: If token verification fails.
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Get user information using access token.
        
        Args:
            access_token: OAuth access token.
            
        Returns:
            OAuthUserInfo: User information.
            
        Raises:
            ValueError: If user info retrieval fails.
        """
        pass
    
    @abstractmethod
    def get_authorization_url(self, oauth_state: OAuthState) -> str:
        """
        Get authorization URL for OAuth flow with PKCE.
        
        Args:
            oauth_state: OAuth state containing PKCE parameters.
            
        Returns:
            str: Authorization URL.
        """
        pass
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokens:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token.
            
        Returns:
            OAuthTokens: New access tokens.
            
        Raises:
            NotImplementedError: If provider doesn't support refresh.
        """
        raise NotImplementedError(f"{self.provider_name} doesn't support token refresh")
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.
        
        Args:
            token: Token to revoke.
            
        Returns:
            bool: True if revocation successful.
            
        Raises:
            NotImplementedError: If provider doesn't support revocation.
        """
        raise NotImplementedError(f"{self.provider_name} doesn't support token revocation")