"""ID generation utilities."""

import uuid
import re
from typing import Optional


def generate_uuid() -> str:
    """
    Generate a new UUID4 string.
    
    Returns:
        str: UUID4 string.
        
    Example:
        ```python
        new_id = generate_uuid()
        # "550e8400-e29b-41d4-a716-446655440000"
        ```
    """
    return str(uuid.uuid4())


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate.
        
    Returns:
        bool: True if valid UUID, False otherwise.
        
    Example:
        ```python
        is_valid = is_valid_uuid("550e8400-e29b-41d4-a716-446655440000")  # True
        is_valid = is_valid_uuid("invalid-uuid")  # False
        ```
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text: Text to convert to slug.
        max_length: Maximum length of slug.
        
    Returns:
        str: URL-friendly slug.
        
    Example:
        ```python
        slug = generate_slug("My Awesome Product!")
        # "my-awesome-product"
        ```
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    # Ensure slug is not empty
    if not slug:
        slug = generate_uuid()[:8]
    
    return slug


def generate_unique_slug(base_text: str, existing_slugs: list[str], max_length: int = 50) -> str:
    """
    Generate a unique slug by appending numbers if necessary.
    
    Args:
        base_text: Base text to generate slug from.
        existing_slugs: List of existing slugs to avoid.
        max_length: Maximum length of slug.
        
    Returns:
        str: Unique URL-friendly slug.
        
    Example:
        ```python
        existing = ["my-product", "my-product-1"]
        slug = generate_unique_slug("My Product", existing)
        # "my-product-2"
        ```
    """
    base_slug = generate_slug(base_text, max_length)
    
    if base_slug not in existing_slugs:
        return base_slug
    
    # Try appending numbers
    counter = 1
    while True:
        # Calculate space for counter suffix
        suffix = f"-{counter}"
        available_length = max_length - len(suffix)
        
        if available_length > 0:
            candidate_slug = base_slug[:available_length] + suffix
        else:
            # If we can't fit the suffix, use a shorter base
            candidate_slug = base_slug[:max_length//2] + suffix
        
        if candidate_slug not in existing_slugs:
            return candidate_slug
        
        counter += 1
        
        # Safety break to avoid infinite loop
        if counter > 9999:
            return f"{generate_uuid()[:8]}"


def generate_cart_token() -> str:
    """
    Generate a cart token for guest carts.
    
    Returns:
        str: Cart token string.
        
    Example:
        ```python
        token = generate_cart_token()
        # "cart_550e8400e29b41d4a716446655440000"
        ```
    """
    return f"cart_{uuid.uuid4().hex}"


def generate_short_id(length: int = 8) -> str:
    """
    Generate a short alphanumeric ID.
    
    Args:
        length: Length of the ID.
        
    Returns:
        str: Short alphanumeric ID.
        
    Example:
        ```python
        short_id = generate_short_id(8)
        # "a1b2c3d4"
        ```
    """
    import secrets
    import string
    
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def mask_id(id_string: str, visible_chars: int = 4) -> str:
    """
    Mask an ID for logging or display purposes.
    
    Args:
        id_string: ID to mask.
        visible_chars: Number of characters to show at the end.
        
    Returns:
        str: Masked ID.
        
    Example:
        ```python
        masked = mask_id("550e8400-e29b-41d4-a716-446655440000", 4)
        # "****-****-****-****-********0000"
        ```
    """
    if len(id_string) <= visible_chars:
        return id_string
    
    masked_length = len(id_string) - visible_chars
    return '*' * masked_length + id_string[-visible_chars:]