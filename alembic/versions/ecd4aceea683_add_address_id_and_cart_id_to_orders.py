"""add_address_id_and_cart_id_to_orders

Revision ID: ecd4aceea683
Revises: e1277fdd82fa
Create Date: 2025-08-16 16:11:51.834349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecd4aceea683'
down_revision = 'e1277fdd82fa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add address_id column with foreign key constraint
    op.add_column('orders', sa.Column('address_id', sa.CHAR(36), nullable=True))
    op.create_foreign_key(
        'fk_order_address_id', 'orders', 'addresses',
        ['address_id'], ['id'], ondelete='SET NULL'
    )
    
    # Add cart_id column
    op.add_column('orders', sa.Column('cart_id', sa.CHAR(36), nullable=True))
    
    # Create indexes for new columns
    op.create_index('idx_order_address', 'orders', ['address_id'])
    op.create_index('idx_order_cart', 'orders', ['cart_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_order_address', table_name='orders')
    op.drop_index('idx_order_cart', table_name='orders')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_order_address_id', 'orders', type_='foreignkey')
    
    # Drop columns
    op.drop_column('orders', 'cart_id')
    op.drop_column('orders', 'address_id')