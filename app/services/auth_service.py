"""Authentication service for business logic."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import create_anonymous_token, verify_password, hash_password, create_token_pair
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    def create_anonymous_user(self) -> Dict[str, Any]:
        """
        Create an anonymous user for guest sessions.
        
        Returns:
            Dict[str, Any]: Anonymous user token data.
            
        Raises:
            Exception: If anonymous user creation fails.
        """
        try:
            logger.info("Creating anonymous user")
            
            # Create anonymous user
            anonymous_user = self.user_repo.create_anonymous()
            
            # Generate token for anonymous user
            token_data = create_anonymous_token(str(anonymous_user.id))
            
            logger.info(f"Created anonymous user with ID: {anonymous_user.id}")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to create anonymous user: {str(e)}")
            raise
    
    def login(self, email: str, password: str) -> Optional[Dict[str, str]]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address.
            password: User's password.
            
        Returns:
            Optional[Dict[str, str]]: Token pair if successful, None if failed.
        """
        try:
            logger.info(f"Attempting login for email: {email}")
            
            # Get user by email
            user = self.user_repo.get_by_email(email)
            if not user:
                logger.warning(f"User not found: {email}")
                return None
            
            # Verify password
            if not user.can_login_with_password():
                logger.warning(f"User cannot login with password: {email}")
                return None
            
            if not verify_password(password, user.password_hash):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            # Update last login
            user.update_last_login()
            self.db.commit()
            
            # Create tokens
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": getattr(user, 'user_type', 'registered').value if hasattr(user, 'user_type') and user.user_type else 'registered'
            }
            
            tokens = create_token_pair(user_data)
            logger.info(f"Successful login for user: {email}")
            return tokens
            
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}")
            raise
    
    def register(self, email: str, password: str) -> Dict[str, str]:
        """
        Register a new user.
        
        Args:
            email: User's email address.
            password: User's password.
            
        Returns:
            Dict[str, str]: Token pair for the new user.
            
        Raises:
            ValueError: If email already exists.
        """
        try:
            logger.info(f"Attempting registration for email: {email}")
            
            # Check if user already exists
            existing_user = self.user_repo.get_by_email(email)
            if existing_user:
                raise ValueError("Email already registered")
            
            # Create new user
            user = self.user_repo.create(email=email, password=password)
            
            # Create tokens
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": getattr(user, 'user_type', 'registered').value if hasattr(user, 'user_type') and user.user_type else 'registered'
            }
            
            tokens = create_token_pair(user_data)
            logger.info(f"Successful registration for user: {email}")
            return tokens
            
        except Exception as e:
            logger.error(f"Registration error for {email}: {str(e)}")
            raise
