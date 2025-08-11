"""Social account model for OAuth integrations."""

from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from .base import BaseModel


class SocialProvider(str, Enum):
    """Supported social authentication providers."""
    
    GOOGLE = "google"
    GITHUB = "github"
    APPLE = "apple"


class SocialAccount(BaseModel):
    """
    Social account model for OAuth provider integrations.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model.
        provider: OAuth provider (google, github, apple).
        provider_account_id: Account ID from the provider.
        access_token: OAuth access token (optional).
        refresh_token: OAuth refresh token (optional).
        created_at: Account creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "social_accounts"
    
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_account_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="social_accounts")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_social_provider_account", provider, provider_account_id, unique=True),
        Index("idx_social_user_provider", user_id, provider, unique=True),
    )
    
    def __repr__(self) -> str:
        """String representation of the social account."""
        return f"<SocialAccount(id={self.id}, provider={self.provider}, user_id={self.user_id})>"
    
    def update_tokens(self, access_token: Optional[str], refresh_token: Optional[str] = None) -> None:
        """
        Update OAuth tokens.
        
        Args:
            access_token: New access token.
            refresh_token: New refresh token (optional).
        """
        self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token