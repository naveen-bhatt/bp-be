"""Validation utilities."""

import re
from typing import Optional
from decimal import Decimal, InvalidOperation


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate.
        
    Returns:
        bool: True if valid email format, False otherwise.
        
    Example:
        ```python
        is_valid = is_valid_email("user@example.com")  # True
        is_valid = is_valid_email("invalid-email")     # False
        ```
    """
    if not email or len(email) > 254:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate.
        min_length: Minimum password length.
        
    Returns:
        tuple[bool, Optional[str]]: Tuple of (is_valid, error_message).
        
    Example:
        ```python
        is_valid, error = is_valid_password("MyPassword123!")
        if not is_valid:
            print(error)
        ```
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    # Check for at least one letter and one number
    has_letter = re.search(r'[a-zA-Z]', password) is not None
    has_number = re.search(r'\d', password) is not None
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    if not has_number:
        return False, "Password must contain at least one number"
    
    return True, None


def is_valid_currency_code(currency: str) -> bool:
    """
    Validate ISO 4217 currency code.
    
    Args:
        currency: Currency code to validate.
        
    Returns:
        bool: True if valid currency code, False otherwise.
        
    Example:
        ```python
        is_valid = is_valid_currency_code("USD")  # True
        is_valid = is_valid_currency_code("XYZ")  # False
        ```
    """
    # Common currency codes
    valid_currencies = {
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD",
        "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", "INR", "BRL", "ZAR", "KRW"
    }
    
    return currency.upper() in valid_currencies


def is_valid_price(price: str | float | Decimal) -> tuple[bool, Optional[str]]:
    """
    Validate price value.
    
    Args:
        price: Price to validate.
        
    Returns:
        tuple[bool, Optional[str]]: Tuple of (is_valid, error_message).
        
    Example:
        ```python
        is_valid, error = is_valid_price("19.99")
        if not is_valid:
            print(error)
        ```
    """
    try:
        if isinstance(price, str):
            decimal_price = Decimal(price)
        elif isinstance(price, (int, float)):
            decimal_price = Decimal(str(price))
        elif isinstance(price, Decimal):
            decimal_price = price
        else:
            return False, "Invalid price format"
        
        if decimal_price < 0:
            return False, "Price cannot be negative"
        
        if decimal_price > Decimal('999999.99'):
            return False, "Price is too large"
        
        # Check decimal places (max 2)
        if decimal_price.as_tuple().exponent < -2:
            return False, "Price cannot have more than 2 decimal places"
        
        return True, None
        
    except (ValueError, InvalidOperation):
        return False, "Invalid price format"


def is_valid_quantity(quantity: int | str) -> tuple[bool, Optional[str]]:
    """
    Validate quantity value.
    
    Args:
        quantity: Quantity to validate.
        
    Returns:
        tuple[bool, Optional[str]]: Tuple of (is_valid, error_message).
        
    Example:
        ```python
        is_valid, error = is_valid_quantity(5)
        if not is_valid:
            print(error)
        ```
    """
    try:
        if isinstance(quantity, str):
            int_quantity = int(quantity)
        elif isinstance(quantity, int):
            int_quantity = quantity
        else:
            return False, "Invalid quantity format"
        
        if int_quantity < 0:
            return False, "Quantity cannot be negative"
        
        if int_quantity > 10000:
            return False, "Quantity is too large (max 10,000)"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid quantity format"


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input by removing dangerous characters.
    
    Args:
        text: Text to sanitize.
        max_length: Maximum length to truncate to.
        
    Returns:
        str: Sanitized text.
        
    Example:
        ```python
        clean_text = sanitize_string("<script>alert('xss')</script>")
        # "alert('xss')"
        ```
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def is_valid_slug(slug: str) -> bool:
    """
    Validate URL slug format.
    
    Args:
        slug: Slug to validate.
        
    Returns:
        bool: True if valid slug format, False otherwise.
        
    Example:
        ```python
        is_valid = is_valid_slug("my-product-name")  # True
        is_valid = is_valid_slug("My Product!")      # False
        ```
    """
    if not slug:
        return False
    
    # Slug should only contain lowercase letters, numbers, and hyphens
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return re.match(pattern, slug) is not None and len(slug) <= 100


def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate phone number format (basic validation).
    
    Args:
        phone: Phone number to validate.
        
    Returns:
        tuple[bool, Optional[str]]: Tuple of (is_valid, error_message).
        
    Example:
        ```python
        is_valid, error = validate_phone_number("+1-234-567-8900")
        ```
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check format
    if not re.match(r'^\+?[\d]{7,15}$', cleaned):
        return False, "Invalid phone number format"
    
    return True, None