"""GitHub OAuth provider implementation."""

from typing import Optional
import httpx

from .base import OAuthProvider, OAuthTokens, OAuthUserInfo
from app.core.logging import get_logger

logger = get_logger(__name__)


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth 2.0 provider implementation."""
    
    AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    USER_EMAILS_URL = "https://api.github.com/user/emails"
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize GitHub OAuth provider."""
        super().__init__(client_id, client_secret)
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "github"
    
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Get GitHub authorization URL.
        
        Args:
            redirect_uri: Redirect URI for callback.
            state: Optional state parameter for CSRF protection.
            
        Returns:
            str: Authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "user:email",
            "response_type": "code"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, redirect_uri: Optional[str] = None) -> OAuthTokens:
        """
        Exchange authorization code for GitHub tokens.
        
        Args:
            code: Authorization code from GitHub callback.
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
            "redirect_uri": redirect_uri
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.TOKEN_URL, data=data, headers=headers)
                response.raise_for_status()
                
                token_data = response.json()
                
                # Check for errors in response
                if "error" in token_data:
                    raise ValueError(token_data.get("error_description", "Token exchange failed"))
                
                return OAuthTokens(
                    access_token=token_data["access_token"],
                    token_type=token_data.get("token_type", "Bearer")
                )
                
        except Exception as e:
            logger.error(f"GitHub token exchange failed: {e}")
            raise ValueError(f"Failed to exchange code for tokens: {e}")
    
    async def verify_id_token(self, id_token: str, access_token: str, nonce: Optional[str] = None) -> OAuthUserInfo:
        """
        GitHub doesn't provide ID tokens, so this is not supported.
        
        Args:
            id_token: Not used for GitHub.
            access_token: Not used for GitHub.
            nonce: Not used for GitHub.
            
        Raises:
            NotImplementedError: GitHub doesn't use ID tokens.
        """
        raise NotImplementedError("GitHub doesn't provide ID tokens. Use authorization code flow.")
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Get user information using GitHub access token.
        
        Args:
            access_token: GitHub access token.
            
        Returns:
            OAuthUserInfo: User information.
            
        Raises:
            ValueError: If user info retrieval fails.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Get user profile
                user_response = await client.get(self.USER_URL, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()
                
                # Get user emails
                email_response = await client.get(self.USER_EMAILS_URL, headers=headers)
                email_response.raise_for_status()
                emails_data = email_response.json()
                
                # Find primary/verified email
                primary_email = None
                verified = False
                
                for email_info in emails_data:
                    if email_info.get("primary", False):
                        primary_email = email_info["email"]
                        verified = email_info.get("verified", False)
                        break
                
                # Fallback to first email if no primary found
                if not primary_email and emails_data:
                    email_info = emails_data[0]
                    primary_email = email_info["email"]
                    verified = email_info.get("verified", False)
                
                # Fallback to public email from profile
                if not primary_email:
                    primary_email = user_data.get("email")
                
                if not primary_email:
                    raise ValueError("No email address found in GitHub profile")
                
                return OAuthUserInfo(
                    email=primary_email,
                    provider_account_id=str(user_data["id"]),
                    name=user_data.get("name") or user_data.get("login"),
                    avatar_url=user_data.get("avatar_url"),
                    verified=verified
                )
                
        except Exception as e:
            logger.error(f"GitHub user info retrieval failed: {e}")
            raise ValueError(f"Failed to get user info: {e}")
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke GitHub access token.
        
        Args:
            token: Token to revoke.
            
        Returns:
            bool: True if revocation successful.
        """
        # GitHub uses HTTP Basic Auth with client credentials
        import base64
        
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        data = {"access_token": token}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"https://api.github.com/applications/{self.client_id}/token",
                    headers=headers,
                    json=data
                )
                return response.status_code == 204
                
        except Exception as e:
            logger.error(f"GitHub token revocation failed: {e}")
            return False