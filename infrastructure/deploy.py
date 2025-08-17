#!/usr/bin/env python3
"""
Deployment script for BluePansy Infrastructure
This script works around CDK CLI compatibility issues with Python 3.12
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), result.stderr.strip(), 0
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    stdout, stderr, code = run_command("aws sts get-caller-identity")
    if code != 0:
        print("❌ AWS credentials not configured or invalid")
        print("Please run: aws configure")
        return False
    
    try:
        identity = json.loads(stdout)
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ AWS User: {identity['Arn']}")
        return True
    except json.JSONDecodeError:
        print("❌ Failed to parse AWS identity")
        return False

def bootstrap_cdk():
    """Bootstrap CDK if needed"""
    print("🔧 Checking CDK bootstrap status...")
    stdout, stderr, code = run_command("cdk bootstrap --list")
    
    if "No environments bootstrapped" in stdout or code != 0:
        print("🚀 Bootstrapping CDK...")
        stdout, stderr, code = run_command("cdk bootstrap")
        if code == 0:
            print("✅ CDK bootstrapped successfully")
            return True
        else:
            print(f"❌ CDK bootstrap failed: {stderr}")
            return False
    else:
        print("✅ CDK already bootstrapped")
        return True

def deploy_stacks(environment):
    """Deploy all stacks for the given environment"""
    print(f"🚀 Deploying {environment.upper()} environment...")
    
    # First, synthesize to check for errors
    print("📊 Synthesizing CDK stacks...")
    stdout, stderr, code = run_command("cdk synth")
    
    if code != 0:
        print(f"❌ Synthesis failed: {stderr}")
        print("💡 Try running: python app.py {environment}")
        return False
    
    print("✅ Synthesis successful")
    
    # Deploy all stacks
    print("🚀 Deploying infrastructure...")
    stdout, stderr, code = run_command("cdk deploy --all --require-approval never")
    
    if code == 0:
        print("✅ Deployment successful!")
        return True
    else:
        print(f"❌ Deployment failed: {stderr}")
        return False

def main():
    """Main deployment function"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🚀 BluePansy Infrastructure Deployment Script")
        print("=" * 50)
        print("Usage: python deploy.py <environment>")
        print("\nEnvironments:")
        print("  dev         - Development environment")
        print("  qa          - Quality Assurance environment")
        print("  beta        - Beta/Staging environment")
        print("  production  - Production environment")
        print("\nExamples:")
        print("  python deploy.py dev")
        print("  python deploy.py production")
        print("\nNote: This script works around CDK CLI compatibility issues with Python 3.12+")
        sys.exit(0)
    
    environment = sys.argv[1]
    valid_environments = ['dev', 'qa', 'beta', 'production']
    
    if environment not in valid_environments:
        print(f"❌ Invalid environment: {environment}")
        print(f"Valid environments: {', '.join(valid_environments)}")
        print("Run 'python deploy.py --help' for usage information")
        sys.exit(1)
    
    print(f"🚀 BluePansy Infrastructure Deployment")
    print(f"📍 Environment: {environment.upper()}")
    print(f"🌍 Region: ap-south-1")
    print("=" * 50)
    
    # Check prerequisites
    if not check_aws_credentials():
        sys.exit(1)
    
    if not bootstrap_cdk():
        sys.exit(1)
    
    # Deploy infrastructure
    if deploy_stacks(environment):
        print("\n🎉 Deployment completed successfully!")
        print(f"🌐 Your {environment} environment should be available soon")
        print("📊 Check AWS Console for deployment status")
    else:
        print("\n❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
