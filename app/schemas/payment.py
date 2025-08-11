"""Payment schemas."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from .common import BaseSchema, UUIDMixin, TimestampMixin


class PaymentIntentRequest(BaseModel):
    """Payment intent creation request."""
    
    order_id: str = Field(..., description="Order ID to create payment for")
    provider: str = Field(..., description="Payment provider (stripe, razorpay, mock)")
    return_url: Optional[str] = Field(None, description="Return URL after payment")
    cancel_url: Optional[str] = Field(None, description="Cancel URL if payment cancelled")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate payment provider."""
        allowed_providers = ['stripe', 'razorpay', 'mock']
        if v.lower() not in allowed_providers:
            raise ValueError(f'Provider must be one of: {", ".join(allowed_providers)}')
        return v.lower()


class PaymentIntentResponse(BaseModel):
    """Payment intent response."""
    
    payment_id: str = Field(..., description="Payment ID")
    client_secret: Optional[str] = Field(None, description="Client secret for frontend")
    payment_url: Optional[str] = Field(None, description="Payment URL for redirect")
    provider_data: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific data")


class PaymentConfirmRequest(BaseModel):
    """Payment confirmation request."""
    
    payment_id: str = Field(..., description="Payment ID")
    provider_payment_id: Optional[str] = Field(None, description="Provider payment ID")
    payment_method: Optional[str] = Field(None, description="Payment method used")


class PaymentPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public payment schema."""
    
    order_id: str = Field(..., description="Order ID")
    provider: str = Field(..., description="Payment provider")
    provider_payment_id: Optional[str] = Field(None, description="Provider payment ID")
    status: str = Field(..., description="Payment status")
    amount: str = Field(..., description="Payment amount as decimal string")
    currency: str = Field(..., description="Payment currency")


class PaymentWebhookRequest(BaseModel):
    """Payment webhook request (base)."""
    
    provider: str = Field(..., description="Payment provider")
    event_type: str = Field(..., description="Webhook event type")
    data: Dict[str, Any] = Field(..., description="Webhook payload data")


class StripeWebhookRequest(PaymentWebhookRequest):
    """Stripe webhook request."""
    
    stripe_signature: str = Field(..., description="Stripe signature header")


class RazorpayWebhookRequest(PaymentWebhookRequest):
    """Razorpay webhook request."""
    
    razorpay_signature: str = Field(..., description="Razorpay signature header")


class PaymentStatus(BaseModel):
    """Payment status response."""
    
    payment_id: str = Field(..., description="Payment ID")
    status: str = Field(..., description="Payment status")
    amount: str = Field(..., description="Payment amount as decimal string")
    currency: str = Field(..., description="Payment currency")
    provider: str = Field(..., description="Payment provider")
    provider_payment_id: Optional[str] = Field(None, description="Provider payment ID")
    created_at: str = Field(..., description="Payment creation timestamp")
    updated_at: str = Field(..., description="Payment last update timestamp")


class PaymentRefundRequest(BaseModel):
    """Payment refund request."""
    
    payment_id: str = Field(..., description="Payment ID to refund")
    amount: Optional[str] = Field(None, description="Refund amount (full refund if not specified)")
    reason: Optional[str] = Field(None, max_length=500, description="Refund reason")


class PaymentRefundResponse(BaseModel):
    """Payment refund response."""
    
    refund_id: str = Field(..., description="Refund ID")
    payment_id: str = Field(..., description="Original payment ID")
    amount: str = Field(..., description="Refunded amount as decimal string")
    currency: str = Field(..., description="Refund currency")
    status: str = Field(..., description="Refund status")
    provider_refund_id: Optional[str] = Field(None, description="Provider refund ID")