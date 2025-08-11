"""User model."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Unique identifier (UUID).
        email: User's email address (unique).
        hashed_password: Bcrypt hashed password (nullable for social-only accounts).
        is_active: Whether the user account is active.
        is_superuser: Whether the user has admin privileges.
        last_login: Timestamp of last successful login.
        created_at: Account creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for social-only accounts
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_email_active", email, is_active),
        Index("idx_user_last_login", last_login),
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"
    
    def update_last_login(self) -> None:
        """Update the last login timestamp to now."""
        self.last_login = datetime.utcnow()
    
    def is_password_set(self) -> bool:
        """Check if user has a password set."""
        return self.hashed_password is not None
    
    def can_login_with_password(self) -> bool:
        """Check if user can login with email/password."""
        return self.is_active and self.is_password_set()