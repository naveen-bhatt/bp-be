"""Cart model."""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class Cart(BaseModel):
    """
    Cart model representing a product in a user's cart.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model.
        product_id: Foreign key to Product model.
        quantity: Quantity of the product.
        created_at: Item creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "carts"
    
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(CHAR(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_cart_user_product", user_id, product_id, unique=True),
        Index("idx_cart_user", user_id),
        Index("idx_cart_product", product_id),
    )
    
    def __repr__(self) -> str:
        """String representation of the cart."""
        return f"<Cart(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, qty={self.quantity})>"
    
    @property
    def subtotal(self) -> Decimal:
        """
        Calculate subtotal for this cart item.
        
        Returns:
            Decimal: Subtotal (quantity * product.price).
        """
        return self.product.price * self.quantity
    
    def update_quantity(self, new_quantity: int) -> None:
        """
        Update item quantity.
        
        Args:
            new_quantity: New quantity value.
        """
        self.quantity = new_quantity