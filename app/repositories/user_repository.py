"""User repository for database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User, UserRole, UserType
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
    
    def create(self, email: str, password_hash: str, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address.
            password_hash: Hashed password.
            **kwargs: Additional user attributes.
            
        Returns:
            User: Created user instance.
            
        Raises:
            ValueError: If email already exists.
        """
        # Check if email already exists
        if self.get_by_email(email):
            logger.warning(f"Email already exists: {email}")
            raise ValueError("Email already registered")
        
        # Set role based on is_admin flag for backward compatibility
        role = kwargs.get('role', UserRole.USER.value)
        if kwargs.get('is_admin', False):
            role = UserRole.ADMIN.value
        
        # Set user type
        user_type = kwargs.get('user_type', UserType.EMAIL.value)
        
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
            is_active=kwargs.get('is_active', True),
            is_admin=kwargs.get('is_admin', False),
            email_verified=kwargs.get('email_verified', False),
            display_picture=kwargs.get('display_picture'),
            phone=kwargs.get('phone'),
            user_type=user_type,
            role=role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created user: {user.email}")
        return user
    
    def create_anonymous(self) -> User:
        """
        Create an anonymous user for guest sessions.
        
        Returns:
            User: Created anonymous user instance.
            
        Example:
            ```python
            anonymous_user = user_repo.create_anonymous()
            ```
        """
        # Generate a unique email for anonymous users for now
        import uuid
        anonymous_email = f"anonymous_{str(uuid.uuid4())[:8]}@temp.local"
        
        user = User(
            email=anonymous_email,  # Temporary email for anonymous users
            password_hash=hash_password("anonymous_temp_password"),  # Temporary password for anonymous users
            first_name=None,
            last_name=None,
            is_active=True,
            is_admin=False,
            email_verified=False,
            user_type=UserType.ANONYMOUS,
            role=UserRole.USER.value
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created anonymous user: {user.id} with temp email: {anonymous_email}")
        return user
    
    def convert_anonymous_to_registered(self, user_id: str, email: str, password: str) -> Optional[User]:
        """
        Convert an anonymous user to a registered user.
        
        Args:
            user_id: ID of the anonymous user to convert.
            email: New email address for the user.
            password: Plain text password (will be hashed).
            
        Returns:
            Optional[User]: Updated user if successful, None if user not found or not anonymous.
            
        Raises:
            ValueError: If user is not anonymous or email already exists.
        """
        # Get the user
        user = self.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found for conversion: {user_id}")
            return None
        
        # Check if user is anonymous
        if not user.is_anonymous():
            logger.warning(f"User {user_id} is not anonymous, cannot convert")
            raise ValueError("User is not anonymous")
        
        # Check if email already exists
        existing_user = self.get_by_email(email)
        if existing_user and existing_user.id != user_id:
            logger.warning(f"Email already exists: {email}")
            raise ValueError("Email already registered")
        
        # Update user to registered
        user.email = email
        user.password_hash = hash_password(password)
        user.email_verified = False  # Will be verified later via email
        user.user_type = UserType.EMAIL  # Set user type to EMAIL
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Converted anonymous user {user_id} to registered user with email: {email}")
        return user
    
    def convert_anonymous_to_social(self, user_id: str, email: str, provider: str) -> Optional[User]:
        """
        Convert an anonymous user to a social user.
        
        Args:
            user_id: ID of the anonymous user to convert.
            email: Email address from social provider.
            provider: Social provider name.
            
        Returns:
            Optional[User]: Updated user if successful, None if user not found or not anonymous.
            
        Raises:
            ValueError: If user is not anonymous.
        """
        # Get the user
        user = self.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found for social conversion: {user_id}")
            return None
        
        # Check if user is anonymous
        if not user.is_anonymous():
            logger.warning(f"User {user_id} is not anonymous, cannot convert")
            raise ValueError("User is not anonymous")
        
        # Update user to social
        user.email = email
        user.password_hash = hash_password("social_temp_password")  # Temporary password for social users
        user.email_verified = True  # Social providers verify emails
        user.user_type = UserType.SOCIAL  # Set user type to SOCIAL
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Converted anonymous user {user_id} to social user with email: {email} (provider: {provider})")
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