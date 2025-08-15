"""create_addresses_table_complete

Revision ID: create_addresses_table_complete
Revises: a7672856e3d4
Create Date: 2025-01-27 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'create_addresses_table_complete'
down_revision = 'a7672856e3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create addresses table with all fields and constraints."""
    op.create_table('addresses',
        # Primary key and timestamps
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # User relationship
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        
        # Address type and personal info
        sa.Column('address_type', sa.String(length=20), nullable=False, default='home'),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        
        # Location fields
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('pincode', sa.String(length=20), nullable=False),
        
        # Street address fields
        sa.Column('street1', sa.String(length=255), nullable=False),
        sa.Column('street2', sa.String(length=255), nullable=True),
        sa.Column('landmark', sa.String(length=255), nullable=True),
        
        # Contact and preferences
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('whatsapp_opt_in', sa.Boolean(), nullable=False, default=False),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        
        # Hash column for duplicate detection (will be unique per user)
        sa.Column('address_hash', sa.String(length=64), nullable=False),
        
        # Unique constraint on address_hash + user_id + address_type to prevent duplicate addresses
        sa.UniqueConstraint('address_hash', 'user_id', 'address_type', name='uq_user_address')
    )
    
    # Create index for better query performance
    op.create_index('idx_address_user', 'addresses', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop addresses table."""
    # Drop indexes first
    op.drop_index('idx_address_user', table_name='addresses')
    
    # Drop the table
    op.drop_table('addresses')
