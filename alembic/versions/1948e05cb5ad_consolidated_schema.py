"""consolidated_schema

Revision ID: 1948e05cb5ad
Revises: 
Create Date: 2025-08-13 23:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import mysql

# Import seed data from app.data
from app.data.seed_products import BLUE_PANSY_PRODUCTS


# revision identifiers, used by Alembic.
revision = '1948e05cb5ad'
down_revision = None
branch_labels = None
depends_on = None


def _seed_products() -> None:
    """Seed Blue Pansy perfume collection."""
    now = datetime.utcnow()
    
    # Insert products using bulk insert
    if BLUE_PANSY_PRODUCTS:
        insert_stmt = text("""
            INSERT INTO products (
                id, name, slug, description, main_image_url, slide_image_urls,
                price, currency, quantity, date_of_manufacture, expiry_duration_months,
                `rank_of_product`, is_active, brand, fragrance_family, concentration, volume_ml,
                gender, top_notes, middle_notes, base_notes, created_at, updated_at
            ) VALUES (
                :id, :name, :slug, :description, :main_image_url, :slide_image_urls,
                :price, :currency, :quantity, :date_of_manufacture, :expiry_duration_months,
                :rank_of_product, :is_active, :brand, :fragrance_family, :concentration, :volume_ml,
                :gender, :top_notes, :middle_notes, :base_notes, :created_at, :updated_at
            )
        """)
        
        # Execute each insert individually  
        for product in BLUE_PANSY_PRODUCTS:
            # Add UUID and timestamps
            product_data = product.copy()
            product_data['id'] = str(uuid.uuid4())
            product_data['created_at'] = now
            product_data['updated_at'] = now
            op.get_bind().execute(insert_stmt, product_data)


def upgrade() -> None:
    """Create all tables and seed initial data."""
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('user_type', sa.Enum('ANONYMOUS', 'REGISTERED', 'SOCIAL', name='usertype'), nullable=False, default='REGISTERED'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)

    # Create social_accounts table
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
    op.create_index('uq_social_provider_user', 'social_accounts', ['provider', 'provider_user_id'], unique=True)

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('main_image_url', sa.String(length=500), nullable=True),
        sa.Column('slide_image_urls', sa.JSON(), nullable=True),
        sa.Column('price', mysql.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('date_of_manufacture', sa.DateTime(), nullable=True),
        sa.Column('expiry_duration_months', sa.Integer(), nullable=True),
        sa.Column('rank_of_product', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.CHAR(36), nullable=True),
        sa.Column('updated_by', sa.CHAR(36), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('fragrance_family', sa.String(length=50), nullable=True),
        sa.Column('concentration', sa.String(length=20), nullable=True),
        sa.Column('volume_ml', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('top_notes', sa.JSON(), nullable=True),
        sa.Column('middle_notes', sa.JSON(), nullable=True),
        sa.Column('base_notes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    
    # Create indexes for products
    op.create_index('idx_product_active_name', 'products', ['is_active', 'name'], unique=False)
    op.create_index('idx_product_active_price', 'products', ['is_active', 'price'], unique=False)
    op.create_index('idx_product_quantity', 'products', ['quantity'], unique=False)
    op.create_index('idx_product_brand_gender', 'products', ['brand', 'gender'], unique=False)
    op.create_index('idx_product_fragrance_family', 'products', ['fragrance_family'], unique=False)
    op.create_index('idx_product_rank_active', 'products', ['rank_of_product', 'is_active'], unique=False)
    op.create_index('idx_product_manufacture_date', 'products', ['date_of_manufacture'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_index(op.f('ix_products_slug'), 'products', ['slug'], unique=True)
    op.create_index(op.f('ix_products_price'), 'products', ['price'], unique=False)
    op.create_index(op.f('ix_products_brand'), 'products', ['brand'], unique=False)
    op.create_index(op.f('ix_products_gender'), 'products', ['gender'], unique=False)
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'], unique=False)

    # Create carts table
    op.create_table('carts',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('product_id', sa.CHAR(36), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_cart_user_product', 'carts', ['user_id', 'product_id'], unique=True)
    op.create_index('idx_cart_user', 'carts', ['user_id'], unique=False)
    op.create_index('idx_cart_product', 'carts', ['product_id'], unique=False)

    # Create wishlist_items table
    op.create_table('wishlist_items',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('product_id', sa.CHAR(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_wishlist_user_product', 'wishlist_items', ['user_id', 'product_id'], unique=True)
    op.create_index('idx_wishlist_user', 'wishlist_items', ['user_id'], unique=False)
    op.create_index('idx_wishlist_product', 'wishlist_items', ['product_id'], unique=False)

    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=True),
        sa.Column('guest_email', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_amount', mysql.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('shipping_address', sa.JSON(), nullable=True),
        sa.Column('billing_address', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_order_user', 'orders', ['user_id'], unique=False)
    op.create_index('idx_order_status', 'orders', ['status'], unique=False)

    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('order_id', sa.CHAR(36), nullable=False),
        sa.Column('product_id', sa.CHAR(36), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', mysql.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('total_price', mysql.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_order_item_order', 'order_items', ['order_id'], unique=False)
    op.create_index('idx_order_item_product', 'order_items', ['product_id'], unique=False)

    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('order_id', sa.CHAR(36), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_payment_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('amount', mysql.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('provider_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payment_order', 'payments', ['order_id'], unique=False)
    op.create_index('idx_payment_status', 'payments', ['status'], unique=False)
    op.create_index('idx_payment_provider', 'payments', ['provider'], unique=False)
    
    # Seed initial Blue Pansy perfume products
    _seed_products()


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('wishlist_items')
    op.drop_table('carts')
    op.drop_table('products')
    op.drop_table('social_accounts')
    op.drop_table('users')
    
    # Drop enum type
    op.execute('DROP TYPE usertype')