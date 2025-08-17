#!/usr/bin/env python3
"""
Direct Deployment Script for BluePansy Infrastructure
This script bypasses CDK CLI and uses Python CDK directly
"""

import os
import sys
import json
import boto3
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import main as create_app
from aws_cdk import App, Environment
from aws_cdk import aws_cloudformation as cfn

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ AWS User: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"❌ AWS credentials not configured or invalid: {e}")
        print("Please run: aws configure")
        return False

def check_cdk_bootstrap():
    """Check if CDK is bootstrapped by looking for the bootstrap stack"""
    try:
        cfn_client = boto3.client('cloudformation')
        response = cfn_client.describe_stacks(
            StackName='CDKToolkit'
        )
        print("✅ CDK already bootstrapped")
        return True
    except cfn_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print("❌ CDK not bootstrapped")
            print("💡 You'll need to bootstrap CDK manually or use AWS Console")
            print("   The bootstrap stack 'CDKToolkit' should exist in your account")
            return False
        else:
            print(f"❌ Error checking CDK bootstrap: {e}")
            return False

def deploy_with_cloudformation(environment):
    """Deploy using CloudFormation directly"""
    print(f"🚀 Deploying {environment.upper()} environment...")
    
    # First, synthesize the CDK app
    print("📊 Synthesizing CDK stacks...")
    try:
        # Create and synthesize the CDK app
        create_app()
        print("✅ Synthesis successful")
        
        # Check if cdk.out directory was created
        cdk_out = Path("cdk.out")
        if not cdk_out.exists():
            print("❌ CDK synthesis failed - no cdk.out directory created")
            return False
        
        print("✅ CDK templates generated successfully")
        print("📁 Templates are ready in cdk.out/ directory")
        print("\n💡 Next steps:")
        print("   1. Bootstrap CDK (if not done): aws cloudformation create-stack --template-body file://cdk.out/boostrap-template.yaml")
        print("   2. Deploy stacks manually via AWS Console or CLI")
        print("   3. Or use the CDK CLI if you can resolve the Python 3.12 compatibility issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Synthesis failed: {e}")
        return False

def main():
    """Main deployment function"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🚀 BluePansy Direct Infrastructure Deployment Script")
        print("=" * 60)
        print("This script bypasses CDK CLI compatibility issues with Python 3.12+")
        print("Usage: python deploy_direct.py <environment>")
        print("\nEnvironments:")
        print("  dev         - Development environment")
        print("  qa          - Quality Assurance environment")
        print("  beta        - Beta/Staging environment")
        print("  production  - Production environment")
        print("\nExamples:")
        print("  python deploy_direct.py dev")
        print("  python deploy_direct.py production")
        print("\nNote: This script generates CloudFormation templates without using CDK CLI")
        sys.exit(0)
    
    environment = sys.argv[1]
    valid_environments = ['dev', 'qa', 'beta', 'production']
    
    if environment not in valid_environments:
        print(f"❌ Invalid environment: {environment}")
        print(f"Valid environments: {', '.join(valid_environments)}")
        print("Run 'python deploy_direct.py --help' for usage information")
        sys.exit(1)
    
    print(f"🚀 BluePansy Direct Infrastructure Deployment")
    print(f"📍 Environment: {environment.upper()}")
    print(f"🌍 Region: ap-south-1")
    print("=" * 60)
    
    # Check prerequisites
    if not check_aws_credentials():
        sys.exit(1)
    
    if not check_cdk_bootstrap():
        print("\n⚠️  CDK bootstrap issue detected")
        print("   This script will generate templates but deployment may require manual steps")
        print("   Continue anyway? (y/N): ", end="")
        
        try:
            response = input().strip().lower()
            if response not in ['y', 'yes']:
                print("Deployment cancelled")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nDeployment cancelled")
            sys.exit(0)
    
    # Deploy infrastructure
    if deploy_with_cloudformation(environment):
        print("\n🎉 Template generation completed successfully!")
        print(f"📁 CloudFormation templates are ready in cdk.out/")
        print("🚀 You can now deploy these templates manually via AWS Console or CLI")
    else:
        print("\n❌ Template generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
