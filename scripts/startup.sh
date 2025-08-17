#!/bin/bash
set -e

echo "🚀 Starting BluePansy API startup sequence..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"; do
    echo "Database not ready, waiting 5 seconds..."
    sleep 5
done

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start the main application
echo "🚀 Starting main application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
