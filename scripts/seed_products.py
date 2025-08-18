#!/usr/bin/env python3
"""
Seed Products Script

This script seeds the products table with the Blue Pansy perfume collection.
Run this after the initial migration to populate the database with products.
"""

import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.data.seed_products import BLUE_PANSY_PRODUCTS
import json

def seed_products():
    """Seed the products table with perfume data."""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    print("🚀 Seeding products table...")
    
    # Create database connection
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check if products already exist
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            count = result.scalar()
            
            if count > 0:
                print(f"⚠️  Products table already has {count} products")
                response = input("Do you want to continue and add more products? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Seeding cancelled")
                    return
            
            # Insert products
            for product in BLUE_PANSY_PRODUCTS:
                # Convert JSON strings to proper JSON for database
                slide_image_urls = json.loads(product['slide_image_urls']) if product['slide_image_urls'] else None
                top_notes = json.loads(product['top_notes']) if product['top_notes'] else None
                middle_notes = json.loads(product['middle_notes']) if product['middle_notes'] else None
                base_notes = json.loads(product['base_notes']) if product['base_notes'] else None
                
                # Insert product
                insert_query = text("""
                    INSERT INTO products (
                        name, slug, description, main_image_url, slide_image_urls,
                        price, currency, quantity, date_of_manufacture, expiry_duration_months,
                        rank_of_product, is_active, brand, fragrance_family, concentration,
                        volume_ml, gender, top_notes, middle_notes, base_notes
                    ) VALUES (
                        :name, :slug, :description, :main_image_url, :slide_image_urls,
                        :price, :currency, :quantity, :date_of_manufacture, :expiry_duration_months,
                        :rank_of_product, :is_active, :brand, :fragrance_family, :concentration,
                        :volume_ml, :gender, :top_notes, :middle_notes, :base_notes
                    )
                """)
                
                conn.execute(insert_query, {
                    'name': product['name'],
                    'slug': product['slug'],
                    'description': product['description'],
                    'main_image_url': product['main_image_url'],
                    'slide_image_urls': slide_image_urls,
                    'price': product['price'],
                    'currency': product['currency'],
                    'quantity': product['quantity'],
                    'date_of_manufacture': product['date_of_manufacture'],
                    'expiry_duration_months': product['expiry_duration_months'],
                    'rank_of_product': product['rank_of_product'],
                    'is_active': product['is_active'],
                    'brand': product['brand'],
                    'fragrance_family': product['fragrance_family'],
                    'concentration': product['concentration'],
                    'volume_ml': product['volume_ml'],
                    'gender': product['gender'],
                    'top_notes': top_notes,
                    'middle_notes': middle_notes,
                    'base_notes': base_notes
                })
                
                print(f"✅ Added: {product['name']}")
            
            # Commit the transaction
            conn.commit()
            
            # Verify the insertion
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            final_count = result.scalar()
            
            print(f"🎉 Successfully seeded {len(BLUE_PANSY_PRODUCTS)} products!")
            print(f"📊 Total products in database: {final_count}")
            
    except Exception as e:
        print(f"❌ Error seeding products: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    seed_products()
