"""add_cart_state_field

Revision ID: e1277fdd82fa
Revises: create_addresses_table_complete
Create Date: 2025-08-16 15:02:44.920843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1277fdd82fa'
down_revision = 'create_addresses_table_complete'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add cart_state column to carts table."""
    # Add cart_state column with enum names (not values)
    op.add_column('carts', sa.Column('cart_state', 
                                    sa.Enum('ACTIVE', 'EXPIRED', name='cartstate'),
                                    nullable=False,
                                    server_default='ACTIVE'))
    
    # Add index on cart_state for better query performance
    op.create_index('idx_cart_state', 'carts', ['cart_state'])


def downgrade() -> None:
    """Remove cart_state column from carts table."""
    # Drop the index first
    op.drop_index('idx_cart_state', 'carts')
    
    # Drop the cart_state column
    op.drop_column('carts', 'cart_state')