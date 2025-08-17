# Database Migration Deployment

## Overview

This document explains how database migrations are now automatically handled during deployment to ensure database schema consistency across all environments.

## How It Works

### 1. Post-Deployment Migration

Migrations are automatically executed after successful deployment:

1. **Application Deployment**: New code is deployed and health checks pass
2. **Migration Execution**: `alembic upgrade head` runs automatically
3. **Schema Update**: Database schema is updated to match new code requirements

### 2. GitHub Actions Integration

- **Post-Health Check**: Migrations run after application is confirmed healthy
- **Automatic Execution**: No manual intervention required
- **Failure Handling**: If migrations fail, deployment workflow shows error

### 3. GitHub Actions Workflow Updates

All environments (dev, qa, beta, production) now include:

- **Post-Deployment Migration Step**: Automatically runs `alembic upgrade head`
- **Health Check Validation**: Ensures application is running before migrations
- **Automatic Execution**: No manual intervention required

## Benefits

1. **Automatic Migration**: No manual intervention required during deployment
2. **Database Consistency**: Ensures all environments have the same schema
3. **Deployment Safety**: Prevents application startup with mismatched database schema
4. **Environment Parity**: Consistent behavior across all deployment environments

## Migration Process

1. **Pre-deployment**: Developer creates migration files using `alembic revision --autogenerate -m "Description"`
2. **During Deployment**:
   - Container starts
   - Startup script waits for database readiness
   - Migrations are applied automatically
   - Application starts with updated schema
3. **Post-deployment**: Health checks verify application is running correctly

## Troubleshooting

### Migration Failures

If migrations fail during deployment:

1. Check CloudWatch logs for the specific ECS task
2. Verify database connectivity and credentials
3. Ensure migration files are properly committed to the repository
4. Check for conflicting migrations or schema inconsistencies

### Database Connection Issues

The startup script includes a retry mechanism for database connectivity. If the database is not ready:

1. Verify RDS instance is running
2. Check security group configurations
3. Ensure proper network connectivity from ECS to RDS

## Environment Variables

The following environment variables are required for migrations to work:

- `DATABASE_URL`: Full database connection string
- `PYTHONPATH`: Set to `/app` for proper module resolution
- All other application-specific environment variables

## Security Considerations

- Database credentials are managed through AWS Secrets Manager
- Startup script runs with the same permissions as the application
- No additional IAM permissions required beyond existing ECS task role

## Rollback Strategy

If a migration causes issues:

1. **Immediate**: Stop the ECS service to prevent new connections
2. **Investigation**: Review migration logs and database state
3. **Rollback**: Use `alembic downgrade -1` to revert the problematic migration
4. **Redeploy**: Deploy the previous version without the problematic migration

## Best Practices

1. **Test Migrations**: Always test migrations in lower environments first
2. **Small Increments**: Keep migrations small and focused
3. **Backup Strategy**: Ensure database backups before major schema changes
4. **Monitoring**: Monitor migration execution times and success rates
5. **Documentation**: Document complex migrations with clear descriptions
