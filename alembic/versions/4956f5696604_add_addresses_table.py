"""add_addresses_table

Revision ID: 4956f5696604
Revises: 1948e05cb5ad
Create Date: 2025-08-13 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '4956f5696604'
down_revision = '1948e05cb5ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add addresses table."""
    op.create_table('addresses',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('pincode', sa.String(length=20), nullable=False),
        sa.Column('street1', sa.String(length=255), nullable=False),
        sa.Column('street2', sa.String(length=255), nullable=True),
        sa.Column('landmark', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_address_user', 'addresses', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop addresses table."""
    op.drop_index('idx_address_user', table_name='addresses')
    op.drop_table('addresses')