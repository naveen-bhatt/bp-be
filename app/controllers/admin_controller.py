"""Admin controller for admin interface."""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.admin_dependencies import get_admin_user, get_superadmin_user
from app.core.dependencies import DatabaseSession, AdminUserId
from app.schemas.admin import (
    OrderFilter, PaginationFilter, ShippedOrdersFilter, BulkShipRequest, BulkShipResponse, 
    OrderCancelRequest, OrderCancelResponse, AdminOrderListResponse, 
    ShippedOrdersAddressList, AdminStats
)
from app.schemas.order import OrderSummary
from app.services.admin_service import AdminService
from app.models.user import User


def get_recent_orders(
    current_user: AdminUserId,
    db: DatabaseSession,
    filters: OrderFilter = Depends(),
    pagination: PaginationFilter = Depends()
) -> AdminOrderListResponse:
    """
    Get recent orders with custom filters (Admin only).
    
    Args:
        current_user: Current admin user ID.
        db: Database session.
        filters: Order filtering parameters.
        pagination: Pagination parameters.
        
    Returns:
        AdminOrderListResponse: Filtered orders with count.
    """
    try:
        admin_service = AdminService(db)
        return admin_service.get_recent_orders(
            filters=filters,
            limit=pagination.limit,
            offset=pagination.offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orders: {str(e)}"
        )


def bulk_ship_orders(
    request: BulkShipRequest,
    current_user: AdminUserId,
    db: DatabaseSession
) -> BulkShipResponse:
    """
    Bulk ship multiple orders (Admin only).
    
    Args:
        request: Bulk ship request with order IDs.
        current_user: Current admin user ID.
        db: Database session.
        
    Returns:
        BulkShipResponse: Result of bulk shipping operation.
    """
    try:
        admin_service = AdminService(db)
        return admin_service.bulk_ship_orders(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk ship orders: {str(e)}"
        )


def cancel_order(
    order_id: str,
    request: OrderCancelRequest,
    current_user: AdminUserId,
    db: DatabaseSession
) -> OrderCancelResponse:
    """
    Cancel an order (Admin only).
    
    Args:
        order_id: Order ID to cancel.
        request: Cancellation request with reason.
        current_user: Current admin user ID.
        db: Database session.
        
    Returns:
        OrderCancelResponse: Cancellation result.
    """
    try:
        admin_service = AdminService(db)
        return admin_service.cancel_order(order_id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}"
        )


def get_shipped_orders(
    current_user: AdminUserId,
    db: DatabaseSession,
    filters: ShippedOrdersFilter = Depends()
) -> List[OrderSummary]:
    """
    Get all shipped orders (Admin only).
    
    Args:
        current_user: Current admin user ID.
        db: Database session.
        filters: Pagination filters for shipped orders.
        
    Returns:
        List[OrderSummary]: List of shipped orders.
    """
    try:
        admin_service = AdminService(db)
        shipped_orders = admin_service.get_shipped_orders(limit=filters.limit, offset=filters.offset)
        
        # Convert to summary schemas
        order_summaries = []
        for order in shipped_orders:
            summary = admin_service._order_to_summary_schema(order)
            order_summaries.append(OrderSummary(**summary))
        
        return order_summaries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get shipped orders: {str(e)}"
        )


def generate_shipped_orders_address_pdf(
    current_user: AdminUserId,
    db: DatabaseSession
) -> ShippedOrdersAddressList:
    """
    Generate address list for all shipped orders (Admin only).
    
    Args:
        current_user: Current admin user ID.
        db: Database session.
        
    Returns:
        ShippedOrdersAddressList: Address information for shipped orders.
    """
    try:
        admin_service = AdminService(db)
        return admin_service.generate_shipped_orders_address_pdf()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate address list: {str(e)}"
        )


def get_admin_stats(
    current_user: AdminUserId,
    db: DatabaseSession
) -> AdminStats:
    """
    Get admin dashboard statistics (Admin only).
    
    Args:
        current_user: Current admin user ID.
        db: Database session.
        
    Returns:
        AdminStats: Dashboard statistics.
    """
    try:
        admin_service = AdminService(db)
        return admin_service.get_admin_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin stats: {str(e)}"
        )
