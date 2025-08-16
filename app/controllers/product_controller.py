"""Product controller - handles HTTP request/response logic."""

from typing import Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import DatabaseSession, AdminUserId, Pagination
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductPublic, ProductDetail,
    ProductList, ProductSearch, StockUpdate, ProductFilter
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.core.logging import get_logger

from app.services.product_service import ProductService

logger = get_logger(__name__)


async def list_products(
    db: DatabaseSession,
    pagination: Pagination,
    filters: ProductFilter = Depends()
) -> PaginatedResponse:
    """
    List active products with pagination and search.
    
    Args:
        db: Database session.
        pagination: Pagination parameters.
        filters: Product filtering parameters.
        
    Returns:
        PaginatedResponse: Paginated list of products.
    """
    logger.info(f"Listing products with filters: {filters}, page: {pagination.page}")
    
    try:
        from app.services.product_service import ProductService
        service = ProductService(db)
        return await service.list_products(pagination=pagination, search=filters.search)
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )


async def get_product(
    product_id: str,
    db: DatabaseSession
) -> ProductPublic:
    """
    Get product by ID.
    
    Args:
        product_id: Product ID.
        db: Database session.
        
    Returns:
        ProductPublic: Product details.
        
    Raises:
        HTTPException: If product not found.
    """
    # TODO: Implement with ProductService
    # service = ProductService(db)
    # return await service.get_product_by_id(product_id)
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get product endpoint not yet implemented"
    )


def get_product_by_slug(
    slug: str,
    db: DatabaseSession
) -> ProductDetail:
    """
    Get product by slug with detailed information.
    
    Args:
        slug: Product slug.
        db: Database session.
        
    Returns:
        ProductDetail: Detailed product information.
        
    Raises:
        HTTPException: If product not found.
    """
    try:
        logger.info(f"Getting product by slug: {slug}")
        
        service = ProductService(db)
        product = service.get_product_by_slug(slug)
        
        if not product:
            logger.warning(f"Product not found with slug: {slug}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with slug '{slug}' not found"
            )
        
        logger.info(f"Successfully retrieved product: {product.name}")
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product by slug {slug}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )


async def create_product(
    request: ProductCreate,
    admin_user_id: AdminUserId,
    db: DatabaseSession
) -> ProductPublic:
    """
    Create a new product (admin only).
    
    Args:
        request: Product creation data.
        admin_user_id: Admin user ID from JWT.
        db: Database session.
        
    Returns:
        ProductPublic: Created product.
        
    Raises:
        HTTPException: If creation fails.
    """
    # TODO: Implement with ProductService
    # service = ProductService(db)
    # return await service.create_product(request, created_by=admin_user_id)
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Create product endpoint not yet implemented"
    )


async def update_product(
    product_id: str,
    request: ProductUpdate,
    admin_user_id: AdminUserId,
    db: DatabaseSession
) -> ProductPublic:
    """
    Update a product (admin only).
    
    Args:
        product_id: Product ID to update.
        request: Product update data.
        admin_user_id: Admin user ID from JWT.
        db: Database session.
        
    Returns:
        ProductPublic: Updated product.
        
    Raises:
        HTTPException: If update fails.
    """
    # TODO: Implement with ProductService
    # service = ProductService(db)
    # return await service.update_product(product_id, request, updated_by=admin_user_id)
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update product endpoint not yet implemented"
    )


async def update_product_stock(
    product_id: str,
    request: StockUpdate,
    admin_user_id: AdminUserId,
    db: DatabaseSession
) -> ProductPublic:
    """
    Update product stock (admin only).
    
    Args:
        product_id: Product ID to update.
        request: Stock update data.
        admin_user_id: Admin user ID from JWT.
        db: Database session.
        
    Returns:
        ProductPublic: Updated product.
        
    Raises:
        HTTPException: If update fails.
    """
    # TODO: Implement with ProductService
    # service = ProductService(db)
    # return await service.update_stock(product_id, request, updated_by=admin_user_id)
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update product stock endpoint not yet implemented"
    )


async def delete_product(
    product_id: str,
    admin_user_id: AdminUserId,
    db: DatabaseSession
) -> SuccessResponse:
    """
    Delete/archive a product (admin only).
    
    Args:
        product_id: Product ID to delete.
        admin_user_id: Admin user ID from JWT.
        db: Database session.
        
    Returns:
        SuccessResponse: Deletion confirmation.
        
    Raises:
        HTTPException: If deletion fails.
    """
    # TODO: Implement with ProductService
    # service = ProductService(db)
    # await service.delete_product(product_id, deleted_by=admin_user_id)
    # return SuccessResponse(message="Product deleted successfully")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete product endpoint not yet implemented"
    )
