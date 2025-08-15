"""Address repository for database operations."""

from datetime import UTC, datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address, AddressType


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
    
    def get_by_user_and_hash(self, user_id: str, address_hash: str) -> Optional[Address]:
        """
        Get address by user ID and address hash for duplicate detection.
        
        Args:
            user_id: User ID.
            address_hash: Address hash.
            
        Returns:
            Optional[Address]: Address if found, None otherwise.
        """
        stmt = select(Address).where(
            Address.user_id == user_id,
            Address.address_hash == address_hash
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
        address_type: AddressType,
        first_name: str,
        last_name: str,
        country: str,
        state: str,
        city: str,
        pincode: str,
        street1: str,
        street2: Optional[str] = None,
        landmark: Optional[str] = None,
        phone_number: str = None,
        whatsapp_opt_in: bool = False,
        address_hash: str = None
    ) -> Address:
        """
        Create a new address.
        
        Args:
            user_id: User ID.
            address_type: Type of address (home, office, custom).
            first_name: First name of the person.
            last_name: Last name of the person.
            country: Country name.
            state: State/Province name.
            city: City name.
            pincode: Postal/ZIP code.
            street1: Primary street address.
            street2: Secondary street address.
            landmark: Nearby landmark.
            phone_number: Contact phone number.
            whatsapp_opt_in: Whether user opted in for WhatsApp notifications.
            address_hash: Hash of address data for duplicate detection.
            
        Returns:
            Address: Created address.
        """
        address = Address(
            user_id=user_id,
            address_type=address_type,
            first_name=first_name,
            last_name=last_name,
            country=country,
            state=state,
            city=city,
            pincode=pincode,
            street1=street1,
            street2=street2,
            landmark=landmark,
            phone_number=phone_number,
            whatsapp_opt_in=whatsapp_opt_in,
            address_hash=address_hash,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        
        return address
    
    def update(
        self,
        address: Address,
        address_type: Optional[AddressType] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        pincode: Optional[str] = None,
        street1: Optional[str] = None,
        street2: Optional[str] = None,
        landmark: Optional[str] = None,
        phone_number: Optional[str] = None,
        whatsapp_opt_in: Optional[bool] = None,
        address_hash: Optional[str] = None
    ) -> Address:
        """
        Update address.
        
        Args:
            address: Address to update.
            address_type: New address type.
            first_name: New first name.
            last_name: New last name.
            country: New country.
            state: New state.
            city: New city.
            pincode: New postal/ZIP code.
            street1: New primary street address.
            street2: New secondary street address.
            landmark: New nearby landmark.
            phone_number: New contact phone number.
            whatsapp_opt_in: New WhatsApp opt-in preference.
            address_hash: New address hash.
            
        Returns:
            Address: Updated address.
        """
        if address_type is not None:
            address.address_type = address_type
        
        if first_name is not None:
            address.first_name = first_name
        
        if last_name is not None:
            address.last_name = last_name
        
        if country is not None:
            address.country = country
        
        if state is not None:
            address.state = state
        
        if city is not None:
            address.city = city
        
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
        
        if whatsapp_opt_in is not None:
            address.whatsapp_opt_in = whatsapp_opt_in
        
        if address_hash is not None:
            address.address_hash = address_hash
        
        address.updated_at = datetime.now(UTC)
        
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
