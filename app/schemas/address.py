"""Address schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from .common import BaseSchema, UUIDMixin, TimestampMixin
from ..models.address import AddressType


class Address(BaseModel):
    """Address schema for create and update operations."""
    id: Optional[str] = Field(None, description="Address ID")
    address_type: Optional[AddressType] = Field(None, description="Type of address (home, office, custom)")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name of the person")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name of the person")
    country: Optional[str] = Field(None, min_length=2, max_length=100, description="Country name")
    state: Optional[str] = Field(None, min_length=2, max_length=100, description="State/Province name")
    city: Optional[str] = Field(None, min_length=2, max_length=100, description="City name")
    pincode: Optional[str] = Field(None, min_length=3, max_length=20, description="Postal/ZIP code")
    street1: Optional[str] = Field(None, min_length=3, max_length=255, description="Primary street address")
    street2: Optional[str] = Field(None, max_length=255, description="Secondary street address")
    landmark: Optional[str] = Field(None, max_length=255, description="Nearby landmark")
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20, description="Contact phone number")
    whatsapp_opt_in: Optional[bool] = Field(None, description="Whether user opted in for WhatsApp notifications")
    address_hash: Optional[str] = Field(None, min_length=64, max_length=64, description="Hash of address data for duplicate detection")
    
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


class AddressListResponse(BaseModel):
    """Response schema for list of addresses."""
    
    items: List[Address] = Field(default_factory=list, description="List of addresses")
    count: int = Field(..., description="Total number of addresses")
