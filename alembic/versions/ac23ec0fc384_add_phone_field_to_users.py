"""add_phone_field_to_users

Revision ID: ac23ec0fc384
Revises: 5c30e340509a
Create Date: 2025-08-16 18:42:57.997852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac23ec0fc384'
down_revision = '5c30e340509a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add phone field to users table."""
    # Add phone column for user phone numbers
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # Create index on phone for better query performance
    op.create_index('idx_user_phone', 'users', ['phone'])


def downgrade() -> None:
    """Remove phone field from users table."""
    # Drop index
    op.drop_index('idx_user_phone', table_name='users')
    
    # Drop column
    op.drop_column('users', 'phone')