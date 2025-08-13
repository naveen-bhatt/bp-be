"""Wishlist controller."""

from fastapi import HTTPException, status

from app.core.dependencies import DatabaseSession, OptionalUserId
from app.schemas.wishlist import AddToWishlistRequest, WishlistResponse
from app.schemas.common import SuccessResponse
from app.services.wishlist_service import WishlistService


def get_wishlist(
    user_id: OptionalUserId,
    db: DatabaseSession
) -> WishlistResponse:
    """
    Get current user's wishlist.
    
    Args:
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        WishlistResponse: Current wishlist with items.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access wishlist"
            )
            
        wishlist_service = WishlistService(db)
        return wishlist_service.get_wishlist(user_id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get wishlist: {str(e)}"
        )


def toggle_wishlist(
    product_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> WishlistResponse:
    """
    Add product to wishlist.
    
    Args:
        product_id: Product ID to toggle.
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        WishlistResponse: Updated wishlist.
        
    Raises:
        HTTPException: If add to wishlist fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to add items to wishlist"
            )
            
        wishlist_service = WishlistService(db)
        return wishlist_service.toggle_wishlist(
            user_id=user_id,
            product_id=product_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add item to wishlist: {str(e)}"
        )


def remove_from_wishlist(
    product_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> WishlistResponse:
    """
    Remove product from wishlist.
    
    Args:
        product_id: Product ID to remove.
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        WishlistResponse: Updated wishlist.
        
    Raises:
        HTTPException: If removal fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to remove items from wishlist"
            )
            
        wishlist_service = WishlistService(db)
        return wishlist_service.remove_from_wishlist(
            user_id=user_id,
            product_id=product_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove item from wishlist: {str(e)}"
        )


def clear_wishlist(
    user_id: OptionalUserId,
    db: DatabaseSession
) -> SuccessResponse:
    """
    Clear all items from wishlist.
    
    Args:
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        SuccessResponse: Clear confirmation.
        
    Raises:
        HTTPException: If clear fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to clear wishlist"
            )
            
        wishlist_service = WishlistService(db)
        wishlist_service.clear_wishlist(user_id=user_id)
        
        return SuccessResponse(message="Wishlist cleared successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear wishlist: {str(e)}"
        )
