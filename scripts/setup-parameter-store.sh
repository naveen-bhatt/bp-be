#!/bin/bash

# Setup AWS Parameter Store parameters for dev environment
# Run this script after your infrastructure is deployed

set -e

ENVIRONMENT="dev"
REGION="ap-south-1"

echo "Setting up Parameter Store parameters for $ENVIRONMENT environment..."

# Database Configuration
aws ssm put-parameter \
    --name "/$ENVIRONMENT/database_url" \
    --value "mysql+pymysql://dev_user:$(aws secretsmanager get-secret-value --secret-id devrdsstackdevdatabaseSecre-yCMu2q5ZHYce-EbeNms --query SecretString --output text | jq -r .password)@$(aws rds describe-db-instances --db-instance-identifier dev-database --query 'DBInstances[0].Endpoint.Address' --output text):3306/dev_bluepansy" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

# Application Configuration
aws ssm put-parameter \
    --name "/$ENVIRONMENT/app_name" \
    --value "BP Backend Dev" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/environment" \
    --value "$ENVIRONMENT" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/debug" \
    --value "true" \
    --type "String" \
    --region $REGION \
    --overwrite

# Security Configuration
aws ssm put-parameter \
    --name "/$ENVIRONMENT/secret_key" \
    --value "dev-secret-key-change-in-production-$(openssl rand -hex 32)" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/jwt_algorithm" \
    --value "HS256" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/access_token_ttl_minutes" \
    --value "30" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/refresh_token_ttl_days" \
    --value "7" \
    --type "String" \
    --region $REGION \
    --overwrite

# CORS Configuration
aws ssm put-parameter \
    --name "/$ENVIRONMENT/cors_origins" \
    --value "http://localhost:3000,https://dev-api.bluepansy.in" \
    --type "String" \
    --region $REGION \
    --overwrite

# Frontend Configuration
aws ssm put-parameter \
    --name "/$ENVIRONMENT/frontend_url" \
    --value "http://localhost:3000" \
    --type "String" \
    --region $REGION \
    --overwrite

# OAuth Configuration (set these manually with your actual values)
aws ssm put-parameter \
    --name "/$ENVIRONMENT/google_client_id" \
    --value "your-google-client-id" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/google_client_secret" \
    --value "your-google-client-secret" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

# Payment Configuration (set these manually with your actual values)
aws ssm put-parameter \
    --name "/$ENVIRONMENT/stripe_secret_key" \
    --value "your-stripe-secret-key" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/razorpay_key_id" \
    --value "your-razorpay-key-id" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/razorpay_key_secret" \
    --value "your-razorpay-key-secret" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

# Admin Configuration
aws ssm put-parameter \
    --name "/$ENVIRONMENT/admin_email" \
    --value "admin@bluepansy.in" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/$ENVIRONMENT/admin_password" \
    --value "admin123" \
    --type "SecureString" \
    --region $REGION \
    --overwrite

echo "✅ Parameter Store parameters created successfully!"
echo "📝 Note: Some parameters (OAuth, Payment) need to be updated with actual values"
echo "🔐 All parameters are prefixed with /$ENVIRONMENT/"
