"""Order schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .common import BaseSchema, UUIDMixin, TimestampMixin
from .product import ProductList


class OrderItemPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public order item schema."""
    
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., description="Item quantity")
    unit_price: str = Field(..., description="Price per unit as decimal string")
    subtotal: str = Field(..., description="Item subtotal as decimal string")
    product: Optional[ProductList] = Field(None, description="Product details")


class OrderCreateRequest(BaseModel):
    """Order creation request."""
    
    shipping_address: Optional[dict] = Field(None, description="Shipping address")
    billing_address: Optional[dict] = Field(None, description="Billing address")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")


class OrderPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public order schema."""
    
    user_id: Optional[str] = Field(None, description="User ID (null for guest orders)")
    total_amount: str = Field(..., description="Total order amount as decimal string")
    currency: str = Field(..., description="Order currency")
    status: str = Field(..., description="Order status")
    items: List[OrderItemPublic] = Field(default_factory=list, description="Order items")


class OrderSummary(BaseModel):
    """Order summary schema."""
    
    id: str = Field(..., description="Order ID")
    total_amount: str = Field(..., description="Total order amount as decimal string")
    currency: str = Field(..., description="Order currency")
    status: str = Field(..., description="Order status")
    created_at: datetime = Field(..., description="Order creation timestamp")
    item_count: int = Field(..., description="Number of items in order")


class OrderStatusUpdate(BaseModel):
    """Order status update schema."""
    
    status: str = Field(..., description="New order status")
    notes: Optional[str] = Field(None, max_length=500, description="Update notes")


class OrderFilter(BaseModel):
    """Order filtering parameters."""
    
    status: Optional[str] = Field(None, description="Filter by order status")
    date_from: Optional[datetime] = Field(None, description="Filter orders from date")
    date_to: Optional[datetime] = Field(None, description="Filter orders to date")
    min_amount: Optional[str] = Field(None, description="Minimum order amount")
    max_amount: Optional[str] = Field(None, description="Maximum order amount")