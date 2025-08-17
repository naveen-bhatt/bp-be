#!/bin/bash

# Infrastructure validation script
# Run this after Terraform deployment to ensure everything is working

set -e

echo "🔍 Validating BluePansy Dev Infrastructure"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    print_status "OK" "AWS credentials are valid"
    aws_account=$(aws sts get-caller-identity --query 'Account' --output text)
    echo "   Account: $aws_account"
else
    print_status "ERROR" "AWS credentials are invalid or not configured"
    exit 1
fi

# Check ECS Cluster
echo ""
echo "🐳 Checking ECS Cluster..."
if aws ecs describe-clusters --clusters dev-bluepansy-cluster --region ap-south-1 &> /dev/null; then
    cluster_status=$(aws ecs describe-clusters --clusters dev-bluepansy-cluster --region ap-south-1 --query 'clusters[0].status' --output text)
    if [ "$cluster_status" = "ACTIVE" ]; then
        print_status "OK" "ECS Cluster 'dev-bluepansy-cluster' is active"
    else
        print_status "WARN" "ECS Cluster status: $cluster_status"
    fi
else
    print_status "ERROR" "ECS Cluster 'dev-bluepansy-cluster' not found"
fi

# Check ECS Service
echo ""
echo "🚀 Checking ECS Service..."
if aws ecs describe-services --cluster dev-bluepansy-cluster --services dev-bluepansy-service --region ap-south-1 &> /dev/null; then
    service_status=$(aws ecs describe-services --cluster dev-bluepansy-cluster --services dev-bluepansy-service --region ap-south-1 --query 'services[0].status' --output text)
    desired_count=$(aws ecs describe-services --cluster dev-bluepansy-cluster --services dev-bluepansy-service --region ap-south-1 --query 'services[0].desiredCount' --output text)
    running_count=$(aws ecs describe-services --cluster dev-bluepansy-cluster --services dev-bluepansy-service --region ap-south-1 --query 'services[0].runningCount' --output text)
    
    if [ "$service_status" = "ACTIVE" ]; then
        print_status "OK" "ECS Service 'dev-bluepansy-service' is active"
        echo "   Desired tasks: $desired_count"
        echo "   Running tasks: $running_count"
        
        if [ "$running_count" -gt 0 ]; then
            print_status "OK" "ECS tasks are running"
        else
            print_status "WARN" "No ECS tasks are running yet"
        fi
    else
        print_status "WARN" "ECS Service status: $service_status"
    fi
else
    print_status "ERROR" "ECS Service 'dev-bluepansy-service' not found"
fi

# Check Application Load Balancer
echo ""
echo "🌐 Checking Application Load Balancer..."
if aws elbv2 describe-load-balancers --names dev-bluepansy-alb --region ap-south-1 &> /dev/null; then
    alb_state=$(aws elbv2 describe-load-balancers --names dev-bluepansy-alb --region ap-south-1 --query 'LoadBalancers[0].State.Code' --output text)
    alb_dns=$(aws elbv2 describe-load-balancers --names dev-bluepansy-alb --region ap-south-1 --query 'LoadBalancers[0].DNSName' --output text)
    
    if [ "$alb_state" = "active" ]; then
        print_status "OK" "ALB 'dev-bluepansy-alb' is active"
        echo "   DNS Name: $alb_dns"
    else
        print_status "WARN" "ALB state: $alb_state"
    fi
else
    print_status "ERROR" "ALB 'dev-bluepansy-alb' not found"
fi

# Check ECR Repository
echo ""
echo "📦 Checking ECR Repository..."
if aws ecr describe-repositories --repository-names dev-bluepansy-api --region ap-south-1 &> /dev/null; then
    print_status "OK" "ECR Repository 'dev-bluepansy-api' exists"
    
    # Check if there are any images
    image_count=$(aws ecr list-images --repository-name dev-bluepansy-api --region ap-south-1 --query 'imageIds | length(@)' --output text)
    if [ "$image_count" -gt 0 ]; then
        print_status "OK" "ECR Repository has $image_count image(s)"
    else
        print_status "WARN" "ECR Repository is empty (no images pushed yet)"
    fi
else
    print_status "ERROR" "ECR Repository 'dev-bluepansy-api' not found"
fi

# Check Target Group Health
echo ""
echo "🎯 Checking Target Group Health..."
if aws elbv2 describe-load-balancers --names dev-bluepansy-alb --region ap-south-1 &> /dev/null; then
    target_group_arn=$(aws ecs describe-services --cluster dev-bluepansy-cluster --services dev-bluepansy-service --region ap-south-1 --query 'services[0].loadBalancers[0].targetGroupArn' --output text 2>/dev/null || echo "")
    
    if [ -n "$target_group_arn" ] && [ "$target_group_arn" != "None" ]; then
        healthy_targets=$(aws elbv2 describe-target-health --target-group-arn "$target_group_arn" --region ap-south-1 --query 'TargetHealthDescriptions[?TargetHealth.State==`healthy`] | length(@)' --output text)
        total_targets=$(aws elbv2 describe-target-health --target-group-arn "$target_group_arn" --region ap-south-1 --query 'TargetHealthDescriptions | length(@)' --output text)
        
        if [ "$healthy_targets" -gt 0 ]; then
            print_status "OK" "Target Group has $healthy_targets healthy targets out of $total_targets"
        else
            print_status "WARN" "Target Group has 0 healthy targets out of $total_targets"
        fi
    else
        print_status "WARN" "Target Group not yet associated with ECS service"
    fi
else
    print_status "ERROR" "Cannot check Target Group (ALB not found)"
fi

# Check CloudWatch Logs
echo ""
echo "📝 Checking CloudWatch Logs..."
if aws logs describe-log-groups --log-group-name-prefix "/ecs/dev-bluepansy-api" --region ap-south-1 &> /dev/null; then
    print_status "OK" "CloudWatch Log Group '/ecs/dev-bluepansy-api' exists"
else
    print_status "ERROR" "CloudWatch Log Group '/ecs/dev-bluepansy-api' not found"
fi

# Check IAM Roles
echo ""
echo "🔐 Checking IAM Roles..."
if aws iam get-role --role-name dev-bluepansy-ecs-execution-role &> /dev/null; then
    print_status "OK" "IAM Execution Role 'dev-bluepansy-ecs-execution-role' exists"
else
    print_status "ERROR" "IAM Execution Role 'dev-bluepansy-ecs-execution-role' not found"
fi

if aws iam get-role --role-name dev-bluepansy-ecs-task-role &> /dev/null; then
    print_status "OK" "IAM Task Role 'dev-bluepansy-ecs-task-role' exists"
else
    print_status "ERROR" "IAM Task Role 'dev-bluepansy-ecs-task-role' not found"
fi

# Summary
echo ""
echo "=========================================="
echo "🏁 Infrastructure Validation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Push your Docker image to ECR:"
echo "   aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $aws_account.dkr.ecr.ap-south-1.amazonaws.com"
echo "   docker build -t dev-bluepansy-api ."
echo "   docker tag dev-bluepansy-api:latest $aws_account.dkr.ecr.ap-south-1.amazonaws.com/dev-bluepansy-api:latest"
echo "   docker push $aws_account.dkr.ecr.ap-south-1.amazonaws.com/dev-bluepansy-api:latest"
echo ""
echo "2. Your app will be available at: $alb_dns"
echo ""
echo "3. Use GitHub workflow to deploy app updates"
