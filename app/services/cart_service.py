"""Cart service with business logic."""

from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartPublic, CartItemPublic, CartSummary
from app.models.cart import Cart, CartState


class CartService:
    """Service for cart operations."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)
    
    def get_cart(self, user_id: str) -> CartPublic:
        """
        Get user's active cart.
        
        Args:
            user_id: User ID (anonymous or registered).
            
        Returns:
            CartPublic: Cart with active items only.
        """
        # Get all cart items for the user
        items = self.cart_repo.get_items_by_user_id(user_id)
        
        # Only return active cart items
        active_items = [item for item in items if item.cart_state == CartState.ACTIVE]
        
        # Convert to schema
        return self._items_to_cart_schema(user_id, active_items)
    
    def get_cart_summary(self, user_id: str) -> CartSummary:
        """
        Get cart summary (totals only).
        
        Args:
            user_id: User ID (anonymous or registered).
            
        Returns:
            CartSummary: Cart totals.
        """
        total_amount = self.cart_repo.calculate_cart_total(user_id)
        total_items = self.cart_repo.get_total_items(user_id)
        
        return CartSummary(
            total_items=total_items,
            total_amount=str(total_amount),
            currency="INR"  # TODO: Make currency configurable
        )
    
    def add_to_cart(self, product_id: str, quantity: int, user_id: str) -> CartPublic:
        """
        Add item to cart.
        
        Args:
            product_id: Product ID to add.
            quantity: Quantity to add.
            user_id: User ID (anonymous or registered).
            
        Returns:
            CartPublic: Updated cart.
            
        Raises:
            ValueError: If product not found or not available.
        """
        # Add item to cart
        self.cart_repo.add_item(user_id, product_id, quantity)
        
        # Get all cart items for the user
        items = self.cart_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_cart_schema(user_id, items)
    
    def update_cart_item(self, product_id: str, user_id: str) -> CartPublic:
        """
        Update cart item quantity.
        
        Args:
            product_id: Product ID.
            quantity: New quantity.
            user_id: User ID (anonymous or registered).
            
        Returns:
            CartPublic: Updated cart.
            
        Raises:
            ValueError: If item not found or not in user's cart.
        """
        # Get the cart item first to verify it belongs to this user
        cart_item = self.cart_repo.get_item_with_product(product_id=product_id, user_id=user_id)
        if not cart_item or cart_item.user_id != user_id:
            raise ValueError(f"Item {product_id} not found in your cart")
        
        # Update quantity
        self.cart_repo.update_cart_item_quantity(cart_id=cart_item.id)
        
        # Get all cart items for the user
        items = self.cart_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_cart_schema(user_id, items)
    
    def remove_cart_item(self, product_id: str, user_id: str) -> CartPublic:
        """
        Remove item from cart (decrease quantity by 1).
        
        Args:
            product_id: Product ID.
            user_id: User ID (anonymous or registered).
            
        Returns:
            CartPublic: Updated cart.
            
        Raises:
            ValueError: If item not found or not in user's cart.
        """
        # Get the cart item first to verify it belongs to this user
        cart_item = self.cart_repo.get_item_with_product(product_id=product_id, user_id=user_id)
        if not cart_item or cart_item.user_id != user_id:
            raise ValueError(f"Item {product_id} not found in your cart")
        
        # Remove item (decrease quantity by 1)
        self.cart_repo.remove_item(cart_id=cart_item.id)
        
        # Get all cart items for the user
        items = self.cart_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_cart_schema(user_id, items)
    
    def clear_product_from_cart(self, product_id: str, user_id: str) -> CartPublic:
        """
        Completely remove a product from cart regardless of quantity.
        
        Args:
            product_id: Product ID to remove completely.
            user_id: User ID (anonymous or registered).
            
        Returns:
            CartPublic: Updated cart.
            
        Raises:
            ValueError: If item not found or not in user's cart.
        """
        # Get the cart item first to verify it belongs to this user
        cart_item = self.cart_repo.get_item_with_product(product_id=product_id, user_id=user_id)
        if not cart_item or cart_item.user_id != user_id:
            raise ValueError(f"Item {product_id} not found in your cart")
        
        # Completely remove the item from cart
        self.cart_repo.clear_product_from_cart(cart_id=cart_item.id)
        
        # Get all cart items for the user
        items = self.cart_repo.get_items_by_user_id(user_id)
        
        # Convert to schema
        return self._items_to_cart_schema(user_id, items)
    
    def clear_cart(self, user_id: str) -> None:
        """
        Clear all items from cart.
        
        Args:
            user_id: User ID (anonymous or registered).
        """
        self.cart_repo.clear_cart(user_id)
    
    def _items_to_cart_schema(self, user_id: str, items: List[Cart]) -> CartPublic:
        """
        Convert list of Cart models to CartPublic schema.
        
        Args:
            user_id: User ID.
            items: List of cart items.
            
        Returns:
            CartPublic: Cart schema.
        """

        total_amount = sum(item.subtotal for item in items) if items else Decimal('0')
            
        total_items = sum(item.quantity for item in items) if items else 0
        
        # Convert cart items
        item_schemas = []
        for item in items:
            # If we need product details and they're not loaded, fetch them
            product_data = None

            if hasattr(item, 'product') and item.product:
                product_data = self.product_repo.to_list_schema(item.product)
                
            # If product data is still None, fetch the product directly
            if product_data is None and item.product_id:
                product = self.product_repo.get_by_id(item.product_id)
                if product:
                    product_data = self.product_repo.to_list_schema(product)

            item_schemas.append(CartItemPublic(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                created_at=item.created_at,
                product=product_data
            ))
        
        # Create cart schema
        return CartPublic(
            user_id=user_id,
            items=item_schemas,
            total_amount=str(total_amount),
            total_items=total_items,
        )