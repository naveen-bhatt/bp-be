"""Razorpay payment provider implementation."""

import hmac
import hashlib
from typing import Dict, Any, Optional
from decimal import Decimal

from .base import PaymentProvider, PaymentIntent, PaymentResult, RefundResult
from app.core.logging import get_logger

logger = get_logger(__name__)

# Try to import Razorpay SDK
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    logger.warning("Razorpay SDK not available. Install with: pip install razorpay")


class RazorpayPaymentProvider(PaymentProvider):
    """
    Razorpay payment provider implementation.
    
    TODO: To use Razorpay integration:
    1. Install Razorpay SDK: pip install razorpay
    2. Obtain Razorpay API keys from Razorpay Dashboard
    3. Set up webhook endpoints in Razorpay Dashboard
    4. Configure webhook secrets for signature verification
    
    Note: This implementation provides a working stub if Razorpay SDK is not installed.
    """
    
    def __init__(self, key_id: str, key_secret: str, webhook_secret: Optional[str] = None):
        """Initialize Razorpay payment provider."""
        super().__init__(key_id, webhook_secret)
        self.key_secret = key_secret
        
        if RAZORPAY_AVAILABLE:
            self.client = razorpay.Client(auth=(key_id, key_secret))
        else:
            logger.warning("Razorpay SDK not available - using stub implementation")
            self.client = None
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "razorpay"
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        order_id: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """
        Create a Razorpay order (equivalent to payment intent).
        
        Args:
            amount: Payment amount.
            currency: Currency code.
            order_id: Internal order ID.
            customer_email: Customer email address.
            metadata: Additional metadata.
            
        Returns:
            PaymentIntent: Payment intent with order details.
            
        Raises:
            ValueError: If order creation fails.
        """
        if not RAZORPAY_AVAILABLE:
            # Stub implementation for testing
            logger.info(f"Creating mock Razorpay order for order {order_id}")
            return PaymentIntent(
                provider_payment_id=f"order_mock_{order_id}",
                client_secret=None,  # Razorpay doesn't use client secrets
                payment_url=f"https://checkout.razorpay.com/v1/checkout.js",
                status="created",
                metadata={
                    "key_id": self.api_key,
                    "order_id": f"order_mock_{order_id}",
                    "amount": str(int(amount * 100)),  # Amount in paise
                    "currency": currency,
                    **(metadata or {})
                }
            )
        
        try:
            # Convert amount to smallest currency unit (paise for INR)
            amount_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_paise,
                "currency": currency.upper(),
                "receipt": order_id,
                "notes": {
                    "order_id": order_id,
                    **(metadata or {})
                }
            }
            
            razorpay_order = self.client.order.create(data=order_data)
            
            return PaymentIntent(
                provider_payment_id=razorpay_order["id"],
                payment_url="https://checkout.razorpay.com/v1/checkout.js",
                status=razorpay_order["status"],
                metadata={
                    "key_id": self.api_key,
                    "order_id": razorpay_order["id"],
                    "amount": str(razorpay_order["amount"]),
                    "currency": razorpay_order["currency"],
                    "receipt": razorpay_order["receipt"]
                }
            )
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {e}")
            raise ValueError(f"Failed to create order: {e}")
    
    async def confirm_payment(
        self,
        provider_payment_id: str,
        payment_method: Optional[str] = None
    ) -> PaymentResult:
        """
        Confirm a Razorpay payment (capture payment).
        
        Args:
            provider_payment_id: Razorpay payment ID.
            payment_method: Not used for Razorpay.
            
        Returns:
            PaymentResult: Payment confirmation result.
            
        Raises:
            ValueError: If payment confirmation fails.
        """
        if not RAZORPAY_AVAILABLE:
            # Stub implementation
            logger.info(f"Mock confirming Razorpay payment {provider_payment_id}")
            return PaymentResult(
                provider_payment_id=provider_payment_id,
                status="captured",
                amount=Decimal("100.00"),
                currency="INR",
                metadata={}
            )
        
        try:
            # Get payment details
            payment = self.client.payment.fetch(provider_payment_id)
            
            # Capture payment if it's authorized but not captured
            if payment["status"] == "authorized":
                payment = self.client.payment.capture(
                    provider_payment_id,
                    payment["amount"]
                )
            
            return PaymentResult(
                provider_payment_id=payment["id"],
                status=payment["status"],
                amount=Decimal(payment["amount"]) / 100,  # Convert from paise
                currency=payment["currency"],
                metadata=payment.get("notes", {})
            )
            
        except Exception as e:
            logger.error(f"Razorpay payment confirmation failed: {e}")
            raise ValueError(f"Failed to confirm payment: {e}")
    
    async def get_payment_status(self, provider_payment_id: str) -> PaymentResult:
        """
        Get Razorpay payment status.
        
        Args:
            provider_payment_id: Razorpay payment ID.
            
        Returns:
            PaymentResult: Current payment status.
            
        Raises:
            ValueError: If payment status retrieval fails.
        """
        if not RAZORPAY_AVAILABLE:
            # Stub implementation
            logger.info(f"Getting mock Razorpay payment status for {provider_payment_id}")
            return PaymentResult(
                provider_payment_id=provider_payment_id,
                status="captured",
                amount=Decimal("100.00"),
                currency="INR",
                metadata={}
            )
        
        try:
            payment = self.client.payment.fetch(provider_payment_id)
            
            return PaymentResult(
                provider_payment_id=payment["id"],
                status=payment["status"],
                amount=Decimal(payment["amount"]) / 100,
                currency=payment["currency"],
                metadata=payment.get("notes", {})
            )
            
        except Exception as e:
            logger.error(f"Razorpay payment status retrieval failed: {e}")
            raise ValueError(f"Failed to get payment status: {e}")
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Verify Razorpay webhook signature.
        
        Args:
            payload: Raw webhook payload.
            signature: Razorpay signature.
            timestamp: Not used for Razorpay.
            
        Returns:
            bool: True if signature is valid.
        """
        if not self.webhook_secret:
            logger.warning("No Razorpay webhook secret configured")
            return False
        
        if not RAZORPAY_AVAILABLE:
            # Stub implementation for testing
            logger.info("Mock verifying Razorpay webhook signature")
            return True
        
        try:
            # Razorpay signature verification
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Razorpay webhook signature verification failed: {e}")
            return False
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Optional[PaymentResult]:
        """
        Process Razorpay webhook payload.
        
        Args:
            payload: Razorpay webhook payload.
            
        Returns:
            Optional[PaymentResult]: Payment result if applicable.
        """
        event = payload.get("event")
        
        if event in ["payment.captured", "payment.failed"]:
            payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})
            
            status = "succeeded" if event == "payment.captured" else "failed"
            
            return PaymentResult(
                provider_payment_id=payment_data.get("id"),
                status=status,
                amount=Decimal(payment_data.get("amount", 0)) / 100,
                currency=payment_data.get("currency", "INR").upper(),
                metadata=payment_data.get("notes", {})
            )
        
        logger.info(f"Unhandled Razorpay webhook event: {event}")
        return None
    
    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> RefundResult:
        """
        Refund a Razorpay payment.
        
        Args:
            provider_payment_id: Razorpay payment ID.
            amount: Refund amount (full refund if None).
            reason: Refund reason.
            
        Returns:
            RefundResult: Refund result.
            
        Raises:
            ValueError: If refund fails.
        """
        if not RAZORPAY_AVAILABLE:
            # Stub implementation
            logger.info(f"Mock refunding Razorpay payment {provider_payment_id}")
            return RefundResult(
                refund_id=f"rfnd_mock_{provider_payment_id}",
                payment_id=provider_payment_id,
                amount=amount or Decimal("100.00"),
                currency="INR",
                status="processed"
            )
        
        try:
            refund_data = {}
            
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to paise
            
            if reason:
                refund_data["notes"] = {"reason": reason}
            
            refund = self.client.payment.refund(provider_payment_id, refund_data)
            
            return RefundResult(
                refund_id=refund["id"],
                payment_id=provider_payment_id,
                amount=Decimal(refund["amount"]) / 100,
                currency=refund["currency"],
                status=refund["status"],
                metadata=refund.get("notes", {})
            )
            
        except Exception as e:
            logger.error(f"Razorpay refund failed: {e}")
            raise ValueError(f"Failed to process refund: {e}")
    
    def get_supported_currencies(self) -> list[str]:
        """Get Razorpay supported currencies."""
        return [
            "INR", "USD", "EUR", "GBP", "AUD", "CAD", "SGD", "AED", "MYR", "THB"
        ]