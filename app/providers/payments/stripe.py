"""Stripe payment provider implementation."""

import hmac
import hashlib
from typing import Dict, Any, Optional
from decimal import Decimal

from .base import PaymentProvider, PaymentIntent, PaymentResult, RefundResult
from app.core.logging import get_logger

logger = get_logger(__name__)

# Try to import Stripe SDK
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe SDK not available. Install with: pip install stripe")


class StripePaymentProvider(PaymentProvider):
    """
    Stripe payment provider implementation.
    
    TODO: To use Stripe integration:
    1. Install Stripe SDK: pip install stripe
    2. Obtain Stripe API keys from Stripe Dashboard
    3. Set up webhook endpoints in Stripe Dashboard
    4. Configure webhook secrets for signature verification
    
    Note: This implementation provides a working stub if Stripe SDK is not installed.
    """
    
    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        """Initialize Stripe payment provider."""
        super().__init__(api_key, webhook_secret)
        
        if STRIPE_AVAILABLE:
            stripe.api_key = api_key
        else:
            logger.warning("Stripe SDK not available - using stub implementation")
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "stripe"
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        order_id: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """
        Create a Stripe payment intent.
        
        Args:
            amount: Payment amount.
            currency: Currency code.
            order_id: Internal order ID.
            customer_email: Customer email address.
            metadata: Additional metadata.
            
        Returns:
            PaymentIntent: Payment intent with client secret.
            
        Raises:
            ValueError: If payment intent creation fails.
        """
        if not STRIPE_AVAILABLE:
            # Stub implementation for testing
            logger.info(f"Creating mock Stripe payment intent for order {order_id}")
            return PaymentIntent(
                provider_payment_id=f"pi_mock_{order_id}",
                client_secret=f"pi_mock_{order_id}_secret_test",
                status="requires_payment_method",
                metadata=metadata or {}
            )
        
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)
            
            intent_data = {
                "amount": amount_cents,
                "currency": currency.lower(),
                "metadata": {
                    "order_id": order_id,
                    **(metadata or {})
                },
                "automatic_payment_methods": {"enabled": True}
            }
            
            if customer_email:
                intent_data["receipt_email"] = customer_email
            
            intent = stripe.PaymentIntent.create(**intent_data)
            
            return PaymentIntent(
                provider_payment_id=intent.id,
                client_secret=intent.client_secret,
                status=intent.status,
                metadata=intent.metadata
            )
            
        except Exception as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            raise ValueError(f"Failed to create payment intent: {e}")
    
    async def confirm_payment(
        self,
        provider_payment_id: str,
        payment_method: Optional[str] = None
    ) -> PaymentResult:
        """
        Confirm a Stripe payment.
        
        Args:
            provider_payment_id: Stripe payment intent ID.
            payment_method: Payment method ID.
            
        Returns:
            PaymentResult: Payment confirmation result.
            
        Raises:
            ValueError: If payment confirmation fails.
        """
        if not STRIPE_AVAILABLE:
            # Stub implementation
            logger.info(f"Mock confirming Stripe payment {provider_payment_id}")
            return PaymentResult(
                provider_payment_id=provider_payment_id,
                status="succeeded",
                amount=Decimal("100.00"),  # Mock amount
                currency="USD",
                metadata={}
            )
        
        try:
            confirm_data = {}
            if payment_method:
                confirm_data["payment_method"] = payment_method
            
            intent = stripe.PaymentIntent.confirm(
                provider_payment_id,
                **confirm_data
            )
            
            return PaymentResult(
                provider_payment_id=intent.id,
                status=intent.status,
                amount=Decimal(intent.amount) / 100,  # Convert from cents
                currency=intent.currency.upper(),
                metadata=intent.metadata
            )
            
        except Exception as e:
            logger.error(f"Stripe payment confirmation failed: {e}")
            raise ValueError(f"Failed to confirm payment: {e}")
    
    async def get_payment_status(self, provider_payment_id: str) -> PaymentResult:
        """
        Get Stripe payment status.
        
        Args:
            provider_payment_id: Stripe payment intent ID.
            
        Returns:
            PaymentResult: Current payment status.
            
        Raises:
            ValueError: If payment status retrieval fails.
        """
        if not STRIPE_AVAILABLE:
            # Stub implementation
            logger.info(f"Getting mock Stripe payment status for {provider_payment_id}")
            return PaymentResult(
                provider_payment_id=provider_payment_id,
                status="succeeded",
                amount=Decimal("100.00"),
                currency="USD",
                metadata={}
            )
        
        try:
            intent = stripe.PaymentIntent.retrieve(provider_payment_id)
            
            return PaymentResult(
                provider_payment_id=intent.id,
                status=intent.status,
                amount=Decimal(intent.amount) / 100,
                currency=intent.currency.upper(),
                metadata=intent.metadata
            )
            
        except Exception as e:
            logger.error(f"Stripe payment status retrieval failed: {e}")
            raise ValueError(f"Failed to get payment status: {e}")
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Verify Stripe webhook signature.
        
        Args:
            payload: Raw webhook payload.
            signature: Stripe signature header.
            timestamp: Not used for Stripe.
            
        Returns:
            bool: True if signature is valid.
        """
        if not self.webhook_secret:
            logger.warning("No Stripe webhook secret configured")
            return False
        
        if not STRIPE_AVAILABLE:
            # Stub implementation for testing
            logger.info("Mock verifying Stripe webhook signature")
            return True
        
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except Exception as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            return False
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Optional[PaymentResult]:
        """
        Process Stripe webhook payload.
        
        Args:
            payload: Stripe webhook payload.
            
        Returns:
            Optional[PaymentResult]: Payment result if applicable.
        """
        event_type = payload.get("type")
        
        if event_type in ["payment_intent.succeeded", "payment_intent.payment_failed"]:
            payment_intent = payload.get("data", {}).get("object", {})
            
            status = "succeeded" if event_type == "payment_intent.succeeded" else "failed"
            
            return PaymentResult(
                provider_payment_id=payment_intent.get("id"),
                status=status,
                amount=Decimal(payment_intent.get("amount", 0)) / 100,
                currency=payment_intent.get("currency", "USD").upper(),
                metadata=payment_intent.get("metadata", {})
            )
        
        logger.info(f"Unhandled Stripe webhook event: {event_type}")
        return None
    
    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> RefundResult:
        """
        Refund a Stripe payment.
        
        Args:
            provider_payment_id: Stripe payment intent ID.
            amount: Refund amount (full refund if None).
            reason: Refund reason.
            
        Returns:
            RefundResult: Refund result.
            
        Raises:
            ValueError: If refund fails.
        """
        if not STRIPE_AVAILABLE:
            # Stub implementation
            logger.info(f"Mock refunding Stripe payment {provider_payment_id}")
            return RefundResult(
                refund_id=f"re_mock_{provider_payment_id}",
                payment_id=provider_payment_id,
                amount=amount or Decimal("100.00"),
                currency="USD",
                status="succeeded"
            )
        
        try:
            refund_data = {"payment_intent": provider_payment_id}
            
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to cents
            
            if reason:
                refund_data["reason"] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            return RefundResult(
                refund_id=refund.id,
                payment_id=provider_payment_id,
                amount=Decimal(refund.amount) / 100,
                currency=refund.currency.upper(),
                status=refund.status,
                metadata=refund.metadata
            )
            
        except Exception as e:
            logger.error(f"Stripe refund failed: {e}")
            raise ValueError(f"Failed to process refund: {e}")
    
    def get_supported_currencies(self) -> list[str]:
        """Get Stripe supported currencies."""
        return [
            "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD",
            "MXN", "SGD", "HKD", "NOK", "DKK", "PLN", "CZK", "HUF", "ILS", "KRW",
            "MYR", "THB", "PHP", "INR", "BRL", "ZAR", "TRY", "RUB"
        ]