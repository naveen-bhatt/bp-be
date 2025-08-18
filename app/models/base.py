"""Base SQLAlchemy models and mixins."""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr
import uuid

# Base class for all ORM models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class UUIDMixin:
    """Mixin to add UUID primary key to models."""
    
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model class with UUID primary key and timestamps.
    
    All models should inherit from this class to get:
    - UUID primary key
    - created_at timestamp
    - updated_at timestamp (auto-updated on modification)
    """
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case and pluralize
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Simple pluralization rules
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return name + 'es'
        else:
            return name + 's'
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            dict[str, Any]: Dictionary representation of the model.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"