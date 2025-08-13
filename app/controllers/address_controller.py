"""Address controller."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import DatabaseSession, OptionalUserId
from app.schemas.address import (
    AddressCreate, AddressUpdate, AddressPublic, AddressListResponse
)
from app.schemas.common import SuccessResponse
from app.services.address_service import AddressService


def list_addresses(
    user_id: OptionalUserId,
    db: DatabaseSession
) -> AddressListResponse:
    """
    List all addresses for the current user.
    
    Args:
        user_id: User ID from JWT token.
        db: Database session.
        
    Returns:
        AddressListResponse: List of addresses.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access addresses"
            )
            
        address_service = AddressService(db)
        return address_service.list_addresses(user_id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list addresses: {str(e)}"
        )


def get_address(
    address_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> AddressPublic:
    """
    Get address by ID.
    
    Args:
        address_id: Address ID.
        user_id: User ID from JWT token.
        db: Database session.
        
    Returns:
        AddressPublic: Address details.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access address"
            )
            
        address_service = AddressService(db)
        return address_service.get_address(user_id=user_id, address_id=address_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get address: {str(e)}"
        )


def create_address(
    request: AddressCreate,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> AddressPublic:
    """
    Create a new address.
    
    Args:
        request: Address creation data.
        user_id: User ID from JWT token.
        db: Database session.
        
    Returns:
        AddressPublic: Created address.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to create address"
            )
            
        address_service = AddressService(db)
        return address_service.create_address(
            user_id=user_id,
            pincode=request.pincode,
            street1=request.street1,
            street2=request.street2,
            landmark=request.landmark,
            phone_number=request.phone_number
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create address: {str(e)}"
        )


def update_address(
    address_id: str,
    request: AddressUpdate,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> AddressPublic:
    """
    Update address.
    
    Args:
        address_id: Address ID.
        request: Address update data.
        user_id: User ID from JWT token.
        db: Database session.
        
    Returns:
        AddressPublic: Updated address.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to update address"
            )
            
        address_service = AddressService(db)
        return address_service.update_address(
            user_id=user_id,
            address_id=address_id,
            pincode=request.pincode,
            street1=request.street1,
            street2=request.street2,
            landmark=request.landmark,
            phone_number=request.phone_number
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update address: {str(e)}"
        )


def delete_address(
    address_id: str,
    user_id: OptionalUserId,
    db: DatabaseSession
) -> SuccessResponse:
    """
    Delete address.
    
    Args:
        address_id: Address ID.
        user_id: User ID from JWT token.
        db: Database session.
        
    Returns:
        SuccessResponse: Success message.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to delete address"
            )
            
        address_service = AddressService(db)
        address_service.delete_address(user_id=user_id, address_id=address_id)
        
        return SuccessResponse(message="Address deleted successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete address: {str(e)}"
        )
