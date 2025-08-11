"""Cart and cart item models."""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.mysql import DECIMAL, CHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class Cart(BaseModel):
    """
    Shopping cart model.
    
    Supports both authenticated users and guest carts using cart tokens.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model (nullable for guest carts).
        cart_token: Token for guest cart identification (nullable for user carts).
        items: List of cart items.
        created_at: Cart creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "carts"
    
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    cart_token = Column(String(255), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_cart_user", user_id),
        Index("idx_cart_token", cart_token),
    )
    
    def __repr__(self) -> str:
        """String representation of the cart."""
        identifier = f"user_id={self.user_id}" if self.user_id else f"token={self.cart_token}"
        return f"<Cart(id={self.id}, {identifier}, items={len(self.items)})>"
    
    def calculate_total(self) -> Decimal:
        """
        Calculate total cart value.
        
        Returns:
            Decimal: Total cart value.
        """
        return sum(item.subtotal for item in self.items)
    
    def get_total_items(self) -> int:
        """
        Get total number of items in cart.
        
        Returns:
            int: Total quantity of all items.
        """
        return sum(item.quantity for item in self.items)
    
    def find_item_by_product(self, product_id: str) -> Optional["CartItem"]:
        """
        Find cart item by product ID.
        
        Args:
            product_id: Product ID to search for.
            
        Returns:
            Optional[CartItem]: Cart item if found, None otherwise.
        """
        for item in self.items:
            if item.product_id == product_id:
                return item
        return None
    
    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return len(self.items) == 0


class CartItem(BaseModel):
    """
    Cart item model representing a product in a cart.
    
    Attributes:
        id: Unique identifier (UUID).
        cart_id: Foreign key to Cart model.
        product_id: Foreign key to Product model.
        quantity: Quantity of the product.
        unit_price: Price per unit at the time of adding to cart.
        created_at: Item creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "cart_items"
    
    cart_id = Column(CHAR(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(CHAR(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_cart_item_cart_product", cart_id, product_id, unique=True),
        Index("idx_cart_item_product", product_id),
    )
    
    def __repr__(self) -> str:
        """String representation of the cart item."""
        return f"<CartItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"
    
    @property
    def subtotal(self) -> Decimal:
        """
        Calculate subtotal for this cart item.
        
        Returns:
            Decimal: Subtotal (quantity * unit_price).
        """
        return Decimal(str(self.unit_price)) * self.quantity
    
    def update_quantity(self, new_quantity: int) -> None:
        """
        Update item quantity.
        
        Args:
            new_quantity: New quantity value.
        """
        self.quantity = new_quantity
    
    def update_price(self, new_price: Decimal) -> None:
        """
        Update unit price (e.g., when product price changes).
        
        Args:
            new_price: New unit price.
        """
        self.unit_price = new_price