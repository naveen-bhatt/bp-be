"""Pagination utilities."""

from typing import List, TypeVar, Generic, Dict, Any
from math import ceil
from pydantic import BaseModel

T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    page: int
    per_page: int
    total: int
    pages: int
    has_prev: bool
    has_next: bool
    prev_page: int | None = None
    next_page: int | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    items: List[T]
    meta: PaginationMeta


def create_pagination_meta(
    page: int,
    per_page: int,
    total: int
) -> PaginationMeta:
    """
    Create pagination metadata.
    
    Args:
        page: Current page number (1-based).
        per_page: Number of items per page.
        total: Total number of items.
        
    Returns:
        PaginationMeta: Pagination metadata.
        
    Example:
        ```python
        meta = create_pagination_meta(1, 20, 150)
        # meta.pages = 8, meta.has_next = True, etc.
        ```
    """
    pages = ceil(total / per_page) if per_page > 0 else 0
    has_prev = page > 1
    has_next = page < pages
    
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        has_prev=has_prev,
        has_next=has_next,
        prev_page=page - 1 if has_prev else None,
        next_page=page + 1 if has_next else None
    )


def paginate_query_result(
    items: List[T],
    page: int,
    per_page: int,
    total: int
) -> PaginatedResponse[T]:
    """
    Create paginated response from query results.
    
    Args:
        items: List of items for current page.
        page: Current page number.
        per_page: Number of items per page.
        total: Total number of items.
        
    Returns:
        PaginatedResponse[T]: Paginated response with items and metadata.
        
    Example:
        ```python
        products, total = product_repo.list_active_products(skip=0, limit=20)
        response = paginate_query_result(products, 1, 20, total)
        ```
    """
    meta = create_pagination_meta(page, per_page, total)
    
    return PaginatedResponse(
        items=items,
        meta=meta
    )


def calculate_skip_limit(page: int, per_page: int) -> tuple[int, int]:
    """
    Calculate skip and limit values for database queries.
    
    Args:
        page: Page number (1-based).
        per_page: Number of items per page.
        
    Returns:
        tuple[int, int]: Tuple of (skip, limit) values.
        
    Example:
        ```python
        skip, limit = calculate_skip_limit(3, 20)  # skip=40, limit=20
        products = db.query(Product).offset(skip).limit(limit).all()
        ```
    """
    skip = (page - 1) * per_page
    return skip, per_page


def get_pagination_headers(meta: PaginationMeta) -> Dict[str, str]:
    """
    Generate HTTP headers for pagination.
    
    Args:
        meta: Pagination metadata.
        
    Returns:
        Dict[str, str]: HTTP headers for pagination.
        
    Example:
        ```python
        headers = get_pagination_headers(meta)
        # {"X-Total-Count": "150", "X-Page-Count": "8"}
        ```
    """
    return {
        "X-Total-Count": str(meta.total),
        "X-Page-Count": str(meta.pages),
        "X-Current-Page": str(meta.page),
        "X-Per-Page": str(meta.per_page)
    }