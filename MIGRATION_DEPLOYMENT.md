# Database Migration Deployment Strategy

## Current Approach: Container Startup Migration

We've implemented **Option 1: Startup Script Migration** as the recommended approach for running Alembic migrations during deployment.

### How It Works

1. **Startup Script**: `scripts/startup.sh` handles the complete startup sequence
2. **Database Readiness Check**: Waits for the database to be accessible before proceeding
3. **Migration Execution**: Runs `alembic upgrade head` automatically
4. **Application Start**: Starts the FastAPI application with `uvicorn`

### Benefits

✅ **Network Isolation**: No external connectivity issues (migrations run inside ECS VPC)  
✅ **Dependency Management**: All required packages are available in the container  
✅ **Automatic Execution**: Migrations run every time the container starts  
✅ **Error Handling**: Container won't start if migrations fail  
✅ **Clean Separation**: No complex GitHub Actions migration logic

### Implementation Details

#### 1. Startup Script (`scripts/startup.sh`)

```bash
#!/bin/bash
set -e

echo "🚀 Starting BluePansy API startup sequence..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until python -c "
import pymysql
import os
# ... database connection test logic ...
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
```

#### 2. Dockerfile Changes

```dockerfile
# Copy startup script
COPY scripts/startup.sh /app/startup.sh

# Use startup script instead of direct uvicorn
CMD ["/app/startup.sh"]
```

#### 3. GitHub Actions Workflow

- **Removed**: Complex migration step with external container execution
- **Simplified**: Just deploy the container and let it handle migrations internally

### Deployment Flow

1. **Build & Push**: Docker image with startup script
2. **Deploy**: ECS service starts new task
3. **Startup**: Container runs startup script
4. **Database Check**: Waits for database connectivity
5. **Migrations**: Runs `alembic upgrade head`
6. **Application**: Starts FastAPI server
7. **Health Check**: ECS confirms service is healthy

### Why This Approach is Better

- **No Network Issues**: Migrations run inside AWS VPC with proper security groups
- **Automatic Retry**: Container restart automatically retries failed migrations
- **Simplified CI/CD**: GitHub Actions just deploys, no complex migration logic
- **Production Ready**: Follows container best practices for startup sequences
- **Error Visibility**: Migration failures appear in ECS logs for debugging

### Monitoring

- **ECS Logs**: Check `/ecs/dev-bluepansy-api` log group for migration status
- **Startup Sequence**: Look for "Database is ready!" and "Database migrations completed successfully!" messages
- **Error Handling**: Container will fail to start if migrations fail, preventing deployment issues

This approach eliminates the network connectivity problems we experienced with GitHub Actions and provides a robust, production-ready migration strategy.
