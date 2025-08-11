"""Social account repository for database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.social_account import SocialAccount, SocialProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class SocialRepository:
    """Repository for SocialAccount model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
    
    def create(
        self,
        user_id: str,
        provider: SocialProvider,
        provider_account_id: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ) -> SocialAccount:
        """
        Create a new social account.
        
        Args:
            user_id: User ID to associate with.
            provider: OAuth provider.
            provider_account_id: Account ID from provider.
            access_token: OAuth access token.
            refresh_token: OAuth refresh token.
            
        Returns:
            SocialAccount: Created social account instance.
        """
        social_account = SocialAccount(
            user_id=user_id,
            provider=provider.value,
            provider_account_id=provider_account_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        self.db.add(social_account)
        self.db.commit()
        self.db.refresh(social_account)
        
        logger.info(f"Created social account: {provider.value} for user {user_id}")
        return social_account
    
    def get_by_id(self, social_account_id: str) -> Optional[SocialAccount]:
        """
        Get social account by ID.
        
        Args:
            social_account_id: Social account ID to search for.
            
        Returns:
            Optional[SocialAccount]: Social account if found, None otherwise.
        """
        return self.db.query(SocialAccount).filter(
            SocialAccount.id == social_account_id
        ).first()
    
    def get_by_provider_account(
        self,
        provider: SocialProvider,
        provider_account_id: str
    ) -> Optional[SocialAccount]:
        """
        Get social account by provider and provider account ID.
        
        Args:
            provider: OAuth provider.
            provider_account_id: Account ID from provider.
            
        Returns:
            Optional[SocialAccount]: Social account if found, None otherwise.
        """
        return self.db.query(SocialAccount).filter(
            and_(
                SocialAccount.provider == provider.value,
                SocialAccount.provider_account_id == provider_account_id
            )
        ).first()
    
    def get_by_user_and_provider(
        self,
        user_id: str,
        provider: SocialProvider
    ) -> Optional[SocialAccount]:
        """
        Get social account by user ID and provider.
        
        Args:
            user_id: User ID to search for.
            provider: OAuth provider.
            
        Returns:
            Optional[SocialAccount]: Social account if found, None otherwise.
        """
        return self.db.query(SocialAccount).filter(
            and_(
                SocialAccount.user_id == user_id,
                SocialAccount.provider == provider.value
            )
        ).first()
    
    def list_by_user(self, user_id: str) -> List[SocialAccount]:
        """
        List all social accounts for a user.
        
        Args:
            user_id: User ID to search for.
            
        Returns:
            List[SocialAccount]: List of social accounts.
        """
        return self.db.query(SocialAccount).filter(
            SocialAccount.user_id == user_id
        ).all()
    
    def update_tokens(
        self,
        social_account: SocialAccount,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ) -> SocialAccount:
        """
        Update OAuth tokens for a social account.
        
        Args:
            social_account: Social account to update.
            access_token: New access token.
            refresh_token: New refresh token.
            
        Returns:
            SocialAccount: Updated social account instance.
        """
        if access_token is not None:
            social_account.access_token = access_token
        
        if refresh_token is not None:
            social_account.refresh_token = refresh_token
        
        self.db.commit()
        self.db.refresh(social_account)
        
        logger.info(f"Updated tokens for social account: {social_account.provider}")
        return social_account
    
    def delete(self, social_account: SocialAccount) -> None:
        """
        Delete a social account.
        
        Args:
            social_account: Social account to delete.
        """
        self.db.delete(social_account)
        self.db.commit()
        
        logger.info(f"Deleted social account: {social_account.provider} for user {social_account.user_id}")
    
    def exists_for_user_and_provider(self, user_id: str, provider: SocialProvider) -> bool:
        """
        Check if social account exists for user and provider.
        
        Args:
            user_id: User ID to check.
            provider: OAuth provider to check.
            
        Returns:
            bool: True if social account exists, False otherwise.
        """
        return self.db.query(SocialAccount).filter(
            and_(
                SocialAccount.user_id == user_id,
                SocialAccount.provider == provider.value
            )
        ).first() is not None