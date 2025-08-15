"""Cart repository for database operations."""

from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal

from app.models.cart import Cart
from app.models.product import Product


class CartRepository:
    """Repository for cart operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
    
    def get_items_by_user_id(self, user_id: str) -> List[Cart]:
        """
        Get all cart items for a user.
        
        Args:
            user_id: User ID to find cart items for.
            
        Returns:
            List[Cart]: List of cart items.
        """
        stmt = select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
            
        return list(self.db.execute(stmt).scalars().all())
    
    def add_item(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """
        Add item to user's cart or update quantity if already exists.
        
        Args:
            user_id: User ID.
            product_id: Product ID.
            quantity: Quantity to add.
            
        Returns:
            Cart: Created or updated cart item.
            
        Raises:
            ValueError: If product not found.
        """
        # Get product to check availability and get current price
        product = self.db.execute(
            select(Product).where(Product.id == product_id)
        ).scalars().first()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        if not product.is_available():
            raise ValueError(f"Product not available: {product_id}")
        
        if not product.can_fulfill_quantity(quantity):
            raise ValueError(f"Not enough stock for product: {product_id}")
        
        # Check if item already in user's cart
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id, Cart.product_id == product_id)
        )
        existing_item = self.db.execute(stmt).scalars().first()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            existing_item.update_quantity(new_quantity)
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new item
            cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            return cart_item
    
    def update_cart_item_quantity(self, cart_id: str) -> Optional[Cart]:
        """
        Update cart item quantity.
        
        Args:
            cart_id: Cart ID.
            quantity: New quantity.
            
        Returns:
            Optional[Cart]: Updated cart item or None if removed.
            
        Raises:
            ValueError: If item not found or quantity exceeds stock.
        """
        stmt = (
            select(Cart)
            .where(Cart.id == cart_id)
            .options(joinedload(Cart.product))
        )
        cart_item = self.db.execute(stmt).scalars().first()
        
        if not cart_item:
            raise ValueError(f"Cart item not found: {cart_id}")
        

        
        # Check if product has enough stock
        if not cart_item.product.can_fulfill_quantity(1):
            raise ValueError(f"Not enough stock for product: {cart_item.product_id}")
        
        cart_item.quantity += 1
        # Update quantity
        cart_item.update_quantity(cart_item.quantity)
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item
    
    def remove_item(self, cart_id: str) -> None:
        """
        Remove item from cart (decrease quantity by 1).
        
        Args:
            cart_id: Cart ID.
            
        Raises:
            ValueError: If item not found.
        """
        stmt = select(Cart).where(Cart.id == cart_id)
        cart_item = self.db.execute(stmt).scalars().first()
        if not cart_item:
            raise ValueError(f"Cart item not found: {cart_id}")
        
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            self.db.delete(cart_item)
            self.db.commit()
            return
        
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item
    
    def clear_product_from_cart(self, cart_id: str) -> None:
        """
        Completely remove a product from cart regardless of quantity.
        
        Args:
            cart_id: Cart ID.
            
        Raises:
            ValueError: If item not found.
        """
        stmt = select(Cart).where(Cart.id == cart_id)
        cart_item = self.db.execute(stmt).scalars().first()
        if not cart_item:
            raise ValueError(f"Cart item not found: {cart_id}")
        
        # Completely remove the item regardless of quantity
        self.db.delete(cart_item)
        self.db.commit()
    
    def clear_cart(self, user_id: str) -> None:
        """
        Remove all items from user's cart.
        
        Args:
            user_id: User ID.
        """
        stmt = select(Cart).where(Cart.user_id == user_id)
        items = self.db.execute(stmt).scalars().all()
        
        for item in items:
            self.db.delete(item)
        
        self.db.commit()
    
    def get_item_with_product(self, product_id: str, user_id: str) -> Optional[Cart]:
        """
        Get cart item with product details.
        
        Args:
            product_id: Product ID.
            user_id: User ID.
        Returns:
            Optional[Cart]: Cart item with loaded relationships.
        """
        stmt = (
            select(Cart)
            .where(Cart.product_id == product_id, Cart.user_id == user_id)
            .options(
                joinedload(Cart.product)
            )
        )
        return self.db.execute(stmt).scalars().first()
    
    def find_item_by_product(self, user_id: str, product_id: str) -> Optional[Cart]:
        """
        Find cart item by product ID for a specific user.
        
        Args:
            user_id: User ID.
            product_id: Product ID to search for.
            
        Returns:
            Optional[Cart]: Cart item if found, None otherwise.
        """
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id, Cart.product_id == product_id)
        )
        return self.db.execute(stmt).scalars().first()
    
    def calculate_cart_total(self, user_id: str) -> Decimal:
        """
        Calculate total cart value for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            Decimal: Total cart value.
        """
        items = self.get_items_by_user_id(user_id)
        return sum(item.subtotal for item in items)
    
    def get_total_items(self, user_id: str) -> int:
        """
        Get total number of items in a user's cart.
        
        Args:
            user_id: User ID.
            
        Returns:
            int: Total quantity of all items.
        """
        items = self.get_items_by_user_id(user_id)
        return sum(item.quantity for item in items)
    
    def is_cart_empty(self, user_id: str) -> bool:
        """
        Check if user's cart is empty.
        
        Args:
            user_id: User ID.
            
        Returns:
            bool: True if cart is empty, False otherwise.
        """
        stmt = (
            select(func.count())
            .select_from(Cart)
            .where(Cart.user_id == user_id)
        )
        count = self.db.execute(stmt).scalar()
        return count == 0