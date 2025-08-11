"""Password hashing utilities."""

from passlib.context import CryptContext

# Initialize password context with bcrypt
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


def needs_update(hashed_password: str) -> bool:
    """
    Check if a hashed password needs to be rehashed (due to algorithm updates).
    
    Args:
        hashed_password: Previously hashed password.
        
    Returns:
        bool: True if password needs update, False otherwise.
        
    Example:
        ```python
        if needs_update(user.hashed_password):
            user.hashed_password = hash_password(plain_password)
        ```
    """
    return pwd_context.needs_update(hashed_password)