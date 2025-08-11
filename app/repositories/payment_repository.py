"""Payment repository for database operations."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class PaymentRepository:
    """Repository for Payment model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
    
    def create_payment(
        self,
        order_id: str,
        provider: PaymentProvider,
        amount: Decimal,
        currency: str = "USD",
        provider_payment_id: Optional[str] = None
    ) -> Payment:
        """
        Create a new payment.
        
        Args:
            order_id: Order ID to associate payment with.
            provider: Payment provider.
            amount: Payment amount.
            currency: Currency code.
            provider_payment_id: Payment ID from provider.
            
        Returns:
            Payment: Created payment instance.
        """
        payment = Payment(
            order_id=order_id,
            provider=provider.value,
            amount=amount,
            currency=currency,
            provider_payment_id=provider_payment_id,
            status=PaymentStatus.PENDING.value
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Created payment: {payment.id}, provider: {provider.value}, amount: {amount}")
        return payment
    
    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """
        Get payment by ID.
        
        Args:
            payment_id: Payment ID to search for.
            
        Returns:
            Optional[Payment]: Payment if found, None otherwise.
        """
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def get_by_provider_payment_id(
        self,
        provider: PaymentProvider,
        provider_payment_id: str
    ) -> Optional[Payment]:
        """
        Get payment by provider payment ID.
        
        Args:
            provider: Payment provider.
            provider_payment_id: Provider payment ID.
            
        Returns:
            Optional[Payment]: Payment if found, None otherwise.
        """
        return self.db.query(Payment).filter(
            and_(
                Payment.provider == provider.value,
                Payment.provider_payment_id == provider_payment_id
            )
        ).first()
    
    def get_order_payments(self, order_id: str) -> List[Payment]:
        """
        Get all payments for an order.
        
        Args:
            order_id: Order ID to search for.
            
        Returns:
            List[Payment]: List of payments for the order.
        """
        return self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).order_by(desc(Payment.created_at)).all()
    
    def get_latest_payment_for_order(self, order_id: str) -> Optional[Payment]:
        """
        Get latest payment for an order.
        
        Args:
            order_id: Order ID to search for.
            
        Returns:
            Optional[Payment]: Latest payment if found, None otherwise.
        """
        return self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).order_by(desc(Payment.created_at)).first()
    
    def update_status(
        self,
        payment: Payment,
        new_status: PaymentStatus,
        provider_payment_id: Optional[str] = None,
        raw_payload: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        Update payment status and provider data.
        
        Args:
            payment: Payment to update.
            new_status: New payment status.
            provider_payment_id: Provider payment ID.
            raw_payload: Raw response from provider.
            
        Returns:
            Payment: Updated payment instance.
        """
        old_status = payment.status
        payment.status = new_status.value
        
        if provider_payment_id:
            payment.provider_payment_id = provider_payment_id
        
        if raw_payload:
            payment.raw_payload = raw_payload
        
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Updated payment {payment.id} status: {old_status} -> {new_status.value}")
        return payment
    
    def update_provider_data(
        self,
        payment: Payment,
        provider_payment_id: str,
        raw_payload: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        Update provider-specific payment data.
        
        Args:
            payment: Payment to update.
            provider_payment_id: Provider payment ID.
            raw_payload: Raw response from provider.
            
        Returns:
            Payment: Updated payment instance.
        """
        payment.provider_payment_id = provider_payment_id
        
        if raw_payload:
            payment.raw_payload = raw_payload
        
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"Updated payment {payment.id} provider data")
        return payment
    
    def list_payments_by_status(
        self,
        status: PaymentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        List payments by status with pagination.
        
        Args:
            status: Payment status to filter by.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List[Payment]: List of payments with the given status.
        """
        return self.db.query(Payment).filter(
            Payment.status == status.value
        ).order_by(desc(Payment.created_at)).offset(skip).limit(limit).all()
    
    def list_payments_by_provider(
        self,
        provider: PaymentProvider,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        List payments by provider with pagination.
        
        Args:
            provider: Payment provider to filter by.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List[Payment]: List of payments for the given provider.
        """
        return self.db.query(Payment).filter(
            Payment.provider == provider.value
        ).order_by(desc(Payment.created_at)).offset(skip).limit(limit).all()
    
    def count_payments_by_status(self, status: PaymentStatus) -> int:
        """
        Count payments by status.
        
        Args:
            status: Payment status to count.
            
        Returns:
            int: Number of payments with the given status.
        """
        return self.db.query(Payment).filter(Payment.status == status.value).count()
    
    def get_pending_payments(self, hours_old: int = 1) -> List[Payment]:
        """
        Get payments that are pending for more than specified hours.
        
        Args:
            hours_old: Number of hours to look back.
            
        Returns:
            List[Payment]: List of pending payments.
        """
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
        
        return self.db.query(Payment).filter(
            and_(
                Payment.status == PaymentStatus.PENDING.value,
                Payment.created_at < cutoff_time
            )
        ).all()
    
    def delete_payment(self, payment: Payment) -> None:
        """
        Delete a payment.
        
        Args:
            payment: Payment to delete.
        """
        payment_id = payment.id
        self.db.delete(payment)
        self.db.commit()
        
        logger.info(f"Deleted payment: {payment_id}")