"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

from .common import BaseSchema


class LoginRequest(BaseModel):
    """User login request."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class RegisterRequest(BaseModel):
    """User registration request."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v


class TokenResponse(BaseModel):
    """Token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""
    
    refresh_token: str = Field(..., description="JWT refresh token")


class SocialLoginRequest(BaseModel):
    """Social login request."""
    
    provider: str = Field(..., description="OAuth provider (google, github, apple)")
    id_token: Optional[str] = Field(None, description="OAuth ID token")
    code: Optional[str] = Field(None, description="OAuth authorization code")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate OAuth provider."""
        allowed_providers = ['google', 'github', 'apple']
        if v.lower() not in allowed_providers:
            raise ValueError(f'Provider must be one of: {", ".join(allowed_providers)}')
        return v.lower()
    
    @field_validator('id_token')
    @classmethod
    def validate_token_or_code(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that either id_token or code is provided."""
        if not v and not info.data.get('code'):
            raise ValueError('Either id_token or code must be provided')
        return v


class GoogleOneTapRequest(BaseModel):
    """Google One Tap sign-in request."""
    
    id_token: str = Field(..., description="Google ID token from One Tap")
    anonymous_user_id: Optional[str] = Field(None, description="Optional anonymous user ID to convert")


class GoogleOneTapResponse(BaseModel):
    """Google One Tap sign-in response."""
    
    success: bool = Field(..., description="Whether the sign-in was successful")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user_email: str = Field(..., description="User's email address")


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v


class AnonymousTokenResponse(BaseModel):
    """Anonymous user token response."""
    
    access_token: str = Field(..., description="JWT access token for anonymous user")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Access token expiration in seconds (null for no expiration)")
    user_id: str = Field(..., description="Anonymous user ID")
    user_type: str = Field(default="anonymous", description="User type")


class AnonymousUserInfo(BaseModel):
    """Anonymous user information."""
    
    id: str = Field(..., description="User ID")
    user_type: str = Field(..., description="User type")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True