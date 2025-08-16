"""add_user_role_field

Revision ID: aca13565e8f0
Revises: ecd4aceea683
Create Date: 2025-08-16 17:02:12.450595

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'aca13565e8f0'
down_revision = 'ecd4aceea683'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add role field to users table."""
    # Add role column with ENUM type - using uppercase values to match Python enum
    op.add_column('users', sa.Column('role', 
                                    mysql.ENUM('USER', 'ADMIN', 'SUPERADMIN', name='userrole'),
                                    nullable=False,
                                    server_default='USER'))
    
    # Create index on role for better query performance
    op.create_index('idx_user_role', 'users', ['role'])


def downgrade() -> None:
    """Remove role field from users table."""
    # Drop the index first
    op.drop_index('idx_user_role', 'users')
    
    # Drop the role column
    op.drop_column('users', 'role')