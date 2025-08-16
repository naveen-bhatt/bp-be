"""Base payment provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PaymentIntent:
    """Payment intent response."""
    
    provider_payment_id: str
    client_secret: Optional[str] = None
    payment_url: Optional[str] = None
    status: str = "pending"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PaymentResult:
    """Payment processing result."""
    
    provider_payment_id: str
    status: str  # "succeeded", "failed", "pending"
    amount: Decimal
    currency: str
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RefundResult:
    """Refund processing result."""
    
    refund_id: str
    payment_id: str
    amount: Decimal
    currency: str
    status: str  # "succeeded", "failed", "pending"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        """
        Initialize payment provider.
        
        Args:
            api_key: API key for the payment provider.
            webhook_secret: Webhook secret for signature verification.
        """
        self.api_key = api_key
        self.webhook_secret = webhook_secret
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass
    
    @abstractmethod
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        order_id: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """
        Create a payment intent.
        
        Args:
            amount: Payment amount.
            currency: Currency code.
            order_id: Internal order ID.
            customer_email: Customer email address.
            metadata: Additional metadata.
            
        Returns:
            PaymentIntent: Payment intent with client secret or payment URL.
            
        Raises:
            ValueError: If payment intent creation fails.
        """
        pass
    
    @abstractmethod
    async def confirm_payment(
        self,
        provider_payment_id: str,
        payment_method: Optional[str] = None
    ) -> PaymentResult:
        """
        Confirm a payment.
        
        Args:
            provider_payment_id: Payment ID from provider.
            payment_method: Payment method identifier.
            
        Returns:
            PaymentResult: Payment confirmation result.
            
        Raises:
            ValueError: If payment confirmation fails.
        """
        pass
    
    @abstractmethod
    async def get_payment_status(self, provider_payment_id: str) -> PaymentResult:
        """
        Get payment status.
        
        Args:
            provider_payment_id: Payment ID from provider.
            
        Returns:
            PaymentResult: Current payment status.
            
        Raises:
            ValueError: If payment status retrieval fails.
        """
        pass
    
    @abstractmethod
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Raw webhook payload.
            signature: Webhook signature.
            timestamp: Webhook timestamp (if required).
            
        Returns:
            bool: True if signature is valid.
        """
        pass
    
    @abstractmethod
    async def process_webhook(self, payload: Dict[str, Any]) -> Optional[PaymentResult]:
        """
        Process webhook payload.
        
        Args:
            payload: Webhook payload data.
            
        Returns:
            Optional[PaymentResult]: Payment result if applicable.
        """
        pass
    
    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> RefundResult:
        """
        Refund a payment.
        
        Args:
            provider_payment_id: Payment ID from provider.
            amount: Refund amount (full refund if None).
            reason: Refund reason.
            
        Returns:
            RefundResult: Refund result.
            
        Raises:
            NotImplementedError: If provider doesn't support refunds.
        """
        raise NotImplementedError(f"{self.provider_name} doesn't support refunds")
    
    async def cancel_payment(self, provider_payment_id: str) -> bool:
        """
        Cancel a pending payment.
        
        Args:
            provider_payment_id: Payment ID from provider.
            
        Returns:
            bool: True if cancellation successful.
            
        Raises:
            NotImplementedError: If provider doesn't support cancellation.
        """
        raise NotImplementedError(f"{self.provider_name} doesn't support payment cancellation")
    
    def get_supported_currencies(self) -> list[str]:
        """
        Get list of supported currencies.
        
        Returns:
            list[str]: List of supported currency codes.
        """
        # Default to common currencies
        return ["INR", "USD", "EUR", "GBP", "AUD", "CAD"]
    
    def is_currency_supported(self, currency: str) -> bool:
        """
        Check if currency is supported.
        
        Args:
            currency: Currency code to check.
            
        Returns:
            bool: True if currency is supported.
        """
        return currency.upper() in self.get_supported_currencies()