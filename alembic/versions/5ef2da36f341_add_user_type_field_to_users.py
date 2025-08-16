"""add_user_type_field_to_users

Revision ID: 5ef2da36f341
Revises: ac23ec0fc384
Create Date: 2025-08-16 18:47:47.133656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ef2da36f341'
down_revision = 'ac23ec0fc384'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update existing user_type field to use new enum values."""
    # Update the existing user_type column to use new enum values
    # First, update existing values to match new enum
    op.execute("UPDATE users SET user_type = 'EMAIL' WHERE user_type = 'REGISTERED'")
    
    # Alter the column to use new enum values
    op.execute("ALTER TABLE users MODIFY COLUMN user_type ENUM('ANONYMOUS', 'SOCIAL', 'EMAIL', 'PHONE') NOT NULL DEFAULT 'ANONYMOUS'")
    
    # Create index on user_type for better query performance (if it doesn't exist)
    try:
        op.create_index('idx_user_type', 'users', ['user_type'])
    except:
        # Index might already exist
        pass


def downgrade() -> None:
    """Revert user_type field to old enum values."""
    # Revert to old enum values
    op.execute("UPDATE users SET user_type = 'REGISTERED' WHERE user_type = 'EMAIL'")
    
    # Alter the column back to old enum values
    op.execute("ALTER TABLE users MODIFY COLUMN user_type ENUM('ANONYMOUS', 'REGISTERED', 'SOCIAL') NOT NULL DEFAULT 'REGISTERED'")
    
    # Drop index if it exists
    try:
        op.drop_index('idx_user_type', table_name='users')
    except:
        # Index might not exist
        pass