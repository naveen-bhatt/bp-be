"""Admin service for admin interface operations."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, desc, func

from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.repositories.address_repository import AddressRepository
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.schemas.admin import (
    OrderFilter, BulkShipRequest, BulkShipResponse, OrderCancelRequest,
    OrderCancelResponse, AdminOrderListResponse, ShippedOrderAddress,
    ShippedOrdersAddressList, AdminStats
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AdminService:
    """Service for admin operations."""
    
    def __init__(self, db: Session):
        """
        Initialize admin service with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.order_repo = OrderRepository(db)
        self.user_repo = UserRepository(db)
        self.address_repo = AddressRepository(db)
    
    def get_recent_orders(
        self,
        filters: OrderFilter,
        limit: int = 50,
        offset: int = 0
    ) -> AdminOrderListResponse:
        """
        Get recent orders with custom filters for admin.
        
        Args:
            filters: Order filtering parameters.
            limit: Maximum number of orders to return.
            offset: Number of orders to skip.
            
        Returns:
            AdminOrderListResponse: Filtered orders with count.
        """
        # Build query with filters
        query = self.db.query(Order)
        
        if filters.status:
            query = query.filter(Order.status == filters.status)
        
        if filters.user_id:
            query = query.filter(Order.user_id == filters.user_id)
        
        if filters.date_from:
            query = query.filter(Order.created_at >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(Order.created_at <= filters.date_to)
        
        if filters.min_amount:
            query = query.filter(Order.total_amount >= Decimal(filters.min_amount))
        
        if filters.max_amount:
            query = query.filter(Order.total_amount <= Decimal(filters.max_amount))
        
        if filters.address_id:
            query = query.filter(Order.address_id == filters.address_id)
        
        if filters.shipping_id:
            query = query.filter(Order.shipping_id == filters.shipping_id)
        
        if filters.spam_order is not None:
            query = query.filter(Order.spam_order == filters.spam_order)
        
        if filters.has_admin_notes is not None:
            if filters.has_admin_notes:
                query = query.filter(Order.admin_notes.isnot(None))
            else:
                query = query.filter(Order.admin_notes.is_(None))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        orders = query.options(
            selectinload(Order.items),
            selectinload(Order.user),
            selectinload(Order.address)
        ).order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
        
        # Convert to schemas
        order_summaries = []
        for order in orders:
            summary = self._order_to_summary_schema(order)
            order_summaries.append(summary)
        
        return AdminOrderListResponse(
            items=order_summaries,
            count=total_count,
            filters_applied=filters
        )
    
    def bulk_ship_orders(self, request: BulkShipRequest) -> BulkShipResponse:
        """
        Bulk ship multiple orders.
        
        Args:
            request: Bulk ship request with order IDs.
            
        Returns:
            BulkShipResponse: Result of bulk shipping operation.
        """
        success_count = 0
        failed_count = 0
        failed_orders = []
        
        for order_id in request.order_ids:
            try:
                order = self.order_repo.get_by_id(order_id)
                if not order:
                    failed_count += 1
                    failed_orders.append(order_id)
                    continue
                
                # Update order status to shipped
                order.update_status(OrderStatus.SUCCESSFUL)
                
                # TODO: Send notification email
                # await self._send_shipping_notification(order)
                
                success_count += 1
                logger.info(f"Order {order_id} shipped successfully")
                
            except Exception as e:
                failed_count += 1
                failed_orders.append(order_id)
                logger.error(f"Failed to ship order {order_id}: {str(e)}")
        
        self.db.commit()
        
        message = f"Successfully shipped {success_count} orders"
        if failed_count > 0:
            message += f", {failed_count} failed"
        
        return BulkShipResponse(
            success_count=success_count,
            failed_count=failed_count,
            failed_orders=failed_orders,
            message=message
        )
    
    def cancel_order(self, order_id: str, request: OrderCancelRequest) -> OrderCancelResponse:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel.
            request: Cancellation request with reason.
            
        Returns:
            OrderCancelResponse: Cancellation result.
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        # Check if order can be cancelled
        if order.status in [OrderStatus.SUCCESSFUL.value, OrderStatus.FAILURE.value]:
            raise ValueError(f"Order {order_id} cannot be cancelled in current status: {order.status}")
        
        # Update order status to cancelled
        # Note: We need to add CANCELLED status to OrderStatus enum
        # For now, we'll use FAILURE status
        order.update_status(OrderStatus.FAILURE)
        
        # TODO: Send cancellation notification email
        # await self._send_cancellation_notification(order, request.reason)
        
        self.db.commit()
        
        logger.info(f"Order {order_id} cancelled: {request.reason}")
        
        return OrderCancelResponse(
            order_id=order_id,
            status=order.status,
            message=f"Order cancelled: {request.reason}"
        )
    
    def get_shipped_orders(self, limit: int = 100, offset: int = 0) -> List[Order]:
        """
        Get all shipped orders.
        
        Args:
            limit: Maximum number of orders to return.
            offset: Number of orders to skip.
            
        Returns:
            List[Order]: List of shipped orders.
        """
        return self.db.query(Order).filter(
            Order.status == OrderStatus.SUCCESSFUL.value
        ).options(
            selectinload(Order.user),
            selectinload(Order.address)
        ).order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
    
    def generate_shipped_orders_address_pdf(self) -> ShippedOrdersAddressList:
        """
        Generate address list for all shipped orders.
        
        Returns:
            ShippedOrdersAddressList: Address information for shipped orders.
        """
        shipped_orders = self.get_shipped_orders(limit=1000)  # Get all shipped orders
        
        addresses = []
        for order in shipped_orders:
            if order.address:
                address = ShippedOrderAddress(
                    order_id=order.id,
                    user_name=f"{order.address.first_name or ''} {order.address.last_name or ''}".strip(),
                    address_line1=order.address.street1 or '',
                    address_line2=order.address.street2,
                    city=order.address.city or '',
                    state=order.address.state or '',
                    pincode=order.address.pincode or '',
                    country=order.address.country or '',
                    phone=order.address.phone_number or '',
                    order_date=order.created_at,
                    shipping_date=order.updated_at  # Assuming this is when it was shipped
                )
                addresses.append(address)
        
        return ShippedOrdersAddressList(
            addresses=addresses,
            count=len(addresses),
            generated_at=datetime.utcnow()
        )
    
    def get_admin_stats(self) -> AdminStats:
        """
        Get admin dashboard statistics.
        
        Returns:
            AdminStats: Dashboard statistics.
        """
        # Total orders
        total_orders = self.db.query(Order).count()
        
        # Orders by status
        pending_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING.value
        ).count()
        
        shipped_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.SUCCESSFUL.value
        ).count()
        
        cancelled_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.FAILURE.value
        ).count()
        
        # Total revenue
        total_revenue = self.db.query(func.sum(Order.total_amount)).scalar() or Decimal('0')
        
        # Today's orders and revenue
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= today_start,
                Order.created_at <= today_end
            )
        ).count()
        
        today_revenue = self.db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.created_at >= today_start,
                Order.created_at <= today_end
            )
        ).scalar() or Decimal('0')
        
        return AdminStats(
            total_orders=total_orders,
            pending_orders=pending_orders,
            shipped_orders=shipped_orders,
            cancelled_orders=cancelled_orders,
            total_revenue=str(total_revenue),
            today_orders=today_orders,
            today_revenue=str(today_revenue)
        )
    
    def _order_to_summary_schema(self, order: Order) -> dict:
        """
        Convert Order model to summary schema for admin.
        
        Args:
            order: Order model instance.
            
        Returns:
            dict: Order summary data.
        """
        return {
            "id": order.id,
            "user_id": order.user_id,
            "address_id": order.address_id,
            "cart_id": order.cart_id,
            "shipping_id": order.shipping_id,
            "admin_notes": order.admin_notes,
            "spam_order": order.spam_order,
            "total_amount": str(order.total_amount),
            "currency": order.currency,
            "status": order.status,
            "item_count": len(order.items) if order.items else 0,
            "items": None,  # Not including items for list view
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }
