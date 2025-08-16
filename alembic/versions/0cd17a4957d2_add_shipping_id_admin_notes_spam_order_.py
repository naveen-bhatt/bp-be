"""add_shipping_id_admin_notes_spam_order_to_orders

Revision ID: 0cd17a4957d2
Revises: aca13565e8f0
Create Date: 2025-08-16 18:08:27.637891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cd17a4957d2'
down_revision = 'aca13565e8f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add shipping_id, admin_notes, and spam_order columns to orders table."""
    # Add shipping_id column
    op.add_column('orders', sa.Column('shipping_id', sa.String(255), nullable=True))
    
    # Add admin_notes column
    op.add_column('orders', sa.Column('admin_notes', sa.String(1000), nullable=True))
    
    # Add spam_order column with default value
    op.add_column('orders', sa.Column('spam_order', sa.Boolean(), nullable=False, server_default='0'))
    
    # Create index on shipping_id for better query performance
    op.create_index('idx_order_shipping_id', 'orders', ['shipping_id'])
    
    # Create index on spam_order for filtering suspicious orders
    op.create_index('idx_order_spam_order', 'orders', ['spam_order'])


def downgrade() -> None:
    """Remove shipping_id, admin_notes, and spam_order columns from orders table."""
    # Drop indexes
    op.drop_index('idx_order_spam_order', table_name='orders')
    op.drop_index('idx_order_shipping_id', table_name='orders')
    
    # Drop columns
    op.drop_column('orders', 'spam_order')
    op.drop_column('orders', 'admin_notes')
    op.drop_column('orders', 'shipping_id')