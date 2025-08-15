"""Address service with business logic."""

import hashlib
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.address_repository import AddressRepository
from app.schemas.address import AddressListResponse, Address
from app.models.address import Address as AddressModel, AddressType


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
    
    def get_address(self, user_id: str, address_id: str) -> Address:
        """
        Get address by ID.
        
        Args:
            user_id: User ID.
            address_id: Address ID.
            
        Returns:
            Address: Address details.
            
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
    
    def create_address(self, user_id: str, address_data: Address) -> Address:
        """
        Create a new address.
        
        Args:
            user_id: User ID.
            address_data: Address creation data.
            
        Returns:
            Address: Created address.
            
        Raises:
            ValueError: If address already exists for the user.
        """
        # Generate address hash for duplicate detection
        address_hash = self._generate_address_hash(address_data)
        
        # Check if address already exists for this user
        existing_address = self.address_repo.get_by_user_and_hash(user_id, address_hash)
        if existing_address:
            raise ValueError("Address already exists for this user")
        
        # Create address with hash (ignore any provided id as database will generate it)
        address = self.address_repo.create(
            user_id=user_id,
            address_type=address_data.address_type or AddressType.HOME,
            first_name=address_data.first_name,
            last_name=address_data.last_name,
            country=address_data.country,
            state=address_data.state,
            city=address_data.city,
            pincode=address_data.pincode,
            street1=address_data.street1,
            street2=address_data.street2,
            landmark=address_data.landmark,
            phone_number=address_data.phone_number,
            whatsapp_opt_in=address_data.whatsapp_opt_in or False,
            address_hash=address_hash
        )
        
        return self._address_to_schema(address)
    
    def update_address(
        self,
        user_id: str,
        address_id: str,
        address_data: Address
    ) -> Address:
        """
        Update address.
        
        Args:
            user_id: User ID.
            address_id: Address ID.
            address_data: Address update data.
            
        Returns:
            Address: Updated address.
            
        Raises:
            ValueError: If address not found or doesn't belong to the user.
            ValueError: If updated address would create a duplicate.
        """
        address = self.address_repo.get_by_user_and_id(user_id, address_id)
        if not address:
            raise ValueError(f"Address not found or doesn't belong to the user: {address_id}")
        
        # Create a copy of current address data for hash comparison
        current_data = {
            'address_type': address.address_type,
            'first_name': address.first_name,
            'last_name': address.last_name,
            'country': address.country,
            'state': address.state,
            'city': address.city,
            'pincode': address.pincode,
            'street1': address.street1,
            'street2': address.street2,
            'landmark': address.landmark,
            'phone_number': address.phone_number,
            'whatsapp_opt_in': address.whatsapp_opt_in
        }
        
        # Update with new values
        updated_data = {**current_data}
        for field, value in address_data.dict(exclude_unset=True).items():
            if value is not None:
                updated_data[field] = value
        
        # Generate new hash for updated data
        new_hash = self._generate_address_hash_from_dict(updated_data)
        
        # Check if new address would create a duplicate (excluding current address)
        existing_address = self.address_repo.get_by_user_and_hash(user_id, new_hash)
        if existing_address and existing_address.id != address_id:
            raise ValueError("Updated address would create a duplicate")
        
        # Update address with new hash
        updated_address = self.address_repo.update(
            address=address,
            address_type=updated_data.get('address_type'),
            first_name=updated_data.get('first_name'),
            last_name=updated_data.get('last_name'),
            country=updated_data.get('country'),
            state=updated_data.get('state'),
            city=updated_data.get('city'),
            pincode=updated_data.get('pincode'),
            street1=updated_data.get('street1'),
            street2=updated_data.get('street2'),
            landmark=updated_data.get('landmark'),
            phone_number=updated_data.get('phone_number'),
            whatsapp_opt_in=updated_data.get('whatsapp_opt_in'),
            address_hash=new_hash
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
    
    def _generate_address_hash(self, address_data: Address) -> str:
        """
        Generate hash for address data to detect duplicates.
        
        Args:
            address_data: Address data.
            
        Returns:
            str: SHA-256 hash of address data.
        """
        # Concatenate all input fields in a specific order for consistent hashing
        # Convert to lowercase and strip whitespace for normalization
        first_name = (address_data.first_name or '').lower().strip()
        last_name = (address_data.last_name or '').lower().strip()
        country = (address_data.country or '').lower().strip()
        state = (address_data.state or '').lower().strip()
        city = (address_data.city or '').lower().strip()
        pincode = (address_data.pincode or '').strip()
        street1 = (address_data.street1 or '').lower().strip()
        street2 = (address_data.street2 or '').lower().strip()
        landmark = (address_data.landmark or '').lower().strip()
        phone_number = (address_data.phone_number or '').strip()
        whatsapp_opt_in = str(address_data.whatsapp_opt_in or False).lower()
        address_type = (address_data.address_type or AddressType.HOME).value.lower()
        
        # Concatenate all fields with a separator
        concatenated_string = f"{first_name}|{last_name}|{country}|{state}|{city}|{pincode}|{street1}|{street2}|{landmark}|{phone_number}|{whatsapp_opt_in}|{address_type}"
        
        # Generate SHA-256 hash of the concatenated string
        return hashlib.sha256(concatenated_string.encode('utf-8')).hexdigest()
    
    def _generate_address_hash_from_dict(self, address_data: Dict[str, Any]) -> str:
        """
        Generate hash for address data from dictionary.
        
        Args:
            address_data: Address data dictionary.
            
        Returns:
            str: SHA-256 hash of address data.
        """
        # Concatenate all input fields in a specific order for consistent hashing
        # Convert to lowercase and strip whitespace for normalization
        first_name = str(address_data.get('first_name', '')).lower().strip()
        last_name = str(address_data.get('last_name', '')).lower().strip()
        country = str(address_data.get('country', '')).lower().strip()
        state = str(address_data.get('state', '')).lower().strip()
        city = str(address_data.get('city', '')).lower().strip()
        pincode = str(address_data.get('pincode', '')).strip()
        street1 = str(address_data.get('street1', '')).lower().strip()
        street2 = str(address_data.get('street2', '')).lower().strip()
        landmark = str(address_data.get('landmark', '')).lower().strip()
        phone_number = str(address_data.get('phone_number', '')).strip()
        whatsapp_opt_in = str(address_data.get('whatsapp_opt_in', False)).lower()
        address_type = str(address_data.get('address_type', 'home')).lower()
        
        # Concatenate all fields with a separator
        concatenated_string = f"{first_name}|{last_name}|{country}|{state}|{city}|{pincode}|{street1}|{street2}|{landmark}|{phone_number}|{whatsapp_opt_in}|{address_type}"
        
        # Generate SHA-256 hash of the concatenated string
        return hashlib.sha256(concatenated_string.encode('utf-8')).hexdigest()
    
    def _address_to_schema(self, address: AddressModel) -> Address:
        """
        Convert Address model to Address schema.
        
        Args:
            address: Address model instance.
            
        Returns:
            Address: Address schema.
        """
        return Address(
            id=address.id,
            address_type=address.address_type,
            first_name=address.first_name,
            last_name=address.last_name,
            country=address.country,
            state=address.state,
            city=address.city,
            pincode=address.pincode,
            street1=address.street1,
            street2=address.street2,
            landmark=address.landmark,
            phone_number=address.phone_number,
            whatsapp_opt_in=address.whatsapp_opt_in,
            address_hash=address.address_hash
        )
