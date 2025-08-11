"""Payment model."""

from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, ForeignKey, Index, JSON
from sqlalchemy.dialects.mysql import DECIMAL, CHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class PaymentProvider(str, Enum):
    """Payment provider enumeration."""
    
    STRIPE = "stripe"
    RAZORPAY = "razorpay"
    MOCK = "mock"  # For testing


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Payment(BaseModel):
    """
    Payment model for tracking payment transactions.
    
    Attributes:
        id: Unique identifier (UUID).
        order_id: Foreign key to Order model.
        provider: Payment provider (stripe, razorpay, mock).
        provider_payment_id: Payment ID from the provider.
        status: Payment status.
        amount: Payment amount.
        currency: Currency code.
        raw_payload: Raw response from payment provider.
        created_at: Payment creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "payments"
    
    order_id = Column(CHAR(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_payment_id = Column(String(255), nullable=True)  # Set when payment is created with provider
    status = Column(String(50), default=PaymentStatus.PENDING.value, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    raw_payload = Column(JSON, nullable=True)  # Store raw provider response
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index("idx_payment_order", order_id),
        Index("idx_payment_provider_id", provider, provider_payment_id),
        Index("idx_payment_status", status),
    )
    
    def __repr__(self) -> str:
        """String representation of the payment."""
        return f"<Payment(id={self.id}, order_id={self.order_id}, provider={self.provider}, status={self.status})>"
    
    def update_status(self, new_status: PaymentStatus, provider_payment_id: Optional[str] = None) -> None:
        """
        Update payment status.
        
        Args:
            new_status: New payment status.
            provider_payment_id: Provider payment ID (if available).
        """
        self.status = new_status.value
        if provider_payment_id:
            self.provider_payment_id = provider_payment_id
    
    def update_provider_data(self, provider_payment_id: str, raw_payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Update provider-specific data.
        
        Args:
            provider_payment_id: Payment ID from provider.
            raw_payload: Raw response from provider.
        """
        self.provider_payment_id = provider_payment_id
        if raw_payload:
            self.raw_payload = raw_payload
    
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == PaymentStatus.PENDING.value
    
    def is_succeeded(self) -> bool:
        """Check if payment succeeded."""
        return self.status == PaymentStatus.SUCCEEDED.value
    
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED.value
    
    @property
    def amount_decimal(self) -> Decimal:
        """Get amount as Decimal for precise calculations."""
        return Decimal(str(self.amount))