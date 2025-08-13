"""Authentication service for business logic."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import create_anonymous_token, verify_password, hash_password, create_token_pair, verify_token
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
            
            # Update last login (will be implemented when last_login column is added)
            try:
                user.update_last_login()
                self.db.commit()
            except Exception as e:
                logger.warning(f"Could not update last login: {e}")
                # Continue without updating last login
            
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
    
    def register(self, user_id: str, email: str, password: str) -> Dict[str, str]:
        """
        Register a user by converting an anonymous user.
        
        Args:
            user_id: ID of the anonymous user to convert.
            email: User's email address.
            password: User's password.
            
        Returns:
            Dict[str, str]: Token pair for the registered user.
            
        Raises:
            ValueError: If user not found, not anonymous, or email already exists.
        """
        try:
            logger.info(f"Attempting registration conversion for user {user_id} with email: {email}")
            
            # Get the user first to check its current state
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # If user is already registered, check if it's the same email
            if not user.is_anonymous():
                if user.email == email:
                    logger.info(f"User {user_id} already registered with email: {email}")
                    # User already registered with this email, just return tokens
                    user_data = {
                        "sub": str(user.id),
                        "email": user.email,
                        "user_type": getattr(user, 'user_type', 'registered').value if hasattr(user, 'user_type') and user.user_type else 'registered'
                    }
                    tokens = create_token_pair(user_data)
                    return tokens
                else:
                    raise ValueError(f"User already registered with different email: {user.email}")
            
            # Convert anonymous user to registered
            user = self.user_repo.convert_anonymous_to_registered(user_id, email, password)
            if not user:
                raise ValueError("User not found or conversion failed")
            
            # Create tokens
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": getattr(user, 'user_type', 'registered').value if hasattr(user, 'user_type') and user.user_type else 'registered'
            }
            
            tokens = create_token_pair(user_data)
            logger.info(f"Successful registration conversion for user: {email}")
            return tokens
            
        except Exception as e:
            logger.error(f"Registration error for user {user_id} with email {email}: {str(e)}")
            raise
    
    def social_register(self, user_id: str, email: str, provider: str, provider_account_id: str = None) -> Dict[str, str]:
        """
        Register a user via social login by converting an anonymous user.
        
        Args:
            user_id: ID of the anonymous user to convert.
            email: User's email address from social provider.
            provider: Social provider name.
            provider_account_id: Account ID from the provider (optional).
            
        Returns:
            Dict[str, str]: Token pair for the registered user.
            
        Raises:
            ValueError: If user not found or not anonymous.
        """
        try:
            logger.info(f"Attempting social registration conversion for user {user_id} with email: {email} (provider: {provider})")
            
            # Convert anonymous user to social
            user = self.user_repo.convert_anonymous_to_social(user_id, email, provider)
            if not user:
                raise ValueError("User not found or conversion failed")
            
            # Create social account if provider_account_id is provided
            if provider_account_id:
                from app.repositories.social_repository import SocialRepository
                from app.models.social_account import SocialProvider
                
                social_repo = SocialRepository(self.db)
                social_repo.create(
                    user_id=str(user.id),
                    provider=SocialProvider(provider),
                    provider_account_id=provider_account_id
                )
                logger.info(f"Created social account for user {user.id} with provider {provider}")
            
            # Create tokens
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": getattr(user, 'user_type', 'social').value if hasattr(user, 'user_type') and user.user_type else 'social'
            }
            
            tokens = create_token_pair(user_data)
            logger.info(f"Successful social registration conversion for user: {email}")
            return tokens
            
        except Exception as e:
            logger.error(f"Social registration error for user {user_id} with email {email}: {str(e)}")
            raise
    
    def social_login(self, email: str, provider: str, provider_account_id: str) -> Dict[str, str]:
        """
        Login a user via social OAuth (existing users).
        
        Args:
            email: User's email address from social provider.
            provider: Social provider name.
            provider_account_id: Account ID from the provider.
            
        Returns:
            Dict[str, str]: Token pair for the logged in user.
            
        Raises:
            ValueError: If user not found or social account doesn't exist.
        """
        try:
            logger.info(f"Attempting social login for user with email: {email} (provider: {provider})")
            
            # First check if a user with this email exists
            user = self.user_repo.get_by_email(email)
            if not user:
                raise ValueError(f"No user found with email {email}")
            
            # Check if user has a social account for this provider
            from app.repositories.social_repository import SocialRepository
            from app.models.social_account import SocialProvider
            
            social_repo = SocialRepository(self.db)
            social_account = social_repo.get_by_user_and_provider(
                user_id=str(user.id),
                provider=SocialProvider(provider)
            )
            
            if not social_account:
                raise ValueError(f"User {email} exists but has no social account for provider {provider}")
            
            # Update last login (will be implemented when last_login column is added)
            try:
                user.update_last_login()
                self.db.commit()
            except Exception as e:
                logger.warning(f"Could not update last login: {e}")
                # Continue without updating last login
            
            # Create tokens
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": getattr(user, 'user_type', 'social').value if hasattr(user, 'user_type') and user.user_type else 'social'
            }
            
            tokens = create_token_pair(user_data)
            logger.info(f"Successful social login for user: {email}")
            return tokens
            
        except Exception as e:
            logger.error(f"Social login error for email {email} with provider {provider}: {str(e)}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token.
            
        Returns:
            Dict[str, str]: New token pair.
            
        Raises:
            HTTPException: If refresh token is invalid or user not found.
        """
        try:
            logger.info("Attempting to refresh access token")
            
            # Verify refresh token
            payload = verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            
            if not user_id:
                raise ValueError("Invalid token: missing user ID")
            
            # Get user from database to ensure they still exist and are active
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            if not user.is_active:
                raise ValueError("User account is not active")
            
            # Create new token pair
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": getattr(user, 'user_type', 'registered').value if hasattr(user, 'user_type') and user.user_type else 'registered'
            }
            
            tokens = create_token_pair(user_data)
            logger.info(f"Successfully refreshed tokens for user: {user.email}")
            return tokens
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise
