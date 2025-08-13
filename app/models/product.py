"""Product model for perfume e-commerce."""

from decimal import Decimal
from typing import List
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, Index, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class Product(BaseModel):
    """
    Product model for perfume e-commerce catalog.
    
    Attributes:
        id: Unique identifier (UUID).
        name: Perfume name.
        slug: URL-friendly identifier (unique).
        description: Detailed product description.
        main_image_url: Main product image URL.
        slide_image_urls: Array of additional product image URLs.
        price: Product price (decimal with 2 decimal places).
        currency: Currency code (e.g., USD, EUR, INR).
        date_of_manufacture: Manufacturing date.
        expiry_duration_months: Duration in months before expiry.
        rank: Product ranking/priority for sorting.
        quantity: Available stock quantity.
        is_active: Whether the product is active and available for purchase.
        created_by: User ID who created the product.
        updated_by: User ID who last updated the product.
        created_at: Product creation timestamp (from BaseModel).
        updated_at: Last modification timestamp (from BaseModel).
        
        # Perfume-specific fields
        brand: Perfume brand name.
        fragrance_family: Type of fragrance (Oriental, Fresh, Floral, etc.).
        concentration: Perfume concentration (EDT, EDP, Parfum, etc.).
        volume_ml: Volume in milliliters.
        gender: Target gender (Men, Women, Unisex).
        top_notes: Top fragrance notes (JSON array).
        middle_notes: Middle/heart fragrance notes (JSON array).
        base_notes: Base fragrance notes (JSON array).
    """
    
    __tablename__ = "products"
    
    # Basic product information
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Images
    main_image_url = Column(String(500), nullable=True)
    slide_image_urls = Column(JSON, nullable=True, comment="Array of image URLs")
    
    # Pricing and inventory
    price = Column(DECIMAL(10, 2), nullable=False, index=True)
    currency = Column(String(3), default="USD", nullable=False)
    quantity = Column(Integer, default=0, nullable=False, index=True)
    
    # Product lifecycle
    date_of_manufacture = Column(DateTime, nullable=True)
    expiry_duration_months = Column(Integer, nullable=True, comment="Months until expiry")
    rank_of_product = Column(Integer, default=0, nullable=False, index=True, comment="For sorting/priority")
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Audit fields
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Perfume-specific fields
    brand = Column(String(100), nullable=True, index=True)
    fragrance_family = Column(String(50), nullable=True, index=True, 
                            comment="Oriental, Fresh, Floral, Woody, etc.")
    concentration = Column(String(20), nullable=True, 
                         comment="EDT, EDP, Parfum, Cologne, etc.")
    volume_ml = Column(Integer, nullable=True, comment="Volume in milliliters")
    gender = Column(String(10), nullable=True, index=True, 
                   comment="Men, Women, Unisex")
    
    # Fragrance notes (stored as JSON arrays)
    top_notes = Column(JSON, nullable=True, comment="Top fragrance notes")
    middle_notes = Column(JSON, nullable=True, comment="Middle/heart fragrance notes") 
    base_notes = Column(JSON, nullable=True, comment="Base fragrance notes")
    
    # Relationships
    carts = relationship("Cart", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_product_active_name", is_active, name),
        Index("idx_product_active_price", is_active, price),
        Index("idx_product_quantity", quantity),
        Index("idx_product_brand_gender", brand, gender),
        Index("idx_product_fragrance_family", fragrance_family),
        Index("idx_product_rank_active", rank_of_product, is_active),
        Index("idx_product_manufacture_date", date_of_manufacture),
    )
    
    def __repr__(self) -> str:
        """String representation of the product."""
        return f"<Product(id={self.id}, name={self.name}, brand={self.brand}, price={self.price})>"
    
    def is_available(self) -> bool:
        """Check if product is available for purchase."""
        return self.is_active and self.quantity > 0
    
    def can_fulfill_quantity(self, requested_quantity: int) -> bool:
        """
        Check if product has sufficient stock for the requested quantity.
        
        Args:
            requested_quantity: Requested quantity.
            
        Returns:
            bool: True if stock is sufficient, False otherwise.
        """
        return self.quantity >= requested_quantity
    
    def reserve_stock(self, requested_quantity: int) -> bool:
        """
        Reserve stock for an order (decrease stock).
        
        Args:
            requested_quantity: Quantity to reserve.
            
        Returns:
            bool: True if reservation successful, False if insufficient stock.
        """
        if not self.can_fulfill_quantity(requested_quantity):
            return False
        
        self.quantity -= requested_quantity
        return True
    
    def release_stock(self, released_quantity: int) -> None:
        """
        Release reserved stock (increase stock).
        
        Args:
            released_quantity: Quantity to release.
        """
        self.quantity += released_quantity
    
    @property
    def price_decimal(self) -> Decimal:
        """Get price as Decimal for precise calculations."""
        return Decimal(str(self.price))
    
    @property
    def expiry_date(self) -> datetime | None:
        """
        Calculate expiry date based on manufacture date and duration.
        
        Returns:
            datetime | None: Expiry date or None if manufacture date/duration not set.
        """
        if not self.date_of_manufacture or not self.expiry_duration_months:
            return None
        
        from dateutil.relativedelta import relativedelta
        return self.date_of_manufacture + relativedelta(months=self.expiry_duration_months)
    
    def is_expired(self) -> bool:
        """
        Check if product has expired.
        
        Returns:
            bool: True if expired, False otherwise.
        """
        expiry = self.expiry_date
        if not expiry:
            return False
        
        return datetime.utcnow() > expiry
    
    def days_until_expiry(self) -> int | None:
        """
        Calculate days until expiry.
        
        Returns:
            int | None: Days until expiry or None if expiry date not available.
        """
        expiry = self.expiry_date
        if not expiry:
            return None
        
        delta = expiry - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def all_fragrance_notes(self) -> List[str]:
        """
        Get all fragrance notes combined.
        
        Returns:
            List[str]: Combined list of all fragrance notes.
        """
        notes = []
        if self.top_notes:
            notes.extend(self.top_notes)
        if self.middle_notes:
            notes.extend(self.middle_notes)
        if self.base_notes:
            notes.extend(self.base_notes)
        return notes
    
    def has_note(self, note: str) -> bool:
        """
        Check if product contains a specific fragrance note.
        
        Args:
            note: Fragrance note to search for.
            
        Returns:
            bool: True if note is found, False otherwise.
        """
        note_lower = note.lower()
        return any(note_lower in n.lower() for n in self.all_fragrance_notes)
    
    @property
    def display_name(self) -> str:
        """
        Get formatted display name with brand.
        
        Returns:
            str: Formatted display name.
        """
        if self.brand:
            return f"{self.brand} - {self.name}"
        return self.name