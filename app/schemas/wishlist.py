"""Wishlist schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field

from .common import BaseSchema, UUIDMixin, TimestampMixin
from .product import ProductList


class WishlistItemBase(BaseModel):
    """Base wishlist item schema."""
    
    product_id: str = Field(..., description="Product ID")


class AddToWishlistRequest(WishlistItemBase):
    """Add to wishlist request."""
    pass


class WishlistItemPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public wishlist item schema."""
    
    product_id: str = Field(..., description="Product ID")
    product: Optional[ProductList] = Field(None, description="Product details")


class WishlistResponse(BaseSchema):
    """Wishlist response schema."""
    
    items: List[WishlistItemPublic] = Field(default_factory=list, description="Wishlist items")
    total_items: int = Field(..., description="Total number of items")
