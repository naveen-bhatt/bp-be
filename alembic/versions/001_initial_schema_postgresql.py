"""Initial schema for PostgreSQL

Revision ID: 001_initial_schema_postgresql
Revises: 
Create Date: 2025-08-18 19:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema_postgresql'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('display_picture', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('user_type', sa.Enum('ANONYMOUS', 'SOCIAL', 'EMAIL', 'PHONE', name='usertype'), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ADMIN', 'SUPERADMIN', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create social_accounts table
    op.create_table('social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_account_id', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create products table
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('main_image_url', sa.String(length=500), nullable=True),
        sa.Column('slide_image_urls', postgresql.JSON(), nullable=True),
        sa.Column('price', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('date_of_manufacture', sa.DateTime(), nullable=True),
        sa.Column('expiry_duration_months', sa.Integer(), nullable=True),
        sa.Column('rank_of_product', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('fragrance_family', sa.String(length=50), nullable=True),
        sa.Column('concentration', sa.String(length=20), nullable=True),
        sa.Column('volume_ml', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('top_notes', postgresql.JSON(), nullable=True),
        sa.Column('middle_notes', postgresql.JSON(), nullable=True),
        sa.Column('base_notes', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='uq_product_slug'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    
    # Create addresses table
    op.create_table('addresses',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('address_type', sa.Enum('home', 'office', 'custom', name='addresstype'), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('pincode', sa.String(length=20), nullable=False),
        sa.Column('street1', sa.String(length=255), nullable=False),
        sa.Column('street2', sa.String(length=255), nullable=True),
        sa.Column('landmark', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('whatsapp_opt_in', sa.Boolean(), nullable=False),
        sa.Column('address_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('address_hash', 'user_id', 'address_type', name='uq_user_address')
    )
    
    # Create carts table
    op.create_table('carts',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('cart_state', sa.Enum('ACTIVE', 'EXPIRED', name='cartstate'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'product_id', name='idx_cart_user_product')
    )
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('address_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('cart_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('shipping_id', sa.String(length=255), nullable=True),
        sa.Column('admin_notes', sa.String(length=1000), nullable=True),
        sa.Column('spam_order', sa.Boolean(), nullable=False),
        sa.Column('total_amount', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='SET NULL')
    )
    
    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE')
    )
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_payment_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('raw_payload', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE')
    )
    
    # Create wishlist_items table
    op.create_table('wishlist_items',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'product_id', name='idx_wishlist_user_product')
    )
    
    # Create indexes
    op.create_index('idx_user_email_active', 'users', ['email', 'is_active'])
    op.create_index('idx_user_role', 'users', ['role'])
    op.create_index('idx_user_display_picture', 'users', ['display_picture'])
    op.create_index('idx_user_phone', 'users', ['phone'])
    op.create_index('idx_user_type', 'users', ['user_type'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    op.create_index('idx_social_provider_account', 'social_accounts', ['provider', 'provider_account_id'], unique=True)
    op.create_index('idx_social_user_provider', 'social_accounts', ['user_id', 'provider'], unique=True)
    op.create_index('idx_social_accounts_user', 'social_accounts', ['user_id'])
    
    op.create_index('idx_product_active_name', 'products', ['is_active', 'name'])
    op.create_index('idx_product_active_price', 'products', ['is_active', 'price'])
    op.create_index('idx_product_quantity', 'products', ['quantity'])
    op.create_index('idx_product_brand_gender', 'products', ['brand', 'gender'])
    op.create_index('idx_product_fragrance_family', 'products', ['fragrance_family'])
    op.create_index('idx_product_rank_active', 'products', ['rank_of_product', 'is_active'])
    op.create_index('idx_product_manufacture_date', 'products', ['date_of_manufacture'])
    op.create_index('ix_products_brand', 'products', ['brand'])
    op.create_index('ix_products_fragrance_family', 'products', ['fragrance_family'])
    op.create_index('ix_products_gender', 'products', ['gender'])
    op.create_index('ix_products_is_active', 'products', ['is_active'])
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_price', 'products', ['price'])
    op.create_index('ix_products_quantity', 'products', ['quantity'])
    op.create_index('ix_products_rank_of_product', 'products', ['rank_of_product'])
    op.create_index('ix_products_slug', 'products', ['slug'], unique=True)
    
    op.create_index('idx_address_user', 'addresses', ['user_id'])
    
    op.create_index('idx_cart_user', 'carts', ['user_id'])
    op.create_index('idx_cart_product', 'carts', ['product_id'])
    op.create_index('idx_cart_state', 'carts', ['cart_state'])
    
    op.create_index('idx_order_user_status', 'orders', ['user_id', 'status'])
    op.create_index('idx_order_status_created', 'orders', ['status', 'created_at'])
    op.create_index('idx_order_address', 'orders', ['address_id'])
    op.create_index('idx_order_cart', 'orders', ['cart_id'])
    op.create_index('idx_order_shipping_id', 'orders', ['shipping_id'])
    op.create_index('idx_order_spam_order', 'orders', ['spam_order'])
    
    op.create_index('idx_order_item_order', 'order_items', ['order_id'])
    op.create_index('idx_order_item_product', 'order_items', ['product_id'])
    
    op.create_index('idx_payment_order', 'payments', ['order_id'])
    op.create_index('idx_payment_provider_id', 'payments', ['provider', 'provider_payment_id'])
    op.create_index('idx_payment_status', 'payments', ['status'])
    
    op.create_index('idx_wishlist_user', 'wishlist_items', ['user_id'])
    op.create_index('idx_wishlist_product', 'wishlist_items', ['product_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('wishlist_items')
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('carts')
    op.drop_table('addresses')
    op.drop_table('products')
    op.drop_table('social_accounts')
    op.drop_table('users')
