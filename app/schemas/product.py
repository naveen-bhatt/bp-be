"""Product schemas."""

from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .common import BaseSchema, UUIDMixin, TimestampMixin


class ProductBase(BaseModel):
    """Base product schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    slug: str = Field(..., min_length=1, max_length=255, description="URL-friendly identifier")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    main_image_url: Optional[str] = Field(None, max_length=500, description="Main product image URL")
    slide_image_urls: Optional[List[str]] = Field(None, description="Slide image URLs array")
    price: str = Field(..., description="Product price as decimal string")
    currency: str = Field(default="USD", description="Currency code")
    quantity: int = Field(default=0, ge=0, description="Available stock quantity")
    date_of_manufacture: Optional[datetime] = Field(None, description="Date of manufacture")
    expiry_duration_months: Optional[int] = Field(None, description="Months until expiry")
    rank_of_product: int = Field(default=0, description="Product ranking for sorting")
    is_active: bool = Field(default=True, description="Whether product is active")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")
    fragrance_family: Optional[str] = Field(None, max_length=50, description="Fragrance family")
    concentration: Optional[str] = Field(None, max_length=20, description="Fragrance concentration")
    volume_ml: Optional[int] = Field(None, description="Volume in milliliters")
    gender: Optional[str] = Field(None, max_length=10, description="Target gender")
    top_notes: Optional[List[str]] = Field(None, description="Top fragrance notes")
    middle_notes: Optional[List[str]] = Field(None, description="Middle fragrance notes")
    base_notes: Optional[List[str]] = Field(None, description="Base fragrance notes")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: str) -> str:
        """Validate price format."""
        try:
            price_decimal = Decimal(v)
            if price_decimal < 0:
                raise ValueError('Price cannot be negative')
            if price_decimal > Decimal('999999.99'):
                raise ValueError('Price is too large')
            # Ensure max 2 decimal places
            if price_decimal.as_tuple().exponent < -2:
                raise ValueError('Price cannot have more than 2 decimal places')
            return str(price_decimal)
        except Exception:
            raise ValueError('Invalid price format')
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        valid_currencies = {
            "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", 
            "SEK", "NZD", "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", 
            "INR", "BRL", "ZAR", "KRW"
        }
        if v.upper() not in valid_currencies:
            raise ValueError(f'Invalid currency code: {v}')
        return v.upper()


class ProductCreate(ProductBase):
    """Product creation schema."""
    
    pass


class ProductUpdate(BaseModel):
    """Product update schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    slug: Optional[str] = Field(None, min_length=1, max_length=255, description="URL-friendly identifier")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    main_image_url: Optional[str] = Field(None, max_length=500, description="Main product image URL")
    slide_image_urls: Optional[List[str]] = Field(None, description="Slide image URLs array")
    price: Optional[str] = Field(None, description="Product price as decimal string")
    currency: Optional[str] = Field(None, description="Currency code")
    quantity: Optional[int] = Field(None, ge=0, description="Available stock quantity")
    date_of_manufacture: Optional[datetime] = Field(None, description="Date of manufacture")
    expiry_duration_months: Optional[int] = Field(None, description="Months until expiry")
    rank_of_product: Optional[int] = Field(None, description="Product ranking for sorting")
    is_active: Optional[bool] = Field(None, description="Whether product is active")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")
    fragrance_family: Optional[str] = Field(None, max_length=50, description="Fragrance family")
    concentration: Optional[str] = Field(None, max_length=20, description="Fragrance concentration")
    volume_ml: Optional[int] = Field(None, description="Volume in milliliters")
    gender: Optional[str] = Field(None, max_length=10, description="Target gender")
    top_notes: Optional[List[str]] = Field(None, description="Top fragrance notes")
    middle_notes: Optional[List[str]] = Field(None, description="Middle fragrance notes")
    base_notes: Optional[List[str]] = Field(None, description="Base fragrance notes")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[str]) -> Optional[str]:
        """Validate price format."""
        if v is None:
            return v
        
        try:
            price_decimal = Decimal(v)
            if price_decimal < 0:
                raise ValueError('Price cannot be negative')
            if price_decimal > Decimal('999999.99'):
                raise ValueError('Price is too large')
            # Ensure max 2 decimal places
            if price_decimal.as_tuple().exponent < -2:
                raise ValueError('Price cannot have more than 2 decimal places')
            return str(price_decimal)
        except Exception:
            raise ValueError('Invalid price format')
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code."""
        if v is None:
            return v
        
        valid_currencies = {
            "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", 
            "SEK", "NZD", "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", 
            "INR", "BRL", "ZAR", "KRW"
        }
        if v.upper() not in valid_currencies:
            raise ValueError(f'Invalid currency code: {v}')
        return v.upper()


class ProductPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public product schema."""
    
    name: str = Field(..., description="Product name")
    slug: str = Field(..., description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Product description")
    main_image_url: Optional[str] = Field(None, description="Main product image URL")
    slide_image_urls: Optional[List[str]] = Field(None, description="Slide image URLs array")
    price: str = Field(..., description="Product price as decimal string")
    currency: str = Field(..., description="Currency code")
    quantity: int = Field(..., description="Available stock quantity")
    date_of_manufacture: Optional[datetime] = Field(None, description="Date of manufacture")
    expiry_duration_months: Optional[int] = Field(None, description="Months until expiry")
    rank_of_product: int = Field(..., description="Product ranking for sorting")
    is_active: bool = Field(..., description="Whether product is active")
    brand: Optional[str] = Field(None, description="Product brand")
    fragrance_family: Optional[str] = Field(None, description="Fragrance family")
    concentration: Optional[str] = Field(None, description="Fragrance concentration")
    volume_ml: Optional[int] = Field(None, description="Volume in milliliters")
    gender: Optional[str] = Field(None, description="Target gender")
    top_notes: Optional[List[str]] = Field(None, description="Top fragrance notes")
    middle_notes: Optional[List[str]] = Field(None, description="Middle fragrance notes")
    base_notes: Optional[List[str]] = Field(None, description="Base fragrance notes")


class ProductAdmin(ProductPublic):
    """Admin product schema (includes all fields)."""
    
    pass


class ProductList(BaseModel):
    """Product list item schema."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    slug: str = Field(..., description="URL-friendly identifier")
    main_image_url: Optional[str] = Field(None, description="Main product image URL")
    price: str = Field(..., description="Product price as decimal string")
    currency: str = Field(..., description="Currency code")
    quantity: int = Field(..., description="Available stock quantity")
    brand: Optional[str] = Field(None, description="Product brand")
    fragrance_family: Optional[str] = Field(None, description="Fragrance family")
    concentration: Optional[str] = Field(None, description="Fragrance concentration")
    volume_ml: Optional[int] = Field(None, description="Volume in milliliters")
    gender: Optional[str] = Field(None, description="Target gender")
    rank_of_product: int = Field(..., description="Product ranking for sorting")
    is_active: bool = Field(..., description="Whether product is active")
    
    class Config:
        from_attributes = True


class ProductSearch(BaseModel):
    """Product search parameters."""
    
    search: Optional[str] = Field(None, description="Search term for name or description")
    min_price: Optional[str] = Field(None, description="Minimum price filter")
    max_price: Optional[str] = Field(None, description="Maximum price filter")
    currency: Optional[str] = Field(None, description="Currency filter")
    in_stock_only: bool = Field(default=False, description="Show only products in stock")
    
    @field_validator('min_price', 'max_price')
    @classmethod
    def validate_price_filters(cls, v: Optional[str]) -> Optional[str]:
        """Validate price filter format."""
        if v is None:
            return v
        
        try:
            price_decimal = Decimal(v)
            if price_decimal < 0:
                raise ValueError('Price cannot be negative')
            return str(price_decimal)
        except Exception:
            raise ValueError('Invalid price format')


class StockUpdate(BaseModel):
    """Stock update schema."""
    
    quantity: int = Field(..., ge=0, description="New stock quantity")
    operation: str = Field(default="set", description="Operation type: 'set', 'add', 'subtract'")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate operation type."""
        valid_operations = {'set', 'add', 'subtract'}
        if v not in valid_operations:
            raise ValueError(f'Operation must be one of: {", ".join(valid_operations)}')
        return v