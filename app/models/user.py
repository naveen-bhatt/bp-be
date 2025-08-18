"""User model."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime, Index, Enum as SQLAlchemyEnum

from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserRole(enum.Enum):
    """User role enumeration."""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"


class UserType(enum.Enum):
    """User type enumeration."""
    ANONYMOUS = "ANONYMOUS"
    SOCIAL = "SOCIAL"
    EMAIL = "EMAIL"
    PHONE = "PHONE"


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
    display_picture = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    user_type = Column(SQLAlchemyEnum(UserType), default=UserType.ANONYMOUS, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Future columns (will be added via migration)
    # user_type = Column(Enum(UserType), default=UserType.REGISTERED, nullable=False)
    # is_superuser = Column(Boolean, default=False, nullable=False)
    # last_login = Column(DateTime, nullable=True)
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_email_active", email, is_active),
        Index("idx_user_role", role),
        Index("idx_user_display_picture", display_picture),
        Index("idx_user_phone", phone),
        Index("idx_user_type", user_type),
        # Future indexes (will be added via migration)
        # Index("idx_user_last_login", last_login),
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
        return self.user_type == UserType.ANONYMOUS
    
    def is_registered(self) -> bool:
        """Check if user is registered."""
        return not self.is_anonymous()
    
    def is_social(self) -> bool:
        """Check if user is social."""
        return self.user_type == UserType.SOCIAL
    
    def is_email(self) -> bool:
        """Check if user is email type."""
        return self.user_type == UserType.EMAIL
    
    def is_phone(self) -> bool:
        """Check if user is phone type."""
        return self.user_type == UserType.PHONE
    
    def has_admin_access(self) -> bool:
        """Check if user has admin or superadmin access."""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    def is_admin_user(self) -> bool:
        """Check if user is admin (but not superadmin)."""
        return self.role == UserRole.ADMIN
    
    def is_superadmin(self) -> bool:
        """Check if user is superadmin."""
        return self.role == UserRole.SUPERADMIN
    
    def is_superuser(self) -> bool:
        """Check if user is superadmin (alias for is_superadmin for compatibility)."""
        return self.role == UserRole.SUPERADMIN
    
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