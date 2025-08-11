"""Order and order item models."""

from decimal import Decimal
from enum import Enum
from typing import List
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.mysql import DECIMAL, CHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class OrderStatus(str, Enum):
    """Order status enumeration."""
    
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    """
    Order model for completed purchases.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model (nullable for guest orders).
        total_amount: Total order amount.
        currency: Currency code.
        status: Order status.
        items: List of order items.
        payments: List of payment attempts.
        created_at: Order creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "orders"
    
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(50), default=OrderStatus.CREATED.value, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_order_user_status", user_id, status),
        Index("idx_order_status_created", status, "created_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of the order."""
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total_amount}, status={self.status})>"
    
    def update_status(self, new_status: OrderStatus) -> None:
        """
        Update order status.
        
        Args:
            new_status: New order status.
        """
        self.status = new_status.value
    
    def is_paid(self) -> bool:
        """Check if order is paid."""
        return self.status == OrderStatus.PAID.value
    
    def is_failed(self) -> bool:
        """Check if order failed."""
        return self.status == OrderStatus.FAILED.value
    
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED.value
    
    def can_be_paid(self) -> bool:
        """Check if order can be paid."""
        return self.status == OrderStatus.CREATED.value
    
    def calculate_total(self) -> Decimal:
        """
        Calculate total from order items.
        
        Returns:
            Decimal: Total order value.
        """
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_amount_decimal(self) -> Decimal:
        """Get total amount as Decimal for precise calculations."""
        return Decimal(str(self.total_amount))


class OrderItem(BaseModel):
    """
    Order item model representing a product in an order.
    
    Attributes:
        id: Unique identifier (UUID).
        order_id: Foreign key to Order model.
        product_id: Foreign key to Product model.
        quantity: Quantity of the product.
        unit_price: Price per unit at the time of order.
        created_at: Item creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "order_items"
    
    order_id = Column(CHAR(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(CHAR(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    # Indexes
    __table_args__ = (
        Index("idx_order_item_order", order_id),
        Index("idx_order_item_product", product_id),
    )
    
    def __repr__(self) -> str:
        """String representation of the order item."""
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"
    
    @property
    def subtotal(self) -> Decimal:
        """
        Calculate subtotal for this order item.
        
        Returns:
            Decimal: Subtotal (quantity * unit_price).
        """
        return Decimal(str(self.unit_price)) * self.quantity