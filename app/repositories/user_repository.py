"""User repository for database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.core.security import hash_password
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for User model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
    
    def create(self, email: str, password: Optional[str] = None, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address.
            password: Plain text password (will be hashed).
            **kwargs: Additional user attributes.
            
        Returns:
            User: Created user instance.
            
        Example:
            ```python
            user = user_repo.create("user@example.com", "password123")
            ```
        """
        hashed_password = hash_password(password) if password else None
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created user: {user.email}")
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for.
            
        Returns:
            Optional[User]: User if found, None otherwise.
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for.
            
        Returns:
            Optional[User]: User if found, None otherwise.
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_active_by_email(self, email: str) -> Optional[User]:
        """
        Get active user by email address.
        
        Args:
            email: Email address to search for.
            
        Returns:
            Optional[User]: Active user if found, None otherwise.
        """
        return self.db.query(User).filter(
            and_(User.email == email, User.is_active == True)
        ).first()
    
    def update(self, user: User, **kwargs) -> User:
        """
        Update user attributes.
        
        Args:
            user: User instance to update.
            **kwargs: Attributes to update.
            
        Returns:
            User: Updated user instance.
        """
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_password(self, user: User, new_password: str) -> User:
        """
        Update user password.
        
        Args:
            user: User instance to update.
            new_password: New plain text password.
            
        Returns:
            User: Updated user instance.
        """
        user.hashed_password = hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Updated password for user: {user.email}")
        return user
    
    def deactivate(self, user: User) -> User:
        """
        Deactivate a user account.
        
        Args:
            user: User instance to deactivate.
            
        Returns:
            User: Updated user instance.
        """
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Deactivated user: {user.email}")
        return user
    
    def delete(self, user: User) -> None:
        """
        Delete a user (hard delete).
        
        Args:
            user: User instance to delete.
        """
        self.db.delete(user)
        self.db.commit()
        
        logger.info(f"Deleted user: {user.email}")
    
    def list_users(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """
        List users with pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            active_only: Whether to return only active users.
            
        Returns:
            List[User]: List of users.
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def count_users(self, active_only: bool = True) -> int:
        """
        Count total number of users.
        
        Args:
            active_only: Whether to count only active users.
            
        Returns:
            int: Total number of users.
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.count()
    
    def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: Email address to check.
            
        Returns:
            bool: True if user exists, False otherwise.
        """
        return self.db.query(User).filter(User.email == email).first() is not None