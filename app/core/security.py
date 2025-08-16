"""Security utilities for JWT tokens and password hashing."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash.
        
    Returns:
        str: Hashed password.
        
    Example:
        ```python
        hashed = hash_password("my_password")
        ```
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify.
        hashed_password: Previously hashed password.
        
    Returns:
        bool: True if password matches, False otherwise.
        
    Example:
        ```python
        is_valid = verify_password("my_password", stored_hash)
        ```
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token.
        
    Returns:
        str: Encoded JWT token.
        
    Example:
        ```python
        token = create_access_token({"sub": str(user.id), "email": user.email})
        ```
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_ttl_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Payload data to encode in the token.
        
    Returns:
        str: Encoded JWT refresh token.
        
    Example:
        ```python
        refresh_token = create_refresh_token({"sub": str(user.id)})
        ```
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_ttl_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify.
        token_type: Expected token type ("access" or "refresh").
        
    Returns:
        Optional[Dict[str, Any]]: Decoded payload if valid, None otherwise.
        
    Raises:
        HTTPException: If token is invalid or expired.
        
    Example:
        ```python
        payload = verify_token(token, "access")
        user_id = payload["sub"]
        ```
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_data: User data to encode in tokens.
        
    Returns:
        Dict[str, str]: Dictionary containing access_token and refresh_token.
        
    Example:
        ```python
        tokens = create_token_pair({"sub": str(user.id), "email": user.email})
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        ```
    """
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token({"sub": user_data["sub"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def create_enhanced_token_pair(user: Any) -> Dict[str, str]:
    """
    Create enhanced access and refresh tokens with user profile information.
    
    Args:
        user: User model instance with profile information.
        
    Returns:
        Dict[str, str]: Dictionary containing access_token and refresh_token.
        
    Example:
        ```python
        tokens = create_enhanced_token_pair(user)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        ```
    """
    # Create enhanced user data for access token
    user_data = {
        "sub": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_picture": user.display_picture,
        "phone": getattr(user, 'phone', None),  # Will be added in future migration
        "is_email_verified": user.email_verified,
        "user_type": _determine_user_type(user),
        "provider": _determine_provider(user)
    }
    
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token({"sub": user_data["sub"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def _determine_user_type(user: Any) -> str:
    """
    Get the user type from the database field.
    
    Args:
        user: User model instance.
        
    Returns:
        str: User type (ANONYMOUS, SOCIAL, EMAIL, PHONE).
    """
    return user.user_type.value if hasattr(user, 'user_type') and user.user_type else "ANONYMOUS"


def _determine_provider(user: Any) -> Optional[str]:
    """
    Get the OAuth provider from social accounts table.
    
    Args:
        user: User model instance.
        
    Returns:
        Optional[str]: Provider name or None if not social.
    """
    if _determine_user_type(user) == "SOCIAL":
        # Check social accounts to determine provider
        if hasattr(user, 'social_accounts') and user.social_accounts:
            return user.social_accounts[0].provider.value
    return None


def create_anonymous_token(user_id: str) -> Dict[str, Any]:
    """
    Create an access token for an anonymous user without expiration.
    
    Args:
        user_id: Anonymous user ID.
        
    Returns:
        Dict[str, Any]: Dictionary containing access token information.
        
    Example:
        ```python
        token_data = create_anonymous_token(str(anonymous_user.id))
        ```
    """
    # Create token payload without expiration for anonymous users
    to_encode = {
        "sub": user_id,
        "user_type": "anonymous",
        "email": None,
        "type": "access"
        # No "exp" field - token never expires
    }
    
    # Create token without expiration
    access_token = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.jwt_algorithm
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": None,  # No expiration
        "user_id": user_id,
        "user_type": "anonymous"
    }