"""Address repository for database operations."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address


class AddressRepository:
    """Repository for address operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
    
    def get_by_id(self, address_id: str) -> Optional[Address]:
        """
        Get address by ID.
        
        Args:
            address_id: Address ID.
            
        Returns:
            Optional[Address]: Address if found, None otherwise.
        """
        stmt = select(Address).where(Address.id == address_id)
        return self.db.execute(stmt).scalars().first()
    
    def get_by_user_and_id(self, user_id: str, address_id: str) -> Optional[Address]:
        """
        Get address by user ID and address ID.
        
        Args:
            user_id: User ID.
            address_id: Address ID.
            
        Returns:
            Optional[Address]: Address if found, None otherwise.
        """
        stmt = select(Address).where(
            Address.user_id == user_id,
            Address.id == address_id
        )
        return self.db.execute(stmt).scalars().first()
    
    def list_by_user_id(self, user_id: str) -> List[Address]:
        """
        Get all addresses for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List[Address]: List of addresses.
        """
        stmt = select(Address).where(Address.user_id == user_id)
        return list(self.db.execute(stmt).scalars().all())
    
    def create(
        self,
        user_id: str,
        pincode: str,
        street1: str,
        street2: Optional[str] = None,
        landmark: Optional[str] = None,
        phone_number: str = None
    ) -> Address:
        """
        Create a new address.
        
        Args:
            user_id: User ID.
            pincode: Postal/ZIP code.
            street1: Primary street address.
            street2: Secondary street address.
            landmark: Nearby landmark.
            phone_number: Contact phone number.
            
        Returns:
            Address: Created address.
        """
        address = Address(
            user_id=user_id,
            pincode=pincode,
            street1=street1,
            street2=street2,
            landmark=landmark,
            phone_number=phone_number
        )
        
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        
        return address
    
    def update(
        self,
        address: Address,
        pincode: Optional[str] = None,
        street1: Optional[str] = None,
        street2: Optional[str] = None,
        landmark: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> Address:
        """
        Update address.
        
        Args:
            address: Address to update.
            pincode: New postal/ZIP code.
            street1: New primary street address.
            street2: New secondary street address.
            landmark: New nearby landmark.
            phone_number: New contact phone number.
            
        Returns:
            Address: Updated address.
        """
        if pincode is not None:
            address.pincode = pincode
        
        if street1 is not None:
            address.street1 = street1
        
        if street2 is not None:
            address.street2 = street2
        
        if landmark is not None:
            address.landmark = landmark
        
        if phone_number is not None:
            address.phone_number = phone_number
        
        self.db.commit()
        self.db.refresh(address)
        
        return address
    
    def delete(self, address: Address) -> None:
        """
        Delete address.
        
        Args:
            address: Address to delete.
        """
        self.db.delete(address)
        self.db.commit()
    
    def count_by_user_id(self, user_id: str) -> int:
        """
        Count addresses for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            int: Number of addresses.
        """
        stmt = select(Address).where(Address.user_id == user_id)
        return len(list(self.db.execute(stmt).scalars().all()))
