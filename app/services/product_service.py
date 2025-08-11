"""Product service for business logic."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductList
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.core.dependencies import PaginationParams
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductService:
    """Service for product business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
        self.product_repo = ProductRepository(db)
    
    async def list_products(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None
    ) -> PaginatedResponse:
        """
        List active products with pagination and search.
        
        Args:
            pagination: Pagination parameters.
            search: Optional search term.
            
        Returns:
            PaginatedResponse: Paginated list of products.
        """
        logger.info(f"Listing products - page: {pagination.page}, per_page: {pagination.per_page}, search: {search}")
        
        # Get products from repository
        products, total_count = self.product_repo.list_active_products(
            skip=pagination.offset,
            limit=pagination.per_page,
            search=search
        )
        
        # Convert to list schema
        product_items = [
            ProductList(
                id=product.id,
                name=product.name,
                slug=product.slug,
                main_image_url=product.main_image_url,
                price=str(product.price),
                currency=product.currency,
                quantity=product.quantity,
                brand=product.brand,
                fragrance_family=product.fragrance_family,
                concentration=product.concentration,
                volume_ml=product.volume_ml,
                gender=product.gender,
                rank_of_product=product.rank_of_product,
                is_active=product.is_active
            )
            for product in products
        ]
        
        # Calculate pagination metadata
        total_pages = (total_count + pagination.per_page - 1) // pagination.per_page
        
        meta = PaginationMeta(
            page=pagination.page,
            per_page=pagination.per_page,
            total=total_count,
            pages=total_pages,
            has_prev=pagination.page > 1,
            has_next=pagination.page < total_pages,
            prev_page=pagination.page - 1 if pagination.page > 1 else None,
            next_page=pagination.page + 1 if pagination.page < total_pages else None
        )
        
        logger.info(f"Retrieved {len(product_items)} products (total: {total_count})")
        
        return PaginatedResponse(
            items=product_items,
            meta=meta
        )
