#!/bin/bash
set -e

echo "🚀 Starting BluePansy API startup sequence..."

# Change to app directory to ensure proper context
cd /app

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until python -c "
import pymysql
import os
import time

try:
    # Parse DATABASE_URL to extract connection details
    db_url = os.environ['DATABASE_URL']
    if db_url.startswith('mysql+pymysql://'):
        # Remove mysql+pymysql:// prefix
        db_url = db_url.replace('mysql+pymysql://', '')
        
        # Split user:pass@host:port/database
        if '@' in db_url:
            credentials, rest = db_url.split('@', 1)
            if ':' in credentials:
                user, password = credentials.split(':', 1)
            else:
                user = credentials
                password = ''
            
            if ':' in rest:
                host_port, database = rest.split('/', 1)
                if ':' in host_port:
                    host, port = host_port.split(':', 1)
                    port = int(port)
                else:
                    host = host_port
                    port = 3306
            else:
                host = rest.split('/')[0]
                port = 3306
                database = rest.split('/')[1]
        else:
            print('Invalid DATABASE_URL format')
            exit(1)
        
        # Test connection
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=10
        )
        conn.close()
        print('Database is ready!')
    else:
        print('Unsupported database URL format')
        exit(1)
        
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"; do
    echo "Database not ready, waiting 5 seconds..."
    sleep 5
done

# Run database migrations
echo "🔄 Running database migrations..."
echo "Current working directory: $(pwd)"
echo "Alembic version: $(alembic --version)"
alembic upgrade head

# Start the main application
echo "🚀 Starting main application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
