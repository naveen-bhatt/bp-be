"""Address service with business logic."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.address_repository import AddressRepository
from app.schemas.address import AddressPublic, AddressListResponse
from app.models.address import Address


class AddressService:
    """Service for address operations."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.address_repo = AddressRepository(db)
    
    def get_address(self, user_id: str, address_id: str) -> AddressPublic:
        """
        Get address by ID.
        
        Args:
            user_id: User ID.
            address_id: Address ID.
            
        Returns:
            AddressPublic: Address details.
            
        Raises:
            ValueError: If address not found or doesn't belong to the user.
        """
        address = self.address_repo.get_by_user_and_id(user_id, address_id)
        if not address:
            raise ValueError(f"Address not found or doesn't belong to the user: {address_id}")
        
        return self._address_to_schema(address)
    
    def list_addresses(self, user_id: str) -> AddressListResponse:
        """
        List all addresses for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            AddressListResponse: List of addresses.
        """
        addresses = self.address_repo.list_by_user_id(user_id)
        count = len(addresses)
        
        return AddressListResponse(
            items=[self._address_to_schema(address) for address in addresses],
            count=count
        )
    
    def create_address(
        self,
        user_id: str,
        pincode: str,
        street1: str,
        street2: Optional[str] = None,
        landmark: Optional[str] = None,
        phone_number: str = None
    ) -> AddressPublic:
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
            AddressPublic: Created address.
        """
        address = self.address_repo.create(
            user_id=user_id,
            pincode=pincode,
            street1=street1,
            street2=street2,
            landmark=landmark,
            phone_number=phone_number
        )
        
        return self._address_to_schema(address)
    
    def update_address(
        self,
        user_id: str,
        address_id: str,
        pincode: Optional[str] = None,
        street1: Optional[str] = None,
        street2: Optional[str] = None,
        landmark: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> AddressPublic:
        """
        Update address.
        
        Args:
            user_id: User ID.
            address_id: Address ID.
            pincode: New postal/ZIP code.
            street1: New primary street address.
            street2: New secondary street address.
            landmark: New nearby landmark.
            phone_number: New contact phone number.
            
        Returns:
            AddressPublic: Updated address.
            
        Raises:
            ValueError: If address not found or doesn't belong to the user.
        """
        address = self.address_repo.get_by_user_and_id(user_id, address_id)
        if not address:
            raise ValueError(f"Address not found or doesn't belong to the user: {address_id}")
        
        updated_address = self.address_repo.update(
            address=address,
            pincode=pincode,
            street1=street1,
            street2=street2,
            landmark=landmark,
            phone_number=phone_number
        )
        
        return self._address_to_schema(updated_address)
    
    def delete_address(self, user_id: str, address_id: str) -> None:
        """
        Delete address.
        
        Args:
            user_id: User ID.
            address_id: Address ID.
            
        Raises:
            ValueError: If address not found or doesn't belong to the user.
        """
        address = self.address_repo.get_by_user_and_id(user_id, address_id)
        if not address:
            raise ValueError(f"Address not found or doesn't belong to the user: {address_id}")
        
        self.address_repo.delete(address)
    
    def _address_to_schema(self, address: Address) -> AddressPublic:
        """
        Convert Address model to AddressPublic schema.
        
        Args:
            address: Address model instance.
            
        Returns:
            AddressPublic: Address schema.
        """
        return AddressPublic(
            id=address.id,
            user_id=address.user_id,
            pincode=address.pincode,
            street1=address.street1,
            street2=address.street2,
            landmark=address.landmark,
            phone_number=address.phone_number,
            created_at=address.created_at,
            updated_at=address.updated_at
        )
