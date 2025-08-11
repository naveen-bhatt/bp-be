"""Cart schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from .common import BaseSchema, UUIDMixin, TimestampMixin
from .product import ProductList


class AddToCartRequest(BaseModel):
    """Add item to cart request."""
    
    product_id: str = Field(..., description="Product ID to add")
    quantity: int = Field(..., gt=0, le=1000, description="Quantity to add")


class UpdateCartItemRequest(BaseModel):
    """Update cart item request."""
    
    quantity: int = Field(..., ge=0, le=1000, description="New quantity (0 to remove)")


class CartItemPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public cart item schema."""
    
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., description="Item quantity")
    unit_price: str = Field(..., description="Price per unit as decimal string")
    subtotal: str = Field(..., description="Item subtotal as decimal string")
    product: Optional[ProductList] = Field(None, description="Product details")


class CartPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public cart schema."""
    
    user_id: Optional[str] = Field(None, description="User ID (null for guest carts)")
    items: List[CartItemPublic] = Field(default_factory=list, description="Cart items")
    total_amount: str = Field(..., description="Total cart amount as decimal string")
    total_items: int = Field(..., description="Total number of items")
    currency: str = Field(..., description="Cart currency")


class CartSummary(BaseModel):
    """Cart summary schema."""
    
    total_items: int = Field(..., description="Total number of items")
    total_amount: str = Field(..., description="Total cart amount as decimal string")
    currency: str = Field(..., description="Cart currency")


class CartMergeRequest(BaseModel):
    """Cart merge request for login scenarios."""
    
    guest_cart_token: str = Field(..., description="Guest cart token to merge")


class CartClearRequest(BaseModel):
    """Cart clear request."""
    
    confirm: bool = Field(..., description="Confirmation flag")
    
    @field_validator('confirm')
    @classmethod
    def validate_confirm(cls, v: bool) -> bool:
        """Validate confirmation."""
        if not v:
            raise ValueError('Confirmation required to clear cart')
        return v