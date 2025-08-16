"""Order service with business logic."""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreateRequest, OrderSummary, OrderListResponse, OrderItemSummary
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartState


class OrderService:
    """Service for order operations."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)
    
    def create_order(self, user_id: str, order_data: OrderCreateRequest) -> OrderSummary:
        """
        Create a new order from user's cart.
        
        Args:
            user_id: User ID.
            order_data: Order creation data with cart_id and address_id.
            
        Returns:
            OrderPublic: Created order.
            
        Raises:
            ValueError: If cart is empty or order creation fails.
        """
        # Validate required fields
        if not order_data.cart_id:
            raise ValueError("Cart ID is required")
        
        if not order_data.address_id:
            raise ValueError("Address ID is required")
        
        # Get active cart items for the user
        cart_items = self.cart_repo.get_items_by_user_id(user_id)
        active_cart_items = [item for item in cart_items if item.cart_state == CartState.ACTIVE]
        
        if not active_cart_items:
            raise ValueError("No active items in cart to create order")
        
        # Calculate total amount
        total_amount = sum(item.subtotal for item in active_cart_items)
        
        # Create order
        order = self.order_repo.create(
            user_id=user_id,
            address_id=order_data.address_id,
            cart_id=order_data.cart_id,
            total_amount=total_amount,
            currency="INR",  # Default currency
            status=OrderStatus.INITIATED
        )
        
        # Create order items from cart items
        order_items = []
        for cart_item in active_cart_items:
            order_item = self.order_repo.create_order_item(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            order_items.append(order_item)
        
        # Expire all cart items for this user
        for cart_item in active_cart_items:
            cart_item.expire_cart()
        
        self.db.commit()
        
        # Convert to schema
        return self._order_to_public_schema(order, order_items)
    
    def get_order(self, user_id: str, order_id: str) -> OrderSummary:
        """
        Get order by ID.
        
        Args:
            user_id: User ID.
            order_id: Order ID.
            
        Returns:
            OrderPublic: Order details.
            
        Raises:
            ValueError: If order not found or doesn't belong to the user.
        """
        order = self.order_repo.get_by_user_and_id(user_id, order_id)
        if not order:
            raise ValueError(f"Order not found or doesn't belong to the user: {order_id}")
        
        return self._order_to_public_schema(order, order.items)
    
    def list_orders(self, user_id: str, limit: int = 50, offset: int = 0) -> OrderListResponse:
        """
        List all orders for a user.
        
        Args:
            user_id: User ID.
            limit: Maximum number of orders to return.
            offset: Number of orders to skip.
            
        Returns:
            OrderListResponse: List of orders.
        """
        orders = self.order_repo.list_by_user_id(user_id, limit=limit, offset=offset)
        count = self.order_repo.count_by_user_id(user_id)
        
        # Convert to summary schemas
        order_summaries = []
        for order in orders:
            summary = OrderSummary(
                id=order.id,
                address_id=order.address_id,
                cart_id=order.cart_id,
                shipping_id=order.shipping_id,
                admin_notes=order.admin_notes,
                spam_order=order.spam_order,
                total_amount=str(order.total_amount),
                currency=order.currency,
                status=order.status,
                created_at=order.created_at,
                item_count=len(order.items)
            )
            order_summaries.append(summary)
        
        return OrderListResponse(
            items=order_summaries,
            count=count
        )
    
    def update_order_status(self, user_id: str, order_id: str, new_status: OrderStatus) -> OrderSummary:
        """
        Update order status.
        
        Args:
            user_id: User ID.
            order_id: Order ID.
            new_status: New order status.
            
        Returns:
            OrderPublic: Updated order.
            
        Raises:
            ValueError: If order not found or doesn't belong to the user.
        """
        order = self.order_repo.get_by_user_and_id(user_id, order_id)
        if not order:
            raise ValueError(f"Order not found or doesn't belong to the user: {order_id}")
        
        # Update status
        order.update_status(new_status)
        self.db.commit()
        
        return self._order_to_public_schema(order, order.items)
    
    def _order_to_public_schema(self, order: Order, order_items: List[OrderItem]) -> OrderSummary:
        """
        Convert Order model to OrderSummary schema.
        
        Args:
            order: Order model instance.
            order_items: List of order items.
            
        Returns:
            OrderSummary: Order summary schema with items included.
        """
        # Convert order items to schemas
        item_schemas = []
        for item in order_items:
            # Get product details
            product = self.product_repo.get_by_id(item.product_id)
            product_data = None
            if product:
                product_data = self.product_repo.to_list_schema(product)
            
            item_schema = OrderItemSummary(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=str(item.unit_price),
                subtotal=str(item.subtotal),
                product=product_data,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            item_schemas.append(item_schema)
        
        return OrderSummary(
            id=order.id,
            user_id=order.user_id,
            address_id=order.address_id,
            cart_id=order.cart_id,
            shipping_id=order.shipping_id,
            admin_notes=order.admin_notes,
            spam_order=order.spam_order,
            total_amount=str(order.total_amount),
            currency=order.currency,
            status=order.status,
            item_count=len(order_items),
            items=item_schemas,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
