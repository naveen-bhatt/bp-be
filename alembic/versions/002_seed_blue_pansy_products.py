"""Seed Blue Pansy perfume collection

Revision ID: 002_seed_products
Revises: 001_initial
Create Date: 2025-01-12 01:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '002_seed_products'
down_revision: Union[str, None] = '001_create_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed Blue Pansy perfume collection."""
    
    now = datetime.utcnow()
    manufacture_date = datetime(2024, 6, 15)  # June 15, 2024
    
    # Clear existing products first
    op.execute(text("DELETE FROM products WHERE brand = 'Blue Pansy'"))
    
    products_data = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Monarch\'s Dream',
            'slug': 'monarchs-dream',
            'description': 'Our signature fragrance - A majestic blend inspired by the monarch butterfly\'s journey through blooming meadows. This exquisite parfum captures the essence of transformation and grace.',
            'main_image_url': 'https://images.bluepansy.com/monarchs-dream-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/monarchs-dream-1.jpg", "https://images.bluepansy.com/monarchs-dream-2.jpg", "https://images.bluepansy.com/monarchs-dream-3.jpg"]',
            'price': 189.99,
            'currency': 'USD',
            'quantity': 50,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 1,  # Signature perfume gets top rank
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Floral Oriental',
            'concentration': 'Parfum',
            'volume_ml': 50,
            'gender': 'Unisex',
            'top_notes': '["Bergamot", "Pink Pepper", "Mandarin"]',
            'middle_notes': '["Rose Petals", "Jasmine", "Lily of the Valley", "Peony"]',
            'base_notes': '["Sandalwood", "Vanilla", "White Musk", "Amber"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Swallowtail Serenade',
            'slug': 'swallowtail-serenade',
            'description': 'A delicate dance of citrus and florals, reminiscent of swallowtail butterflies dancing among summer blooms.',
            'main_image_url': 'https://images.bluepansy.com/swallowtail-serenade-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/swallowtail-serenade-1.jpg", "https://images.bluepansy.com/swallowtail-serenade-2.jpg"]',
            'price': 149.99,
            'currency': 'USD',
            'quantity': 75,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 2,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Fresh Floral',
            'concentration': 'EDP',
            'volume_ml': 50,
            'gender': 'Women',
            'top_notes': '["Lemon", "Green Leaves", "Aquatic Notes"]',
            'middle_notes': '["White Jasmine", "Freesia", "Green Tea"]',
            'base_notes': '["Cedar", "White Musk", "Soft Amber"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Woodland Whisper',
            'slug': 'woodland-whisper',
            'description': 'Deep and mysterious, like butterflies fluttering through ancient forests. A woody oriental masterpiece.',
            'main_image_url': 'https://images.bluepansy.com/woodland-whisper-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/woodland-whisper-1.jpg", "https://images.bluepansy.com/woodland-whisper-2.jpg"]',
            'price': 159.99,
            'currency': 'USD',
            'quantity': 60,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 3,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Woody Oriental',
            'concentration': 'EDP',
            'volume_ml': 50,
            'gender': 'Men',
            'top_notes': '["Black Pepper", "Cardamom", "Bergamot"]',
            'middle_notes': '["Cedarwood", "Vetiver", "Rose"]',
            'base_notes': '["Oud", "Patchouli", "Dark Vanilla", "Leather"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Garden Reverie',
            'slug': 'garden-reverie',
            'description': 'A romantic stroll through an English garden where painted lady butterflies dance among roses and peonies.',
            'main_image_url': 'https://images.bluepansy.com/garden-reverie-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/garden-reverie-1.jpg", "https://images.bluepansy.com/garden-reverie-2.jpg"]',
            'price': 139.99,
            'currency': 'USD',
            'quantity': 80,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 4,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Floral',
            'concentration': 'EDT',
            'volume_ml': 75,
            'gender': 'Women',
            'top_notes': '["Peach", "Green Leaves", "Dewdrops"]',
            'middle_notes': '["English Rose", "Peony", "Magnolia"]',
            'base_notes': '["Soft Musk", "Blonde Woods", "Powdery Notes"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Azure Wings',
            'slug': 'azure-wings',
            'description': 'Fresh and invigorating like the blue morpho butterfly soaring over tropical waters. A aquatic fresh fragrance.',
            'main_image_url': 'https://images.bluepansy.com/azure-wings-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/azure-wings-1.jpg", "https://images.bluepansy.com/azure-wings-2.jpg"]',
            'price': 129.99,
            'currency': 'USD',
            'quantity': 90,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 5,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Aquatic Fresh',
            'concentration': 'EDT',
            'volume_ml': 100,
            'gender': 'Unisex',
            'top_notes': '["Sea Breeze", "Mint", "Grapefruit"]',
            'middle_notes': '["Marine Accord", "Lotus", "Cucumber"]',
            'base_notes': '["Driftwood", "Sea Salt", "Clean Musk"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Midnight Orchid',
            'slug': 'midnight-orchid',
            'description': 'Mysterious and sensual, inspired by night-blooming orchids where moths dance in moonlight.',
            'main_image_url': 'https://images.bluepansy.com/midnight-orchid-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/midnight-orchid-1.jpg", "https://images.bluepansy.com/midnight-orchid-2.jpg"]',
            'price': 169.99,
            'currency': 'USD',
            'quantity': 45,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 6,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Oriental Floral',
            'concentration': 'EDP',
            'volume_ml': 50,
            'gender': 'Women',
            'top_notes': '["Black Currant", "Pink Pepper", "Mandarin"]',
            'middle_notes': '["Black Orchid", "Plum", "Rose"]',
            'base_notes': '["Dark Chocolate", "Vanilla", "Patchouli", "Incense"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Copper Sunrise',
            'slug': 'copper-sunrise',
            'description': 'Warm and spicy like copper butterflies basking in the morning sun. A spicy oriental for the modern man.',
            'main_image_url': 'https://images.bluepansy.com/copper-sunrise-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/copper-sunrise-1.jpg", "https://images.bluepansy.com/copper-sunrise-2.jpg"]',
            'price': 154.99,
            'currency': 'USD',
            'quantity': 65,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 7,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Spicy Oriental',
            'concentration': 'EDP',
            'volume_ml': 50,
            'gender': 'Men',
            'top_notes': '["Ginger", "Saffron", "Lemon"]',
            'middle_notes': '["Cinnamon", "Nutmeg", "Orange Blossom"]',
            'base_notes': '["Amber", "Tobacco", "Sandalwood", "Benzoin"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Velvet Meadow',
            'slug': 'velvet-meadow',
            'description': 'Soft and powdery like velvet butterflies in a lavender meadow. A comforting gourmand floral.',
            'main_image_url': 'https://images.bluepansy.com/velvet-meadow-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/velvet-meadow-1.jpg", "https://images.bluepansy.com/velvet-meadow-2.jpg"]',
            'price': 134.99,
            'currency': 'USD',
            'quantity': 70,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 8,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Gourmand Floral',
            'concentration': 'EDT',
            'volume_ml': 75,
            'gender': 'Women',
            'top_notes': '["Lavender", "Honey", "Pear"]',
            'middle_notes': '["Violet", "Iris", "Almond Blossom"]',
            'base_notes': '["Vanilla", "Tonka Bean", "Soft Cashmere", "Musk"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Storm Chaser',
            'slug': 'storm-chaser',
            'description': 'Bold and electrifying like butterflies before a storm. An intense woody fragrance with ozone notes.',
            'main_image_url': 'https://images.bluepansy.com/storm-chaser-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/storm-chaser-1.jpg", "https://images.bluepansy.com/storm-chaser-2.jpg"]',
            'price': 164.99,
            'currency': 'USD',
            'quantity': 55,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 9,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Woody Fresh',
            'concentration': 'EDP',
            'volume_ml': 50,
            'gender': 'Unisex',
            'top_notes': '["Ozone", "Electric Citrus", "Juniper"]',
            'middle_notes': '["Geranium", "Sage", "Pine"]',
            'base_notes': '["Cedarwood", "Vetiver", "Oakmoss", "Gray Amber"]',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Golden Nectar',
            'slug': 'golden-nectar',
            'description': 'Sweet and luminous like golden butterflies sipping nectar from honeysuckle flowers. A radiant gourmand.',
            'main_image_url': 'https://images.bluepansy.com/golden-nectar-main.jpg',
            'slide_image_urls': '["https://images.bluepansy.com/golden-nectar-1.jpg", "https://images.bluepansy.com/golden-nectar-2.jpg"]',
            'price': 144.99,
            'currency': 'USD',
            'quantity': 85,
            'date_of_manufacture': manufacture_date,
            'expiry_duration_months': 36,
            'rank_of_product': 10,
            'is_active': True,
            'brand': 'Blue Pansy',
            'fragrance_family': 'Gourmand',
            'concentration': 'EDT',
            'volume_ml': 75,
            'gender': 'Unisex',
            'top_notes': '["Honeysuckle", "Golden Apple", "Citrus Zest"]',
            'middle_notes': '["Acacia Honey", "Orange Blossom", "Tuberose"]',
            'base_notes': '["Caramel", "Blonde Woods", "Golden Amber", "Soft Musk"]',
            'created_at': now,
            'updated_at': now
        }
    ]
    
    # Insert products using bulk insert
    if products_data:
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
        for product in products_data:
            # Map rank_of_product to rank for the current database schema
            product_data = product.copy()
            op.get_bind().execute(insert_stmt, product_data)


def downgrade() -> None:
    """Remove Blue Pansy products."""
    op.execute(text("DELETE FROM products WHERE brand = 'Blue Pansy'"))
