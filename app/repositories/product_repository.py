"""Product repository for database operations."""

from typing import Optional, List, Tuple, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.product import Product
from app.core.errors import InsufficientStockError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductRepository:
    """Repository for Product model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
    
    def create(
        self,
        name: str,
        slug: str,
        price: Decimal,
        currency: str = "INR",
        description: Optional[str] = None,
        quantity: int = 0,
        is_active: bool = True
    ) -> Product:
        """
        Create a new product.
        
        Args:
            name: Product name.
            slug: URL-friendly identifier.
            price: Product price.
            currency: Currency code.
            description: Product description.
            quantity: Initial stock quantity.
            is_active: Whether product is active.
            
        Returns:
            Product: Created product instance.
        """
        product = Product(
            name=name,
            slug=slug,
            price=price,
            currency=currency,
            description=description,
            quantity=quantity,
            is_active=is_active
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Created product: {product.name} (slug: {product.slug})")
        return product
    
    def get_by_id(self, product_id: str) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            product_id: Product ID to search for.
            
        Returns:
            Optional[Product]: Product if found, None otherwise.
        """
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_by_slug(self, slug: str) -> Optional[Product]:
        """
        Get product by slug.
        
        Args:
            slug: Product slug to search for.
            
        Returns:
            Optional[Product]: Product if found, None otherwise.
        """
        return self.db.query(Product).filter(Product.slug == slug).first()
        
    def get_active_by_id(self, product_id: str) -> Optional[Product]:
        """
        Get active product by ID.
        
        Args:
            product_id: Product ID to search for.
            
        Returns:
            Optional[Product]: Active product if found, None otherwise.
        """
        return self.db.query(Product).filter(
            and_(Product.id == product_id, Product.is_active == True)
        ).first()
    
    def get_active_by_slug(self, slug: str) -> Optional[Product]:
        """
        Get active product by slug.
        
        Args:
            slug: Product slug to search for.
            
        Returns:
            Optional[Product]: Active product if found, None otherwise.
        """
        return self.db.query(Product).filter(
            and_(Product.slug == slug, Product.is_active == True)
        ).first()
    
    def list_active_products(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Tuple[List[Product], int]:
        """
        List active products with optional search and pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            search: Search term for name or description.
            
        Returns:
            Tuple[List[Product], int]: Tuple of (products, total_count).
        """
        query = self.db.query(Product).filter(Product.is_active == True)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        products = query.order_by(Product.rank_of_product, Product.name).offset(skip).limit(limit).all()
        
        return products, total_count
    
    def list_all_products(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> Tuple[List[Product], int]:
        """
        List all products with pagination (admin function).
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            active_only: Whether to return only active products.
            
        Returns:
            Tuple[List[Product], int]: Tuple of (products, total_count).
        """
        query = self.db.query(Product)
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        total_count = query.count()
        products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
        
        return products, total_count
    
    def update(self, product: Product, **kwargs) -> Product:
        """
        Update product attributes.
        
        Args:
            product: Product instance to update.
            **kwargs: Attributes to update.
            
        Returns:
            Product: Updated product instance.
        """
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Updated product: {product.name}")
        return product
    
    def update_stock(self, product: Product, new_quantity: int) -> Product:
        """
        Update product quantity.
        
        Args:
            product: Product instance to update.
            new_quantity: New stock quantity.
            
        Returns:
            Product: Updated product instance.
        """
        old_quantity = product.quantity
        product.quantity = new_quantity
        
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Updated quantity for {product.name}: {old_quantity} -> {new_quantity}")
        return product
    
    def decrement_stock(self, product_id: str, quantity: int) -> Product:
        """
        Decrement product quantity with optimistic locking check.
        
        Args:
            product_id: Product ID to update.
            quantity: Quantity to decrement.
            
        Returns:
            Product: Updated product instance.
            
        Raises:
            InsufficientStockError: If insufficient stock available.
        """
        # Get fresh product data
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Check stock availability
        if product.quantity < quantity:
            raise InsufficientStockError(
                product_name=product.name,
                requested=quantity,
                available=product.quantity
            )
        
        # Decrement stock
        product.quantity -= quantity
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Decremented quantity for {product.name}: -{quantity} (remaining: {product.quantity})")
        return product
    
    def increment_stock(self, product_id: str, quantity: int) -> Product:
        """
        Increment product quantity (e.g., for returns or restocking).
        
        Args:
            product_id: Product ID to update.
            quantity: Quantity to increment.
            
        Returns:
            Product: Updated product instance.
        """
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        product.quantity += quantity
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Incremented quantity for {product.name}: +{quantity} (total: {product.quantity})")
        return product
    
    def archive(self, product: Product) -> Product:
        """
        Archive a product (set as inactive).
        
        Args:
            product: Product instance to archive.
            
        Returns:
            Product: Updated product instance.
        """
        product.is_active = False
        self.db.commit()
        self.db.refresh(product)
        
        logger.info(f"Archived product: {product.name}")
        return product
    
    def delete(self, product: Product) -> None:
        """
        Delete a product (hard delete).
        
        Args:
            product: Product instance to delete.
        """
        self.db.delete(product)
        self.db.commit()
        
        logger.info(f"Deleted product: {product.name}")
    
    def exists_by_slug(self, slug: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if product exists by slug.
        
        Args:
            slug: Slug to check.
            exclude_id: Product ID to exclude from check (for updates).
            
        Returns:
            bool: True if product exists, False otherwise.
        """
        query = self.db.query(Product).filter(Product.slug == slug)
        
        if exclude_id:
            query = query.filter(Product.id != exclude_id)
        
        return query.first() is not None
        
    def to_list_schema(self, product: Product) -> Dict[str, Any]:
        """
        Convert Product model to dictionary for list display.
        
        Args:
            product: Product model instance.
            
        Returns:
            Dict[str, Any]: Dictionary with product data.
        """
        if not product:
            return None
            
        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "price": str(product.price),
            "currency": product.currency,
            "main_image_url": product.main_image_url,
            "quantity": product.quantity,
            "is_active": product.is_active,
            "brand": product.brand,
            "concentration": product.concentration,
            "volume_ml": product.volume_ml,
            "gender": product.gender,
            "rank_of_product": product.rank_of_product
        }