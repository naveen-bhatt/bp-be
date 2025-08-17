# GitHub Secrets Configuration

This document outlines the GitHub secrets required for the deployment pipelines to work correctly.

## 🔐 Required Secrets

### **AWS Credentials**

These secrets are required for all deployment workflows:

| Secret Name             | Description                          | Example                                    |
| ----------------------- | ------------------------------------ | ------------------------------------------ |
| `AWS_ACCESS_KEY_ID`     | AWS Access Key ID for deployment     | `AKIAIOSFODNN7EXAMPLE`                     |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key for deployment | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_ACCOUNT_ID`        | Your AWS Account ID                  | `123456789012`                             |

## 🚀 How to Configure Secrets

### **Step 1: Create AWS IAM User**

1. Go to AWS IAM Console
2. Create a new user with programmatic access
3. Attach the following policies:
   - `AdministratorAccess` (for full deployment access)
   - Or create a custom policy with specific permissions

### **Step 2: Add Secrets to GitHub**

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact names above

## 🔒 Security Best Practices

### **IAM Policy Recommendations**

Instead of `AdministratorAccess`, consider creating a custom policy with minimal required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "ecs:*",
        "ecr:*",
        "rds:*",
        "ec2:*",
        "elasticloadbalancing:*",
        "route53:*",
        "acm:*",
        "lambda:*",
        "events:*",
        "logs:*",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

### **Secret Rotation**

- Rotate AWS access keys regularly (every 90 days)
- Use temporary credentials when possible
- Monitor AWS CloudTrail for unauthorized access

## 🧪 Testing Secrets

You can test if your secrets are configured correctly by:

1. **Manual Workflow Trigger**: Use the "workflow_dispatch" trigger
2. **Check Logs**: Look for AWS credential errors in workflow logs
3. **Test Deployment**: Try deploying to dev environment first

## 📋 Environment-Specific Secrets

The current setup uses the same AWS credentials for all environments. If you need different credentials per environment, you can:

1. **Create environment-specific secrets**:

   - `DEV_AWS_ACCESS_KEY_ID`
   - `QA_AWS_ACCESS_KEY_ID`
   - `BETA_AWS_ACCESS_KEY_ID`
   - `PROD_AWS_ACCESS_KEY_ID`

2. **Update workflows** to use environment-specific secrets

## 🚨 Troubleshooting

### **Common Issues**

1. **"Invalid credentials" error**

   - Check if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are correct
   - Verify the IAM user has necessary permissions

2. **"Access denied" error**

   - Ensure the IAM user has the required policies attached
   - Check if the AWS account ID is correct

3. **"Region not found" error**
   - Verify the AWS_REGION in the workflow matches your AWS setup
   - Ensure the region supports all required AWS services

### **Getting Help**

- Check GitHub Actions logs for detailed error messages
- Verify AWS credentials work locally with `aws configure`
- Test AWS CLI commands manually before running workflows
