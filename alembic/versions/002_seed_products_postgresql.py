"""Seed products data for PostgreSQL

Revision ID: 002_seed_products_postgresql
Revises: 001_initial_schema_postgresql
Create Date: 2025-08-18 19:35:00

This revision seeds the products table with the Blue Pansy collection.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import json
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_seed_products_postgresql'
down_revision = '001_initial_schema_postgresql'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # Import seed data from app module
    try:
        from app.data.seed_products import BLUE_PANSY_PRODUCTS
    except Exception as import_error:
        # If import fails (e.g., PYTHONPATH issues), do nothing rather than fail the whole migration
        # to keep schema migrations resilient. You can re-run seeding later once environment is correct.
        print(f"Skipping product seeding due to import error: {import_error}")
        return

    insert_sql = text(
        """
        INSERT INTO products (
            id, name, slug, description, main_image_url, slide_image_urls,
            price, currency, quantity, date_of_manufacture, expiry_duration_months,
            rank_of_product, is_active, brand, fragrance_family, concentration,
            volume_ml, gender, top_notes, middle_notes, base_notes, created_at, updated_at
        ) VALUES (
            :id, :name, :slug, :description, :main_image_url, :slide_image_urls,
            :price, :currency, :quantity, :date_of_manufacture, :expiry_duration_months,
            :rank_of_product, :is_active, :brand, :fragrance_family, :concentration,
            :volume_ml, :gender, :top_notes, :middle_notes, :base_notes, :created_at, :updated_at
        )
        """
    )

    # Best-effort insert; if slugs exist, skip duplicates
    check_sql = text("SELECT 1 FROM products WHERE slug = :slug LIMIT 1")

    for product in BLUE_PANSY_PRODUCTS:
        # Keep JSON columns as strings (PostgreSQL will parse them)
        # Don't parse with json.loads() as it converts to Python lists
        slide_image_urls = product.get('slide_image_urls')
        top_notes = product.get('top_notes')
        middle_notes = product.get('middle_notes')
        base_notes = product.get('base_notes')

        exists = bind.execute(check_sql, {"slug": product['slug']}).fetchone()
        if exists:
            continue

        bind.execute(
            insert_sql,
            {
                'id': str(uuid.uuid4()),
                'name': product['name'],
                'slug': product['slug'],
                'description': product.get('description'),
                'main_image_url': product.get('main_image_url'),
                'slide_image_urls': slide_image_urls,
                'price': product['price'],
                'currency': product['currency'],
                'quantity': product['quantity'],
                'date_of_manufacture': product.get('date_of_manufacture'),
                'expiry_duration_months': product.get('expiry_duration_months'),
                'rank_of_product': product['rank_of_product'],
                'is_active': product['is_active'],
                'brand': product.get('brand'),
                'fragrance_family': product.get('fragrance_family'),
                'concentration': product.get('concentration'),
                'volume_ml': product.get('volume_ml'),
                'gender': product.get('gender'),
                'top_notes': top_notes,
                'middle_notes': middle_notes,
                'base_notes': base_notes,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
        )


def downgrade() -> None:
    # Best-effort delete seeded products by slug list
    bind = op.get_bind()
    try:
        from app.data.seed_products import BLUE_PANSY_PRODUCTS
    except Exception:
        return

    slugs = [p['slug'] for p in BLUE_PANSY_PRODUCTS]
    if not slugs:
        return

    delete_sql = text(
        "DELETE FROM products WHERE slug IN (" + ",".join([":s" + str(i) for i in range(len(slugs))]) + ")"
    )

    params = {"s" + str(i): slug for i, slug in enumerate(slugs)}
    bind.execute(delete_sql, params)
