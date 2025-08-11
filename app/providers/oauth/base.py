"""Base OAuth provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OAuthTokens:
    """OAuth token response."""
    
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"


@dataclass
class OAuthUserInfo:
    """OAuth user information."""
    
    email: str
    provider_account_id: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    verified: bool = False


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
    async def exchange_code_for_tokens(self, code: str, redirect_uri: Optional[str] = None) -> OAuthTokens:
        """
        Exchange authorization code for access tokens.
        
        Args:
            code: Authorization code from OAuth callback.
            redirect_uri: Redirect URI used in authorization.
            
        Returns:
            OAuthTokens: Access and refresh tokens.
            
        Raises:
            ValueError: If code exchange fails.
        """
        pass
    
    @abstractmethod
    async def verify_id_token(self, id_token: str) -> OAuthUserInfo:
        """
        Verify ID token and extract user information.
        
        Args:
            id_token: JWT ID token from OAuth provider.
            
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
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Get authorization URL for OAuth flow.
        
        Args:
            redirect_uri: Redirect URI for callback.
            state: Optional state parameter for CSRF protection.
            
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