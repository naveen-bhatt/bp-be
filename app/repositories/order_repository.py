"""Order repository for database operations."""

from typing import Optional, List, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, desc

from app.models.order import Order, OrderItem, OrderStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class OrderRepository:
    """Repository for Order and OrderItem model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
    
    def create_order(
        self,
        user_id: Optional[str],
        total_amount: Decimal,
        currency: str = "USD"
    ) -> Order:
        """
        Create a new order.
        
        Args:
            user_id: User ID (nullable for guest orders).
            total_amount: Total order amount.
            currency: Currency code.
            
        Returns:
            Order: Created order instance.
        """
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            currency=currency,
            status=OrderStatus.CREATED.value
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Created order: {order.id}, amount: {total_amount} {currency}")
        return order
    
    def create_order_from_cart(self, cart: Cart, user_id: Optional[str] = None) -> Order:
        """
        Create order from cart items.
        
        Args:
            cart: Cart to create order from.
            user_id: User ID (overrides cart user_id if provided).
            
        Returns:
            Order: Created order with items.
        """
        # Calculate total
        total_amount = cart.calculate_total()
        currency = cart.items[0].product.currency if cart.items else "USD"
        
        # Create order
        order = self.create_order(
            user_id=user_id or cart.user_id,
            total_amount=total_amount,
            currency=currency
        )
        
        # Create order items from cart items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price
            )
            self.db.add(order_item)
        
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Created order from cart: {order.id}, items: {len(cart.items)}")
        return order
    
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """
        Get order by ID with items loaded.
        
        Args:
            order_id: Order ID to search for.
            
        Returns:
            Optional[Order]: Order if found, None otherwise.
        """
        return self.db.query(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payments)
        ).filter(Order.id == order_id).first()
    
    def get_user_order(self, user_id: str, order_id: str) -> Optional[Order]:
        """
        Get order by ID for specific user.
        
        Args:
            user_id: User ID.
            order_id: Order ID.
            
        Returns:
            Optional[Order]: Order if found and belongs to user, None otherwise.
        """
        return self.db.query(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.payments)
        ).filter(
            and_(Order.id == order_id, Order.user_id == user_id)
        ).first()
    
    def list_user_orders(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Order], int]:
        """
        List orders for a user with pagination.
        
        Args:
            user_id: User ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            Tuple[List[Order], int]: Tuple of (orders, total_count).
        """
        query = self.db.query(Order).filter(Order.user_id == user_id)
        
        total_count = query.count()
        orders = query.options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
        
        return orders, total_count
    
    def list_orders_by_status(
        self,
        status: OrderStatus,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Order], int]:
        """
        List orders by status with pagination.
        
        Args:
            status: Order status to filter by.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            Tuple[List[Order], int]: Tuple of (orders, total_count).
        """
        query = self.db.query(Order).filter(Order.status == status.value)
        
        total_count = query.count()
        orders = query.options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
        
        return orders, total_count
    
    def update_status(self, order: Order, new_status: OrderStatus) -> Order:
        """
        Update order status.
        
        Args:
            order: Order to update.
            new_status: New order status.
            
        Returns:
            Order: Updated order instance.
        """
        old_status = order.status
        order.status = new_status.value
        
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Updated order {order.id} status: {old_status} -> {new_status.value}")
        return order
    
    def update_total(self, order: Order, new_total: Decimal) -> Order:
        """
        Update order total amount.
        
        Args:
            order: Order to update.
            new_total: New total amount.
            
        Returns:
            Order: Updated order instance.
        """
        old_total = order.total_amount
        order.total_amount = new_total
        
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Updated order {order.id} total: {old_total} -> {new_total}")
        return order
    
    def add_order_item(
        self,
        order: Order,
        product_id: str,
        quantity: int,
        unit_price: Decimal
    ) -> OrderItem:
        """
        Add item to order.
        
        Args:
            order: Order to add item to.
            product_id: Product ID.
            quantity: Quantity.
            unit_price: Price per unit.
            
        Returns:
            OrderItem: Created order item.
        """
        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        
        logger.info(f"Added item to order {order.id}: product {product_id}, qty {quantity}")
        return order_item
    
    def get_order_item(self, order_id: str, product_id: str) -> Optional[OrderItem]:
        """
        Get specific order item.
        
        Args:
            order_id: Order ID.
            product_id: Product ID.
            
        Returns:
            Optional[OrderItem]: Order item if found, None otherwise.
        """
        return self.db.query(OrderItem).filter(
            and_(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id
            )
        ).first()
    
    def delete_order(self, order: Order) -> None:
        """
        Delete order and all its items.
        
        Args:
            order: Order to delete.
        """
        order_id = order.id
        self.db.delete(order)
        self.db.commit()
        
        logger.info(f"Deleted order: {order_id}")
    
    def count_orders_by_status(self, status: OrderStatus) -> int:
        """
        Count orders by status.
        
        Args:
            status: Order status to count.
            
        Returns:
            int: Number of orders with the given status.
        """
        return self.db.query(Order).filter(Order.status == status.value).count()
    
    def get_orders_pending_payment(self, hours_old: int = 24) -> List[Order]:
        """
        Get orders that are pending payment for more than specified hours.
        
        Args:
            hours_old: Number of hours to look back.
            
        Returns:
            List[Order]: List of orders pending payment.
        """
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
        
        return self.db.query(Order).filter(
            and_(
                Order.status == OrderStatus.CREATED.value,
                Order.created_at < cutoff_time
            )
        ).all()