#!/bin/bash

# Beta Environment Deployment Script
# This script deploys the Beta infrastructure using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$SCRIPT_DIR/environments/beta"

echo -e "${BLUE}🚀 Beta Environment Deployment${NC}"
echo "=================================="

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform is not installed. Please install Terraform first.${NC}"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq is not installed. Please install jq first.${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install AWS CLI first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Check AWS credentials
echo -e "${YELLOW}🔍 Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials are valid${NC}"

# Check if Parameter Store parameters exist
echo -e "${YELLOW}🔍 Checking Parameter Store parameters...${NC}"
if ! aws ssm get-parameter --name "/beta/database_url" --region ap-south-1 &> /dev/null; then
    echo -e "${RED}❌ Parameter Store parameters not found. Please run the setup script first.${NC}"
    echo -e "${YELLOW}💡 Run: ./scripts/setup-parameter-store.sh beta${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Parameter Store parameters exist${NC}"

# Check if Terraform has already deployed infrastructure
echo -e "${YELLOW}🔍 Checking existing Terraform deployment...${NC}"
infrastructure_exists=false

# Change to environment directory to check Terraform state
cd "$ENV_DIR"

# Check if Terraform has been initialized
if [ ! -d ".terraform" ]; then
    echo "ℹ️  Terraform not initialized yet"
    infrastructure_exists=false
else
    # Check if Terraform has deployed any resources
    if terraform state list &> /dev/null; then
        # Check for critical resources in Terraform state
        if terraform state list | grep -q "aws_lb.main" && \
           terraform state list | grep -q "aws_ecs_cluster.main" && \
           terraform state list | grep -q "aws_ecr_repository.api"; then
            echo "✅ All critical infrastructure resources deployed by Terraform"
            infrastructure_exists=true
        else
            echo "⚠️  Some Terraform resources missing, proceeding with deployment"
            infrastructure_exists=false
        fi
    else
        echo "ℹ️  Terraform state not available yet"
        infrastructure_exists=false
    fi
fi

if [ "$infrastructure_exists" = true ]; then
    echo -e "${GREEN}✅ All infrastructure resources already deployed by Terraform. Skipping deployment.${NC}"
    echo -e "${BLUE}💡 To redeploy, destroy existing infrastructure first:${NC}"
    echo -e "${BLUE}   terraform destroy${NC}"
    echo -e "${BLUE}💡 Or force update:${NC}"
    echo -e "${BLUE}   terraform apply -replace=aws_lb.main${NC}"
    exit 0
fi

# Go back to script directory
cd "$SCRIPT_DIR"

# Build Lambda functions
echo -e "${YELLOW}🔨 Building Lambda functions...${NC}"
if ! ./build-lambda.sh; then
    echo -e "${RED}❌ Failed to build Lambda functions${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Lambda functions built successfully${NC}"

# Change to environment directory
cd "$ENV_DIR"

# Initialize Terraform
echo -e "${YELLOW}🔧 Initializing Terraform...${NC}"
if ! terraform init; then
    echo -e "${RED}❌ Terraform initialization failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Terraform initialized successfully${NC}"

# Plan Terraform deployment
echo -e "${YELLOW}📋 Planning Terraform deployment...${NC}"
if ! terraform plan; then
    echo -e "${RED}❌ Terraform plan failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Terraform plan completed successfully${NC}"

# Confirm deployment
echo -e "${YELLOW}⚠️  Do you want to proceed with the deployment? (y/N)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚫 Deployment cancelled${NC}"
    exit 0
fi

# Apply Terraform configuration
echo -e "${YELLOW}🚀 Applying Terraform configuration...${NC}"
if ! terraform apply -auto-approve; then
    echo -e "${RED}❌ Terraform apply failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Terraform apply completed successfully${NC}"

# Validate deployment
echo -e "${YELLOW}🔍 Validating deployment...${NC}"
cd "$SCRIPT_DIR"
if ! ./validate-infrastructure.sh beta; then
    echo -e "${RED}❌ Infrastructure validation failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Beta Environment deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo -e "${BLUE}   Environment: Beta${NC}"
echo -e "${BLUE}   ECS Cluster: beta-bluepansy-cluster${NC}"
echo -e "${BLUE}   ECS Service: beta-bluepansy-service${NC}"
echo -e "${BLUE}   ALB: beta-bluepansy-alb${NC}"
echo -e "${BLUE}   ECR: beta-bluepansy-api${NC}"
echo ""
echo -e "${BLUE}🔗 Next steps:${NC}"
echo -e "${BLUE}   1. Push your application image to ECR${NC}"
echo -e "${BLUE}   2. Update the ECS service with the new image${NC}"
echo -e "${BLUE}   3. Test the deployment${NC}"
