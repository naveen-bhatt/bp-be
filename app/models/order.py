"""Order and order item models."""

from decimal import Decimal
from enum import Enum
from typing import List
from sqlalchemy import Column, String, Integer, ForeignKey, Index, Boolean

from sqlalchemy.orm import relationship

from .base import BaseModel


class OrderStatus(str, Enum):
    """Order status enumeration."""
    
    INITIATED = "initiated"
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILURE = "failure"


class Order(BaseModel):
    """
    Order model for completed purchases.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model (nullable for guest orders).
        address_id: Foreign key to Address model for shipping.
        cart_id: ID of the cart used to create this order.
        total_amount: Total order amount.
        currency: Currency code.
        status: Order status.
        items: List of order items.
        payments: List of payment attempts.
        created_at: Order creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "orders"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    address_id = Column(String(36), ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    cart_id = Column(String(36), nullable=True)
    shipping_id = Column(String(255), nullable=True)
    admin_notes = Column(String(1000), nullable=True)
    spam_order = Column(Boolean, default=False, nullable=False)
    total_amount = Column(String(20), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(50), default=OrderStatus.INITIATED.value, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    address = relationship("Address", foreign_keys=[address_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_order_user_status", user_id, status),
        Index("idx_order_status_created", status, "created_at"),
        Index("idx_order_address", address_id),
        Index("idx_order_cart", cart_id),
        Index("idx_order_shipping_id", shipping_id),
        Index("idx_order_spam_order", spam_order),
    )
    
    def __repr__(self) -> str:
        """String representation of the order."""
        return f"<Order(id={self.id}, user_id={self.user_id}, address_id={self.address_id}, cart_id={self.cart_id}, shipping_id={self.shipping_id}, total={self.total_amount}, status={self.status}, spam_order={self.spam_order})>"
    
    def update_status(self, new_status: OrderStatus) -> None:
        """
        Update order status.
        
        Args:
            new_status: New order status.
        """
        self.status = new_status.value
    
    def is_successful(self) -> bool:
        """Check if order is successful."""
        return self.status == OrderStatus.SUCCESSFUL.value
    
    def is_pending(self) -> bool:
        """Check if order is pending."""
        return self.status == OrderStatus.PENDING.value
    
    def is_failure(self) -> bool:
        """Check if order failed."""
        return self.status == OrderStatus.FAILURE.value
    
    def can_be_paid(self) -> bool:
        """Check if order can be paid."""
        return self.status in [OrderStatus.INITIATED.value, OrderStatus.PENDING.value]
    
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
    
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(String(20), nullable=False)
    
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