"""Cart controller."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import DatabaseSession, OptionalUserId
from app.schemas.cart import (
    AddToCartRequest, UpdateCartItemRequest, CartPublic,
    CartSummary, CartClearRequest
)
from app.schemas.common import SuccessResponse
from app.services.cart_service import CartService

def get_cart(
    user_id: OptionalUserId,
    db: DatabaseSession
) -> CartPublic:
    """
    Get current user's cart.
    
    Args:
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        CartPublic: Current cart with items.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access cart"
            )
            
        cart_service = CartService(db)
        return cart_service.get_cart(user_id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cart: {str(e)}"
        )


def get_cart_summary(
    user_id: OptionalUserId,
    db: DatabaseSession
) -> CartSummary:
    """
    Get cart summary (totals only).
    
    Args:
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        CartSummary: Cart totals.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access cart summary"
            )
            
        cart_service = CartService(db)
        return cart_service.get_cart_summary(user_id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cart summary: {str(e)}"
        )


def add_to_cart(
    request: AddToCartRequest,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> CartPublic:
    """
    Add item to cart.
    
    Args:
        request: Add to cart data.
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        CartPublic: Updated cart.
        
    Raises:
        HTTPException: If add to cart fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to add items to cart"
            )
            
        cart_service = CartService(db)
        return cart_service.add_to_cart(
            product_id=request.product_id,
            quantity=request.quantity,
            user_id=user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add item to cart: {str(e)}"
        )


def update_cart_item(
    product_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> CartPublic:
    """
    Update cart item quantity.
    
    Args:
        product_id: Product ID to update.
        request: Update data.
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        CartPublic: Updated cart.
        
    Raises:
        HTTPException: If update fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to update cart items"
            )
            
        cart_service = CartService(db)
        return cart_service.update_cart_item(
            product_id=product_id,
            user_id=user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cart item: {str(e)}"
        )

def clear_a_product_from_cart(
    product_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> CartPublic:
    """
    Completely remove a product from cart regardless of quantity.
    
    Args:
        product_id: Product ID to remove completely.
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        CartPublic: Updated cart.
        
    Raises:
        HTTPException: If removal fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to remove cart items"
            )
            
        cart_service = CartService(db)
        return cart_service.clear_product_from_cart(
            product_id=product_id,
            user_id=user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove product from cart: {str(e)}"
        )




def remove_cart_item(
    product_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> CartPublic:
    """
    Remove item from cart.
    
    Args:
        product_id: Product ID to remove.
        user_id: User ID from JWT token (anonymous or registered).
        db: Database session.
        
    Returns:
        CartPublic: Updated cart.
        
    Raises:
        HTTPException: If removal fails.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to remove cart items"
            )
            
        cart_service = CartService(db)
        return cart_service.remove_cart_item(
            product_id=product_id,
            user_id=user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove cart item: {str(e)}"
        )


# Note: merge_guest_cart method is no longer needed since we're using a single user ID
# for both anonymous and registered users. When a user registers, their cart
# is already associated with their user ID.


def clear_cart(
    request: CartClearRequest,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> SuccessResponse:
    """
    Clear all items from cart.
    
    Args:
        request: Clear cart confirmation.
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
                detail="Authentication required to clear cart"
            )
            
        # Confirmation is validated by pydantic
        cart_service = CartService(db)
        cart_service.clear_cart(user_id=user_id)
        
        return SuccessResponse(message="Cart cleared successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cart: {str(e)}"
        )