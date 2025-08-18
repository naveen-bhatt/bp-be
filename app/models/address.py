"""Address model."""

from sqlalchemy import Column, String, ForeignKey, Index, Boolean, Enum, UniqueConstraint

from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class AddressType(enum.Enum):
    """Address type enumeration."""
    HOME = "home"
    OFFICE = "office"
    CUSTOM = "custom"


class Address(BaseModel):
    """
    Address model for storing user addresses.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model.
        address_type: Type of address (home, office, custom).
        first_name: First name of the person.
        last_name: Last name of the person.
        country: Country name.
        state: State/Province name.
        city: City name.
        pincode: Postal/ZIP code.
        street1: Primary street address.
        street2: Secondary street address (optional).
        landmark: Nearby landmark (optional).
        phone_number: Contact phone number.
        whatsapp_opt_in: Whether user opted in for WhatsApp notifications.
        address_hash: Hash of address data for duplicate detection.
        created_at: Address creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "addresses"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_type = Column(Enum(AddressType), nullable=False, default=AddressType.HOME)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    pincode = Column(String(20), nullable=False)
    street1 = Column(String(255), nullable=False)
    street2 = Column(String(255), nullable=True)
    landmark = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=False)
    whatsapp_opt_in = Column(Boolean, default=False, nullable=False)
    address_hash = Column(String(64), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_address_user", user_id),

        # Unique constraint on user_id + address_hash to prevent duplicate addresses
        UniqueConstraint(
        address_hash, user_id, address_type,
        name="uq_user_address"
    )
    )
    
    def __repr__(self) -> str:
        """String representation of the address."""
        return f"<Address(id={self.id}, user_id={self.user_id}, address_type={self.address_type}, pincode={self.pincode})>"
