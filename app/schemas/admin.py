"""Admin schemas for admin interface."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .order import OrderSummary
from .user import UserPublic


class OrderFilter(BaseModel):
    """Order filtering parameters for admin."""
    
    status: Optional[str] = Field(None, description="Filter by order status")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    date_from: Optional[datetime] = Field(None, description="Filter orders from date")
    date_to: Optional[datetime] = Field(None, description="Filter orders to date")
    min_amount: Optional[str] = Field(None, description="Minimum order amount")
    max_amount: Optional[str] = Field(None, description="Maximum order amount")
    address_id: Optional[str] = Field(None, description="Filter by address ID")
    shipping_id: Optional[str] = Field(None, description="Filter by shipping/tracking ID")
    spam_order: Optional[bool] = Field(None, description="Filter by spam order flag")
    has_admin_notes: Optional[bool] = Field(None, description="Filter orders with/without admin notes")


class PaginationFilter(BaseModel):
    """Pagination parameters for admin endpoints."""
    
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")


class ShippedOrdersFilter(BaseModel):
    """Filter parameters for shipped orders."""
    
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of orders to return")
    offset: int = Field(0, ge=0, description="Number of orders to skip")


class BulkShipRequest(BaseModel):
    """Request schema for bulk shipping orders."""
    
    order_ids: List[str] = Field(..., description="List of order IDs to ship")
    tracking_numbers: Optional[List[str]] = Field(None, description="Optional tracking numbers")
    notes: Optional[str] = Field(None, description="Shipping notes")


class BulkShipResponse(BaseModel):
    """Response schema for bulk shipping operation."""
    
    success_count: int = Field(..., description="Number of orders successfully shipped")
    failed_count: int = Field(..., description="Number of orders that failed to ship")
    failed_orders: List[str] = Field(default_factory=list, description="List of order IDs that failed")
    message: str = Field(..., description="Summary message")


class OrderCancelRequest(BaseModel):
    """Request schema for cancelling an order."""
    
    reason: str = Field(..., description="Reason for cancellation")
    notes: Optional[str] = Field(None, description="Additional notes")


class OrderCancelResponse(BaseModel):
    """Response schema for order cancellation."""
    
    order_id: str = Field(..., description="Cancelled order ID")
    status: str = Field(..., description="New order status")
    message: str = Field(..., description="Cancellation message")


class AdminOrderListResponse(BaseModel):
    """Response schema for admin order list."""
    
    items: List[OrderSummary] = Field(default_factory=list, description="List of orders")
    count: int = Field(..., description="Total number of orders")
    filters_applied: OrderFilter = Field(..., description="Filters that were applied")


class ShippedOrderAddress(BaseModel):
    """Schema for shipped order address information."""
    
    order_id: str = Field(..., description="Order ID")
    user_name: str = Field(..., description="User's full name")
    address_line1: str = Field(..., description="Primary address line")
    address_line2: Optional[str] = Field(None, description="Secondary address line")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/Province")
    pincode: str = Field(..., description="Postal/ZIP code")
    country: str = Field(..., description="Country")
    phone: str = Field(..., description="Contact phone")
    order_date: datetime = Field(..., description="Order creation date")
    shipping_date: datetime = Field(..., description="Order shipping date")


class ShippedOrdersAddressList(BaseModel):
    """Response schema for shipped orders address list."""
    
    addresses: List[ShippedOrderAddress] = Field(default_factory=list, description="List of addresses")
    count: int = Field(..., description="Total number of addresses")
    generated_at: datetime = Field(..., description="Timestamp when list was generated")


class AdminStats(BaseModel):
    """Admin dashboard statistics."""
    
    total_orders: int = Field(..., description="Total number of orders")
    pending_orders: int = Field(..., description="Number of pending orders")
    shipped_orders: int = Field(..., description="Number of shipped orders")
    cancelled_orders: int = Field(..., description="Number of cancelled orders")
    total_revenue: str = Field(..., description="Total revenue")
    today_orders: int = Field(..., description="Orders created today")
    today_revenue: str = Field(..., description="Revenue from today's orders")
