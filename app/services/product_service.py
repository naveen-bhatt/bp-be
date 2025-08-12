"""Product service for business logic."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductList, ProductDetail, UserInfo
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.core.dependencies import PaginationParams
from app.core.logging import get_logger
from app.models.product import Product

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
    
    def get_product_by_slug(self, slug: str) -> Optional[ProductDetail]:
        """
        Get detailed product information by slug.
        
        Args:
            slug: Product slug to search for.
            
        Returns:
            Optional[ProductDetail]: Detailed product information if found, None otherwise.
        """
        logger.info(f"Getting product by slug: {slug}")
        
        # Get product with user relationships from repository
        product = self.product_repo.get_by_slug(slug)
        
        if not product:
            logger.warning(f"Product not found with slug: {slug}")
            return None
        
        # Create detailed product response
        product_detail = ProductDetail(
            id=str(product.id),
            name=product.name,
            slug=product.slug,
            description=product.description,
            main_image_url=product.main_image_url,
            slide_image_urls=product.slide_image_urls or [],
            price=str(product.price),
            currency=product.currency,
            quantity=product.quantity,
            is_active=product.is_active,
            
            # Perfume-specific fields
            brand=product.brand,
            fragrance_family=product.fragrance_family,
            concentration=product.concentration,
            volume_ml=product.volume_ml,
            gender=product.gender,
            rank_of_product=product.rank_of_product,
            
            # Fragrance notes
            top_notes=product.top_notes or [],
            middle_notes=product.middle_notes or [],
            base_notes=product.base_notes or [],
            
            # Manufacturing and expiry information
            date_of_manufacture=product.date_of_manufacture.isoformat() if product.date_of_manufacture else None,
            expiry_duration_months=product.expiry_duration_months,
            
            # Computed fields
            is_available=product.is_available(),
            is_expired=product.is_expired(),
            days_until_expiry=product.days_until_expiry(),
            expiry_date=product.expiry_date.isoformat() if product.expiry_date else None,
            all_fragrance_notes=product.all_fragrance_notes,
        )
        
        logger.info(f"Retrieved product details for: {product.name}")
        return product_detail
