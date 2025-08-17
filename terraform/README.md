# BluePansy Infrastructure as Code (Terraform)

This directory contains Terraform configurations for deploying the BluePansy application infrastructure across multiple environments.

## 🏗️ **Architecture Overview**

The infrastructure includes:

- **ECS Fargate Cluster** - Container orchestration
- **Application Load Balancer (ALB)** - Traffic distribution
- **ECR Repository** - Container image storage
- **RDS Database** - Data persistence (referenced from existing CDK)
- **Lambda Functions** - Auto-start/stop for cost optimization
- **CloudWatch Events** - Scheduled automation
- **IAM Roles & Policies** - Security and permissions
- **Parameter Store** - Environment configuration
- **Secrets Manager** - Sensitive data storage

## 🌍 **Multi-Environment Support**

### **Supported Environments:**

- **`dev`** - Development environment (1 instance, auto-stop after 60 min)
- **`qa`** - Quality Assurance environment (1 instance, auto-stop after 60 min)
- **`beta`** - Beta testing environment (1 instance, auto-stop after 60 min)
- **`prod`** - Production environment (2 instances, always running)

### **Environment-Specific Configurations:**

| Environment | CPU | Memory | Instances | Auto-Stop | Cost Profile |
| ----------- | --- | ------ | --------- | --------- | ------------ |
| `dev`       | 256 | 512MB  | 1         | ✅ 60min  | 💰 Minimal   |
| `qa`        | 256 | 512MB  | 1         | ✅ 60min  | 💰 Minimal   |
| `beta`      | 256 | 512MB  | 1         | ✅ 60min  | 💰 Minimal   |
| `prod`      | 512 | 1GB    | 2         | ❌ Always | 💰 Standard  |

## 🏷️ **Naming Convention**

### **Resource Naming Pattern:**

```
{environment}-{project}-{resource-type}
```

### **Examples:**

- **ECS Cluster**: `dev-bluepansy-cluster`
- **Load Balancer**: `dev-bluepansy-alb`
- **ECR Repository**: `dev-bluepansy-api`
- **ECS Service**: `dev-bluepansy-service`
- **Target Group**: `dev-bluepansy-tg`
- **IAM Role**: `dev-bluepansy-ecs-execution-role`
- **Lambda Function**: `dev-bluepansy-auto-stop`

### **Parameter Store Paths:**

- **Environment Variables**: `/{environment}/*`
- **Examples**: `/dev/secret_key`, `/prod/database_url`

### **Benefits of This Convention:**

- ✅ **Environment Isolation** - No naming conflicts
- ✅ **Easy Identification** - Clear resource ownership
- ✅ **Scalable** - Easy to add new environments
- ✅ **Consistent** - Predictable resource names
- ✅ **Filterable** - Easy to filter by environment

## 🚀 **Quick Start**

### **Prerequisites:**

- Terraform >= 1.0
- AWS CLI configured
- `jq` command-line tool
- Python 3.9+ and pip (for Lambda packaging)

### **1. Deploy Development Environment:**

```bash
cd terraform
./deploy-dev.sh
```

### **2. Deploy Other Environments:**

```bash
# QA Environment
./deploy-qa.sh

# Beta Environment
./deploy-beta.sh

# Production Environment
./deploy-prod.sh
```

## 📁 **Directory Structure**

```
terraform/
├── environments/
│   ├── dev/           # Development environment
│   ├── qa/            # QA environment
│   ├── beta/          # Beta environment
│   └── prod/          # Production environment
├── lambda_functions/  # Lambda function source code
├── deploy-dev.sh      # Dev deployment script
├── deploy-qa.sh       # QA deployment script
├── deploy-beta.sh     # Beta deployment script
├── deploy-prod.sh     # Production deployment script
├── build-lambda.sh    # Lambda packaging script
├── validate-infrastructure.sh  # Post-deployment validation
└── README.md          # This file
```

## 🔧 **Configuration Management**

### **Environment Variables:**

Each environment has its own `variables.tf` file with:

- **`environment`** - Environment name (dev/qa/beta/prod)
- **`project`** - Project name (bluepansy)
- **`aws_region`** - AWS region (ap-south-1)
- **`ecs_cpu`** - CPU units for ECS tasks
- **`ecs_memory`** - Memory allocation for ECS tasks
- **`ecs_desired_count`** - Number of ECS instances

### **Parameter Store Setup:**

Before deploying, ensure Parameter Store has environment-specific parameters:

```bash
# Example for dev environment
aws ssm put-parameter --name "/dev/secret_key" --value "your-secret" --type SecureString
aws ssm put-parameter --name "/dev/database_url" --value "mysql://..." --type SecureString
# ... other parameters
```

## 💰 **Cost Optimization Features**

### **Auto-Stop/Start:**

- **ECS Services** scale to 0 instances after 60 minutes of inactivity
- **RDS Instances** stop automatically when not in use
- **Lambda Functions** trigger on ALB activity to restart services

### **Resource Sizing:**

- **Dev/QA/Beta**: Minimal resources (256 CPU, 512MB RAM)
- **Production**: Adequate resources (512 CPU, 1GB RAM) with redundancy

## 🔒 **Security Features**

### **Network Security:**

- **Private Subnets** for ECS tasks
- **Public Subnets** for ALB only
- **Security Groups** with minimal required access

### **IAM Security:**

- **Least Privilege** principle
- **Environment-Specific** policies
- **Parameter Store** integration for secrets

## 📊 **Monitoring & Logging**

### **CloudWatch Integration:**

- **ECS Container Logs** - Application logs
- **Lambda Function Logs** - Auto-start/stop logs
- **ALB Access Logs** - Traffic monitoring
- **Custom Metrics** - Resource utilization

### **Health Checks:**

- **ALB Health Checks** - `/health` endpoint
- **ECS Service Health** - Task health monitoring
- **Lambda Function Health** - Execution monitoring

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. Resource Naming Conflicts:**

```bash
# Check if resources exist
aws ecs describe-clusters --clusters dev-bluepansy-cluster
aws elbv2 describe-load-balancers --names dev-bluepansy-alb
```

#### **2. Parameter Store Missing:**

```bash
# Verify parameters exist
aws ssm get-parameter --name "/dev/database_url"
```

#### **3. Lambda Functions Not Working:**

```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/dev-bluepansy"
```

### **Validation Commands:**

```bash
# Validate infrastructure
./validate-infrastructure.sh dev

# Check ECS service status
aws ecs describe-services --cluster dev-bluepansy-cluster --services dev-bluepansy-service
```

## 🔄 **Updating Infrastructure**

### **Modify Configuration:**

1. Edit the appropriate `main.tf` file
2. Run `terraform plan` to see changes
3. Run `terraform apply` to apply changes

### **Destroy Infrastructure:**

```bash
cd environments/dev
terraform destroy
```

## 📚 **Additional Resources**

- **Terraform Documentation**: https://www.terraform.io/docs
- **AWS ECS Documentation**: https://docs.aws.amazon.com/ecs/
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/

## 🤝 **Contributing**

When adding new environments or modifying existing ones:

1. **Follow naming conventions** strictly
2. **Update this README** with new information
3. **Test in dev first** before applying to other environments
4. **Document any changes** in commit messages

---

**Note**: This infrastructure is designed to be **idempotent** and **environment-agnostic**. Each environment can be deployed independently without affecting others.
