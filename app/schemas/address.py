"""Address schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from .common import BaseSchema, UUIDMixin, TimestampMixin


class AddressBase(BaseModel):
    """Base address schema."""
    
    pincode: str = Field(..., min_length=3, max_length=20, description="Postal/ZIP code")
    street1: str = Field(..., min_length=3, max_length=255, description="Primary street address")
    street2: Optional[str] = Field(None, max_length=255, description="Secondary street address")
    landmark: Optional[str] = Field(None, max_length=255, description="Nearby landmark")
    phone_number: str = Field(..., min_length=5, max_length=20, description="Contact phone number")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        # Remove any non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 5:
            raise ValueError('Phone number must have at least 5 digits')
        return v


class AddressCreate(AddressBase):
    """Address creation schema."""
    
    pass


class AddressUpdate(BaseModel):
    """Address update schema."""
    
    pincode: Optional[str] = Field(None, min_length=3, max_length=20, description="Postal/ZIP code")
    street1: Optional[str] = Field(None, min_length=3, max_length=255, description="Primary street address")
    street2: Optional[str] = Field(None, max_length=255, description="Secondary street address")
    landmark: Optional[str] = Field(None, max_length=255, description="Nearby landmark")
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20, description="Contact phone number")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
            
        # Remove any non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 5:
            raise ValueError('Phone number must have at least 5 digits')
        return v


class AddressPublic(BaseSchema, UUIDMixin, TimestampMixin):
    """Public address schema."""
    
    user_id: str = Field(..., description="User ID")
    pincode: str = Field(..., description="Postal/ZIP code")
    street1: str = Field(..., description="Primary street address")
    street2: Optional[str] = Field(None, description="Secondary street address")
    landmark: Optional[str] = Field(None, description="Nearby landmark")
    phone_number: str = Field(..., description="Contact phone number")


class AddressListResponse(BaseModel):
    """Response schema for list of addresses."""
    
    items: List[AddressPublic] = Field(default_factory=list, description="List of addresses")
    count: int = Field(..., description="Total number of addresses")
