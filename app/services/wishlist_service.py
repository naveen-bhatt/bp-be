"""Wishlist service with business logic."""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.wishlist import WishlistItemPublic, WishlistResponse
from app.models.wishlist import WishlistItem


class WishlistService:
    """Service for wishlist operations."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.wishlist_repo = WishlistRepository(db)
        self.product_repo = ProductRepository(db)
    
    def get_wishlist(self, user_id: str) -> WishlistResponse:
        """
        Get user's wishlist.
        
        Args:
            user_id: User ID.
            
        Returns:
            WishlistResponse: Wishlist with items.
        """
        # Get all wishlist items for the user
        items = self.wishlist_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_wishlist_schema(items)
    
    def toggle_wishlist(self, user_id: str, product_id: str) -> WishlistResponse:
        """
        Toggle product in wishlist.
        
        Args:
            user_id: User ID.
            product_id: Product ID to add.
            
        Returns:
            WishlistResponse: Updated wishlist.
            
        Raises:
            ValueError: If product not found or already in wishlist.
        """
        # Add item to wishlist
        self.wishlist_repo.toggle_item(user_id, product_id)
        
        # Get updated wishlist
        items = self.wishlist_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_wishlist_schema(items)
    
    def remove_from_wishlist(self, user_id: str, product_id: str) -> WishlistResponse:
        """
        Remove product from wishlist.
        
        Args:
            user_id: User ID.
            product_id: Product ID to remove.
            
        Returns:
            WishlistResponse: Updated wishlist.
            
        Raises:
            ValueError: If product not found in wishlist.
        """
        # Remove item from wishlist
        self.wishlist_repo.remove_item(user_id, product_id)
        
        # Get updated wishlist
        items = self.wishlist_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_wishlist_schema(items)
    
    def remove_wishlist_item(self, user_id: str, item_id: str) -> WishlistResponse:
        """
        Remove wishlist item by ID.
        
        Args:
            user_id: User ID.
            item_id: Wishlist item ID to remove.
            
        Returns:
            WishlistResponse: Updated wishlist.
            
        Raises:
            ValueError: If item not found or not in user's wishlist.
        """
        # Remove item from wishlist
        self.wishlist_repo.remove_item_by_id(item_id, user_id)
        
        # Get updated wishlist
        items = self.wishlist_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_wishlist_schema(items)
    
    def is_product_in_wishlist(self, user_id: str, product_id: str) -> bool:
        """
        Check if a product is in a user's wishlist.
        
        Args:
            user_id: User ID.
            product_id: Product ID to check.
            
        Returns:
            bool: True if product is in wishlist, False otherwise.
        """
        return self.wishlist_repo.is_product_in_wishlist(user_id, product_id)
    
    def clear_wishlist(self, user_id: str) -> None:
        """
        Remove all items from user's wishlist.
        
        Args:
            user_id: User ID.
        """
        self.wishlist_repo.clear_wishlist(user_id)
    
    def _items_to_wishlist_schema(self, items: List[WishlistItem]) -> WishlistResponse:
        """
        Convert list of WishlistItem models to WishlistResponse schema.
        
        Args:
            items: List of wishlist items.
            
        Returns:
            WishlistResponse: Wishlist schema.
        """
        # Convert wishlist items
        item_schemas = []
        for item in items:
            item_schemas.append(WishlistItemPublic(
                id=item.id,
                product_id=item.product_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                product=self.product_repo.to_list_schema(item.product) if item.product else None
            ))
        
        # Create wishlist schema
        return WishlistResponse(
            items=item_schemas,
            total_items=len(items)
        )
