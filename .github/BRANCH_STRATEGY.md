# Branch Strategy & Deployment Workflow

This document outlines the Git branching strategy and deployment workflow for the BluePansy project.

## 🌿 Branch Structure

### **Main Branches**

```
main (production)
├── production (production deployment)
├── beta (staging/pre-production)
├── qa (quality assurance)
└── dev (development)
```

### **Feature Branches**

```
feature/feature-name
├── dev (merge target for features)
└── main (merge target for production)
```

## 🚀 Deployment Workflow

### **Infrastructure Setup (Local, One-time)**

- **Method**: CDK deployment from local machine
- **Purpose**: Create all AWS resources (VPC, RDS, ECS, etc.)
- **Command**: `cdk deploy --all --context environment=<env>`

### **Application Deployment (GitHub Actions, Automatic)**

#### **1. Development Environment (`dev` branch)**

- **Trigger**: Push to `dev` branch
- **Purpose**: Development and testing
- **Auto-deploy**: ✅ Yes
- **Domain**: `dev-api.bluepansy.in`
- **ECS**: `dev-bluepansy-cluster` → `dev-bluepansy-service`
- **ECR**: `dev-bluepansy-api`

**Workflow**: `.github/workflows/deploy-app-dev.yml`

#### **2. QA Environment (`qa` branch)**

- **Trigger**: Push to `qa` branch
- **Purpose**: Quality assurance and testing
- **Auto-deploy**: ✅ Yes
- **Domain**: `qa-api.bluepansy.in`
- **ECS**: `qa-bluepansy-cluster` → `qa-bluepansy-service`
- **ECR**: `qa-bluepansy-api`

**Workflow**: `.github/workflows/deploy-app-qa.yml`

#### **3. Beta Environment (`beta` branch)**

- **Trigger**: Push to `beta` branch
- **Purpose**: Staging and pre-production testing
- **Auto-deploy**: ✅ Yes
- **Domain**: `beta-api.bluepansy.in`
- **ECS**: `beta-bluepansy-cluster` → `beta-bluepansy-service`
- **ECR**: `beta-bluepansy-api`

**Workflow**: `.github/workflows/deploy-app-beta.yml`

#### **4. Production Environment (`main` branch)**

- **Trigger**: Push to `main` branch
- **Purpose**: Production deployment
- **Auto-deploy**: ✅ Yes
- **Domain**: `api.bluepansy.in`
- **ECS**: `production-bluepansy-cluster` → `production-bluepansy-service`
- **ECR**: `production-bluepansy-api`

**Workflow**: `.github/workflows/deploy-app-production.yml`

## 🔄 Development Process

### **Feature Development**

```
1. Create feature branch from dev
   git checkout -b feature/new-feature dev

2. Develop and test locally
   git add .
   git commit -m "Add new feature"

3. Push to feature branch
   git push origin feature/new-feature

4. Create Pull Request to dev branch
   (GitHub will show PR creation form)

5. Code review and merge to dev
   (Triggers dev deployment automatically)
```

### **Promoting to Higher Environments**

```
1. Merge dev → qa
   git checkout qa
   git merge dev
   git push origin qa
   (Triggers qa deployment)

2. Merge qa → beta
   git checkout beta
   git merge qa
   git push origin beta
   (Triggers beta deployment)

3. Merge beta → main
   git checkout main
   git merge beta
   git push origin main
   (Triggers production deployment)
```

## 📋 Deployment Checklist

### **Before Deploying to Production**

- [ ] All tests pass in dev environment
- [ ] QA testing completed successfully
- [ ] Beta environment tested and stable
- [ ] Database migrations tested
- [ ] Performance testing completed
- [ ] Security review completed
- [ ] Documentation updated

### **Production Deployment Steps**

1. **Code Review**: Ensure all changes are reviewed
2. **Merge to main**: Merge from beta branch
3. **Monitor Deployment**: Watch GitHub Actions workflow
4. **Health Checks**: Verify production endpoints
5. **Smoke Tests**: Run basic functionality tests
6. **Monitor Logs**: Check for any errors

## 🚨 Rollback Strategy

### **Quick Rollback**

If a production deployment fails:

1. **Revert the merge**:

   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Manual rollback** (if needed):
   ```bash
   # Rollback to previous ECS deployment
   aws ecs update-service --cluster production-bluepansy-cluster --service production-bluepansy-service --task-definition <previous-task-definition>
   ```

### **Database Rollback**

- **RDS Snapshots**: Use point-in-time recovery
- **Migrations**: Revert database schema changes
- **Data**: Restore from backup if necessary

## 🔍 Monitoring & Alerts

### **Deployment Monitoring**

- **GitHub Actions**: Monitor workflow success/failure
- **AWS CloudWatch**: Monitor resource health
- **Application Logs**: Monitor application performance
- **Health Checks**: Automated endpoint monitoring

### **Alerting**

- **Deployment Failures**: Immediate notification
- **Service Health**: Monitor ECS service status
- **Database Issues**: RDS performance alerts
- **Cost Alerts**: Monitor AWS spending

## 📚 Best Practices

### **Code Quality**

- **Linting**: Use pre-commit hooks
- **Testing**: Write unit and integration tests
- **Code Review**: Require PR reviews
- **Documentation**: Keep docs updated

### **Security**

- **Secrets Management**: Use GitHub secrets
- **IAM Policies**: Principle of least privilege
- **Network Security**: VPC and security groups
- **SSL/TLS**: Always use HTTPS

### **Performance**

- **Resource Optimization**: Right-size instances
- **Auto-scaling**: Use ECS auto-scaling
- **Caching**: Implement appropriate caching
- **Monitoring**: Track performance metrics

## 🆘 Troubleshooting

### **Common Issues**

1. **Deployment Stuck**

   - Check ECS service status
   - Verify ECR image availability
   - Review CloudWatch logs

2. **Service Unhealthy**

   - Review ECS task logs
   - Check health check endpoints
   - Verify security group rules

3. **Database Issues**
   - Check RDS instance status
   - Review CloudWatch metrics
   - Verify connection strings

### **Getting Help**

- **GitHub Issues**: Create detailed bug reports
- **AWS Support**: Use AWS support if needed
- **Team Chat**: Coordinate with team members
- **Documentation**: Check this guide first
