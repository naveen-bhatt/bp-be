"""User model."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime, Index, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserType(enum.Enum):
    """User type enumeration."""
    ANONYMOUS = "anonymous"
    REGISTERED = "registered"
    SOCIAL = "social"


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
    
    # Current database schema columns
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Current column name in DB
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)  # Current column name in DB
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Future columns (will be added via migration)
    # user_type = Column(Enum(UserType), default=UserType.REGISTERED, nullable=False)
    # is_superuser = Column(Boolean, default=False, nullable=False)
    # last_login = Column(DateTime, nullable=True)
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_email_active", email, is_active),
        # Future indexes (will be added via migration)
        # Index("idx_user_last_login", last_login),
        # Index("idx_user_type", user_type),
        # Index("idx_user_type_active", user_type, is_active),
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"
    
    def update_last_login(self) -> None:
        """Update the last login timestamp to now."""
        # Will be implemented when last_login column is added
        pass
    
    def is_password_set(self) -> bool:
        """Check if user has a password set."""
        return self.password_hash is not None
    
    def can_login_with_password(self) -> bool:
        """Check if user can login with email/password."""
        return self.is_active and self.is_password_set()
    
    def is_anonymous(self) -> bool:
        """Check if user is anonymous."""
        # For now, check if email contains 'anonymous' until user_type column is added
        return self.email and "anonymous_" in self.email and "@temp.local" in self.email
    
    def is_registered(self) -> bool:
        """Check if user is registered."""
        return not self.is_anonymous()
    
    def is_social(self) -> bool:
        """Check if user is social."""
        # Will be implemented when user_type column is added
        return False
    
    def convert_to_registered(self, email: str, hashed_password: str) -> None:
        """Convert anonymous user to registered user."""
        if not self.is_anonymous():
            raise ValueError("Can only convert anonymous users")
        
        self.email = email
        self.password_hash = hashed_password
        self.update_last_login()
    
    def convert_to_social(self, email: str) -> None:
        """Convert anonymous user to social user."""
        if not self.is_anonymous():
            raise ValueError("Can only convert anonymous users")
        
        self.email = email
        self.update_last_login()