"""Address model."""

from sqlalchemy import Column, String, ForeignKey, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class Address(BaseModel):
    """
    Address model for storing user addresses.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to User model.
        pincode: Postal/ZIP code.
        street1: Primary street address.
        street2: Secondary street address (optional).
        landmark: Nearby landmark (optional).
        phone_number: Contact phone number.
        created_at: Address creation timestamp.
        updated_at: Last modification timestamp.
    """
    
    __tablename__ = "addresses"
    
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pincode = Column(String(20), nullable=False)
    street1 = Column(String(255), nullable=False)
    street2 = Column(String(255), nullable=True)
    landmark = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_address_user", user_id),
    )
    
    def __repr__(self) -> str:
        """String representation of the address."""
        return f"<Address(id={self.id}, user_id={self.user_id}, pincode={self.pincode})>"
