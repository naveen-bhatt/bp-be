"""Order schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .common import BaseSchema, UUIDMixin, TimestampMixin
from .product import ProductList
from ..models.order import OrderStatus


class OrderCreateRequest(BaseModel):
    """Order creation request."""
    
    cart_id: str = Field(..., description="Cart ID to create order from")
    address_id: str = Field(..., description="Address ID to use for shipping")


class OrderItemSummary(BaseModel):
    """Order item summary schema."""
    
    id: str = Field(..., description="Order item ID")
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., description="Item quantity")
    unit_price: str = Field(..., description="Price per unit as decimal string")
    subtotal: str = Field(..., description="Item subtotal as decimal string")
    product: Optional[ProductList] = Field(None, description="Product details")
    created_at: datetime = Field(..., description="Item creation timestamp")
    updated_at: datetime = Field(..., description="Item last update timestamp")


class OrderSummary(BaseModel):
    """Order schema for both list and detail views."""
    
    id: str = Field(..., description="Order ID")
    user_id: Optional[str] = Field(None, description="User ID (null for guest orders)")
    address_id: str = Field(..., description="Address ID used for shipping")
    cart_id: str = Field(..., description="Cart ID used for order creation")
    shipping_id: Optional[str] = Field(None, description="Shipping/tracking ID")
    admin_notes: Optional[str] = Field(None, description="Admin notes about the order")
    spam_order: bool = Field(False, description="Flag to mark suspicious orders")
    total_amount: str = Field(..., description="Total order amount as decimal string")
    currency: str = Field(..., description="Order currency")
    status: str = Field(..., description="Order status")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime = Field(..., description="Order last update timestamp")
    item_count: int = Field(..., description="Number of items in order")
    items: Optional[List[OrderItemSummary]] = Field(None, description="Order items (only populated in detail view)")


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


class OrderListResponse(BaseModel):
    """Response schema for list of orders."""
    
    items: List[OrderSummary] = Field(default_factory=list, description="List of orders")
    count: int = Field(..., description="Total number of orders")