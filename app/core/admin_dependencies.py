"""Admin dependencies for role-based access control."""

from typing import Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_id, DatabaseSession
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


async def get_admin_user(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(DatabaseSession)
) -> User:
    """
    Dependency to ensure current user has admin or superadmin role.
    
    Args:
        current_user_id: Current authenticated user ID.
        db: Database session.
        
    Returns:
        User: Admin user if authorized.
        
    Raises:
        HTTPException: If user doesn't have admin access.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.has_admin_access():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user


async def get_superadmin_user(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(DatabaseSession)
) -> User:
    """
    Dependency to ensure current user has superadmin role.
    
    Args:
        current_user_id: Current authenticated user ID.
        db: Database session.
        
    Returns:
        User: Superadmin user if authorized.
        
    Raises:
        HTTPException: If user doesn't have superadmin access.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_superadmin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    
    return user


async def get_user_by_id(
    user_id: str,
    db: Session = Depends(DatabaseSession)
) -> Optional[User]:
    """
    Get user by ID for admin operations.
    
    Args:
        user_id: User ID to fetch.
        db: Database session.
        
    Returns:
        Optional[User]: User if found, None otherwise.
    """
    user_repo = UserRepository(db)
    return user_repo.get_by_id(user_id)
