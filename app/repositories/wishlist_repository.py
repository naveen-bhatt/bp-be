"""Wishlist repository for database operations."""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.wishlist import WishlistItem
from app.models.product import Product


class WishlistRepository:
    """Repository for wishlist operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
    
    def get_items_by_user_id(self, user_id: str) -> List[WishlistItem]:
        """
        Get all wishlist items for a user.
        
        Args:
            user_id: User ID to find wishlist items for.
            
        Returns:
            List[WishlistItem]: List of wishlist items.
        """
        stmt = (
            select(WishlistItem)
            .where(WishlistItem.user_id == user_id)
            .options(
                joinedload(WishlistItem.product)
            )
        )
        return list(self.db.execute(stmt).scalars().all())
    
    def toggle_item(self, user_id: str, product_id: str) -> WishlistItem:
        """
        Add item to user's wishlist.
        
        Args:
            user_id: User ID.
            product_id: Product ID.
            
        Returns:
            WishlistItem: Created wishlist item.
            
        Raises:
            ValueError: If product not found or already in wishlist.
        """
        # Check if product exists
        product = self.db.execute(
            select(Product).where(Product.id == product_id)
        ).scalars().first()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Check if item already in wishlist
        existing_item = self.find_item_by_product(user_id, product_id)
        if existing_item:
            #  delete the item
            self.db.delete(existing_item)
            self.db.commit()
            return
        
        # Create new wishlist item
        wishlist_item = WishlistItem(
            user_id=user_id,
            product_id=product_id
        )
        self.db.add(wishlist_item)
        self.db.commit()
        self.db.refresh(wishlist_item)
        return wishlist_item
    
    def remove_item(self, user_id: str, product_id: str) -> None:
        """
        Remove item from wishlist.
        
        Args:
            user_id: User ID.
            product_id: Product ID.
            
        Raises:
            ValueError: If item not found in wishlist.
        """
        # Find the item
        item = self.find_item_by_product(user_id, product_id)
        if not item:
            raise ValueError(f"Product not found in wishlist: {product_id}")
        
        # Remove the item
        self.db.delete(item)
        self.db.commit()
    
    def remove_item_by_id(self, item_id: str, user_id: str) -> None:
        """
        Remove wishlist item by ID.
        
        Args:
            item_id: Wishlist item ID.
            user_id: User ID (for verification).
            
        Raises:
            ValueError: If item not found or not in user's wishlist.
        """
        stmt = (
            select(WishlistItem)
            .where(WishlistItem.id == item_id)
        )
        item = self.db.execute(stmt).scalars().first()
        
        if not item:
            raise ValueError(f"Wishlist item not found: {item_id}")
        
        if item.user_id != user_id:
            raise ValueError("Item does not belong to this user")
        
        self.db.delete(item)
        self.db.commit()
    
    def find_item_by_product(self, user_id: str, product_id: str) -> Optional[WishlistItem]:
        """
        Find wishlist item by product ID for a specific user.
        
        Args:
            user_id: User ID.
            product_id: Product ID to search for.
            
        Returns:
            Optional[WishlistItem]: Wishlist item if found, None otherwise.
        """
        stmt = (
            select(WishlistItem)
            .where(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
        )
        return self.db.execute(stmt).scalars().first()
    
    def is_product_in_wishlist(self, user_id: str, product_id: str) -> bool:
        """
        Check if a product is in a user's wishlist.
        
        Args:
            user_id: User ID.
            product_id: Product ID to check.
            
        Returns:
            bool: True if product is in wishlist, False otherwise.
        """
        stmt = (
            select(func.count())
            .select_from(WishlistItem)
            .where(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
        )
        count = self.db.execute(stmt).scalar()
        return count > 0
    
    def clear_wishlist(self, user_id: str) -> None:
        """
        Remove all items from user's wishlist.
        
        Args:
            user_id: User ID.
        """
        stmt = select(WishlistItem).where(WishlistItem.user_id == user_id)
        items = self.db.execute(stmt).scalars().all()
        
        for item in items:
            self.db.delete(item)
        
        self.db.commit()
    
    def get_item_with_product(self, item_id: str) -> Optional[WishlistItem]:
        """
        Get wishlist item with product details.
        
        Args:
            item_id: Wishlist item ID.
            
        Returns:
            Optional[WishlistItem]: Wishlist item with loaded relationships.
        """
        stmt = (
            select(WishlistItem)
            .where(WishlistItem.id == item_id)
            .options(
                joinedload(WishlistItem.product)
            )
        )
        return self.db.execute(stmt).scalars().first()
