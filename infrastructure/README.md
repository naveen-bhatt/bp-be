# 🚀 BluePansy Infrastructure as Code (CDK) - Python Version

This directory contains the AWS CDK infrastructure code for the BluePansy application, supporting multiple environments: **dev**, **qa**, **beta**, and **production**.

## 🏗️ Architecture Overview

```
Internet → Route53 → ACM (SSL) → ALB → ECS Fargate → RDS MySQL
                ↓
        Lambda (Auto Start/Stop Services)
```

## 🌍 Supported Environments

| Environment    | Subdomain               | Auto-Stop      | Cost Optimization | Purpose               |
| -------------- | ----------------------- | -------------- | ----------------- | --------------------- |
| **dev**        | `dev-api.bluepansy.in`  | ✅ Yes (5 min) | 🟢 High           | Development & Testing |
| **qa**         | `qa-api.bluepansy.in`   | ✅ Yes (5 min) | 🟢 High           | Quality Assurance     |
| **beta**       | `beta-api.bluepansy.in` | ❌ No          | 🟡 Medium         | Staging & Pre-prod    |
| **production** | `api.bluepansy.in`      | ❌ No          | 🔴 Low            | Production            |

## 💰 Cost Breakdown (Monthly)

### Dev Environment (Auto-Stop Enabled)

| Service         | Running Cost | Stopped Cost | Savings    |
| --------------- | ------------ | ------------ | ---------- |
| **RDS MySQL**   | $3-4         | $0           | 100%       |
| **ECS Fargate** | $2-3         | $0           | 100%       |
| **ALB**         | $1-2         | $1-2         | 0%         |
| **Lambda**      | $0.10        | $0.10        | 0%         |
| **Route53**     | $0.50        | $0.50        | 0%         |
| **VPC & NAT**   | $2-3         | $2-3         | 0%         |
| **Total**       | **$9-13**    | **$4-6**     | **40-60%** |

### Production Environment (Always On)

| Service         | Cost       | Notes                            |
| --------------- | ---------- | -------------------------------- |
| **RDS MySQL**   | $15-20     | Multi-AZ, larger instance        |
| **ECS Fargate** | $10-15     | Multiple instances, auto-scaling |
| **ALB**         | $2-3       | High availability                |
| **Lambda**      | $0.50      | Minimal usage                    |
| **Route53**     | $0.50      | Standard                         |
| **VPC & NAT**   | $3-4       | Multi-AZ setup                   |
| **Total**       | **$31-43** | Production-grade                 |

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Python 3.8+** installed (Python 3.12+ may have CDK CLI compatibility issues)
3. **AWS CDK** CLI installed globally
4. **Domain ownership** of `bluepansy.in`

> **⚠️ Python 3.12 Compatibility Note**: If you're using Python 3.12+, the CDK CLI may have syntax compatibility issues. Use the `deploy.py` script instead of direct `cdk` commands.

### Installation

```bash
# Activate the main virtual environment (from bp-be root directory)
source .venv/bin/activate

# Install Python dependencies (if not already installed)
pip install -r requirements.txt

# Install CDK globally (if not already installed)
npm install -g aws-cdk

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Deployment

#### Deploy Dev Environment

```bash
# Option 1: Use the deployment script (recommended for Python 3.12+)
python deploy.py dev

# Option 2: Manual deployment
python app.py dev
cdk deploy --all --context environment=dev

# Option 3: Direct CDK commands (may have compatibility issues with Python 3.12)
cdk synth
cdk deploy --all
```

#### Deploy Other Environments

```bash
# Deploy QA environment
python app.py qa

# Deploy Beta environment
python app.py beta

# Deploy Production environment
python app.py production
```

#### Deploy Individual Stacks

```bash
# Deploy only VPC
cdk deploy dev-vpc-stack

# Deploy only RDS
cdk deploy dev-rds-stack

# Deploy only ECS
cdk deploy dev-ecs-stack
```

## 📁 Project Structure

```
infrastructure/
├── app.py                      # Main CDK app
├── deploy.py                   # Deployment script (Python 3.12+ compatible)
├── config/
│   └── environment_config.py   # Environment configuration
├── stacks/
│   ├── vpc_stack.py           # VPC and networking
│   ├── rds_stack.py           # RDS MySQL database
│   ├── ecs_stack.py           # ECS Fargate service
│   ├── lambda_stack.py        # Lambda functions
│   └── api_stack.py           # API Gateway, Route53, SSL
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Set these environment variables before deployment:

```bash
export CDK_DEFAULT_ACCOUNT=your-aws-account-id
export CDK_DEFAULT_REGION=us-east-1
export GOOGLE_CLIENT_ID=your-google-oauth-client-id
export GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

### Customizing Environments

Edit `config/environment_config.py` to modify environment-specific settings:

```python
ENVIRONMENTS = {
    'dev': EnvironmentConfigBuilder()
        .with_environment('dev')
        .with_domain('bluepansy.in')
        .with_subdomain('dev-api')
        .with_region('us-east-1')
        .with_tags({
            'CostCenter': 'development',
            'AutoStop': 'true'
        })
        .build(),
    # ... other environments
}
```

## 🚀 Deployment Workflow

### 1. Initial Setup

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Verify configuration
cdk synth
```

### 2. Deploy Infrastructure

```bash
# Navigate to infrastructure directory
cd infrastructure

# Deploy all stacks
python app.py dev
cdk deploy --all

# Monitor deployment
aws cloudformation describe-stacks --stack-name dev-vpc-stack
```

### 3. Deploy Application

```bash
# Build Docker image
docker build -t dev-api ..

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin
docker tag dev-api:latest dev-ecr-repo:latest
docker push dev-ecr-repo:latest

# Update ECS service
aws ecs update-service --cluster dev-ecs-cluster --service dev-api-service
```

### 4. Verify Deployment

```bash
# Check ECS service status
aws ecs describe-services --cluster dev-ecs-cluster --services dev-api-service

# Test API endpoint
curl https://dev-api.bluepansy.in/health

# Check RDS status
aws rds describe-db-instances --db-instance-identifier dev-database
```

## 🔍 Monitoring & Troubleshooting

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/dev-auto-start --follow

# View ECS logs
aws logs tail /ecs/dev-api --follow
```

### ECS Service Status

```bash
# Check service status
aws ecs describe-services --cluster dev-ecs-cluster --services dev-api-service

# Check task status
aws ecs list-tasks --cluster dev-ecs-cluster --service-name dev-api-service
```

### RDS Status

```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier dev-database

# Start/stop database manually
aws rds start-db-instance --db-instance-identifier dev-database
aws rds stop-db-instance --db-instance-identifier dev-database
```

## 🧹 Cleanup

### Destroy Infrastructure

```bash
# Destroy all stacks
cdk destroy --all

# Destroy specific stack
cdk destroy dev-vpc-stack
```

### Manual Cleanup

```bash
# Delete ECR repository
aws ecr delete-repository --repository-name dev-bluepansy-api --force

# Delete RDS instance
aws rds delete-db-instance --db-instance-identifier dev-database --skip-final-snapshot
```

## 🔒 Security Features

- **VPC Isolation**: All resources in private subnets
- **Security Groups**: Restrictive access rules
- **SSL/TLS**: ACM certificates for HTTPS
- **IAM Roles**: Least privilege access
- **Encryption**: RDS encryption at rest

## 📊 Cost Optimization Features

### Dev/QA Environments

- **Auto-stop RDS**: Stops after 5 minutes of inactivity
- **Auto-stop ECS**: Scales to 0 tasks when not in use
- **Fargate Spot**: Uses spot instances for additional savings
- **Minimal Resources**: Smallest instance types

### Production Environment

- **Multi-AZ**: High availability setup
- **Auto-scaling**: Handles traffic spikes
- **Backup Retention**: 7-day backup retention
- **Performance Insights**: Database monitoring

## 🚨 Important Notes

1. **Domain Ownership**: Ensure you own `bluepansy.in` before deployment
2. **SSL Certificate**: ACM validation requires DNS access
3. **Auto-stop**: Services will be unavailable when stopped
4. **Cost Monitoring**: Set up AWS Cost Explorer alerts
5. **Backup Strategy**: No automatic backups for dev/qa environments

## 🤝 Contributing

1. **Environment Changes**: Update `config/environment_config.py`
2. **New Stacks**: Create new stack files in `stacks/`
3. **Dependencies**: Update `app.py`
4. **Testing**: Run `cdk synth` before deployment

## 📞 Support

For infrastructure issues:

1. Check CloudWatch logs
2. Verify stack dependencies
3. Review security group rules
4. Check IAM permissions

---

**Happy Deploying! 🚀**
