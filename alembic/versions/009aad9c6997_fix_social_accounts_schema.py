"""fix_social_accounts_schema

Revision ID: 009aad9c6997
Revises: 1948e05cb5ad
Create Date: 2025-08-14 02:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '009aad9c6997'
down_revision = '1948e05cb5ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fix social_accounts table schema to match the model."""
    
    # Drop the old table and recreate it with correct schema
    op.drop_table('social_accounts')
    
    # Create social_accounts table with correct schema
    op.create_table('social_accounts',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_account_id', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_social_provider_account', 'social_accounts', ['provider', 'provider_account_id'], unique=True)
    op.create_index('idx_social_user_provider', 'social_accounts', ['user_id', 'provider'], unique=True)


def downgrade() -> None:
    """Revert social_accounts table to old schema."""
    
    # Drop the corrected table
    op.drop_table('social_accounts')
    
    # Recreate the old table structure
    op.create_table('social_accounts',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
        sa.Column('provider_email', sa.String(length=255), nullable=True),
        sa.Column('provider_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate old indexes
    op.create_index('uq_social_provider_user', 'social_accounts', ['provider', 'provider_user_id'], unique=True)