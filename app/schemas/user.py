"""User schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from .common import BaseSchema, UUIDMixin, TimestampMixin


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr = Field(..., description="User email address")
    is_active: bool = Field(default=True, description="Whether user is active")


class UserCreate(UserBase):
    """User creation schema."""
    
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """User update schema."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    is_active: Optional[bool] = Field(None, description="Whether user is active")


class UserPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public user schema (safe for API responses)."""
    
    email: str = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether user is active")
    is_superuser: bool = Field(..., description="Whether user has admin privileges")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class UserProfile(UserPublic):
    """User profile schema (for authenticated user's own data)."""
    
    social_accounts: list["SocialAccountPublic"] = Field(
        default_factory=list,
        description="Connected social accounts"
    )


class UserAdmin(UserPublic):
    """Admin user schema (includes sensitive fields for admins)."""
    
    pass  # Inherits all fields from UserPublic


class SocialAccountPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public social account schema."""
    
    provider: str = Field(..., description="OAuth provider")
    provider_account_id: str = Field(..., description="Account ID from provider")


# Forward reference resolution
UserProfile.model_rebuild()