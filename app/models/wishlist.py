"""Wishlist model."""

from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class WishlistItem(BaseModel):
    """
    Wishlist item model representing a product in a user's wishlist.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model.
        product_id: Foreign key to Product model.
        created_at: Item creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "wishlist_items"
    
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(CHAR(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_wishlist_user_product", user_id, product_id, unique=True),
        Index("idx_wishlist_user", user_id),
        Index("idx_wishlist_product", product_id),
    )
    
    def __repr__(self) -> str:
        """String representation of the wishlist item."""
        return f"<WishlistItem(id={self.id}, user_id={self.user_id}, product_id={self.product_id})>"
