"""add_display_picture_to_users

Revision ID: 5c30e340509a
Revises: 0cd17a4957d2
Create Date: 2025-08-16 18:18:53.584842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c30e340509a'
down_revision = '0cd17a4957d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add display_picture column to users table."""
    # Add display_picture column for user profile pictures
    op.add_column('users', sa.Column('display_picture', sa.String(500), nullable=True))
    
    # Create index on display_picture for better query performance
    op.create_index('idx_user_display_picture', 'users', ['display_picture'])


def downgrade() -> None:
    """Remove display_picture column from users table."""
    # Drop index
    op.drop_index('idx_user_display_picture', table_name='users')
    
    # Drop column
    op.drop_column('users', 'display_picture')