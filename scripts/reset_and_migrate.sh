#!/bin/bash

# Database Reset and Migration Script
# This script safely resets the database and runs the new consolidated migration
# USE ONLY FOR FIRST-TIME DEPLOYMENT OR DEVELOPMENT

set -e  # Exit on any error

echo "🚀 Database Reset and Migration Script"
echo "======================================"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "🔍 Database URL: ${DATABASE_URL:0:50}..."

# Function to check if table exists
table_exists() {
    local table_name=$1
    python3 -c "
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

try:
    engine = create_engine('$DATABASE_URL')
    with engine.connect() as conn:
        result = conn.execute(text('SHOW TABLES LIKE \"$table_name\"'))
        return len(result.fetchall()) > 0
except Exception as e:
    print(f'Error checking table: {e}')
    return False
"
}

# Check if any tables exist
echo "🔍 Checking existing database state..."
if table_exists "users"; then
    echo "⚠️  Warning: Database already has tables!"
    echo "   This script will DROP ALL TABLES and recreate them."
    echo "   Are you sure you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Operation cancelled by user"
        exit 1
    fi
    
    echo "🗑️  Dropping existing tables..."
    python3 -c "
import os
from sqlalchemy import create_engine, text

engine = create_engine('$DATABASE_URL')
with engine.connect() as conn:
    # Drop tables in reverse dependency order
    tables = ['wishlist', 'payments', 'order_items', 'orders', 'cart', 'addresses', 'products', 'social_accounts', 'users']
    for table in tables:
        try:
            conn.execute(text(f'DROP TABLE IF EXISTS {table}'))
            print(f'✅ Dropped table: {table}')
        except Exception as e:
            print(f'⚠️  Could not drop {table}: {e}')
    conn.commit()
"
else
    echo "✅ Database is empty, proceeding with fresh migration"
fi

# Reset alembic version table
echo "🔄 Resetting Alembic version tracking..."
python3 -c "
import os
from sqlalchemy import create_engine, text

engine = create_engine('$DATABASE_URL')
with engine.connect() as conn:
    try:
        conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        print('✅ Dropped alembic_version table')
    except Exception as e:
        print(f'⚠️  Could not drop alembic_version: {e}')
    conn.commit()
"

# Run the new consolidated migration
echo "🚀 Running consolidated migration..."
cd /app
alembic upgrade head

echo "✅ Migration completed successfully!"
echo "🎉 Database is now ready with complete schema!"

# Verify tables were created
echo "🔍 Verifying created tables..."
python3 -c "
import os
from sqlalchemy import create_engine, text

engine = create_engine('$DATABASE_URL')
with engine.connect() as conn:
    result = conn.execute(text('SHOW TABLES'))
    tables = [row[0] for row in result.fetchall()]
    print(f'✅ Created {len(tables)} tables:')
    for table in sorted(tables):
        print(f'   - {table}')
"
