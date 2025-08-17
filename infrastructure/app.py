#!/usr/bin/env python3
"""
BluePansy Infrastructure as Code (CDK) - Python Version
Supports multiple environments: dev, qa, beta, production
"""

import os
import sys
from aws_cdk import (
    App, Environment, Tags
)
from stacks.vpc_stack import VpcStack
from stacks.rds_stack import RdsStack
from stacks.ecs_stack import EcsStack
from stacks.lambda_stack import LambdaStack
from stacks.api_stack import ApiStack
from config.environment_config import get_environment_config, ENVIRONMENTS

def main():
    # Get environment from command line arguments or default to 'dev'
    environment = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    
    if environment not in ENVIRONMENTS:
        print(f"❌ Unknown environment: {environment}")
        print(f"Available environments: {', '.join(ENVIRONMENTS.keys())}")
        sys.exit(1)
    
    config = get_environment_config(environment)
    print(f"🚀 Deploying {environment.upper()} environment infrastructure...")
    print(f"📍 Domain: {config.full_domain}")
    print(f"🌍 Region: {config.region}")
    
    app = App()
    
    # Create VPC Stack
    vpc_stack = VpcStack(
        app, 
        f"{config.environment}-vpc-stack",
        config=config,
        env=Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=config.region
        ),
        description=f"VPC and networking infrastructure for {config.environment} environment"
    )
    
    # Create RDS Stack
    rds_stack = RdsStack(
        app, 
        f"{config.environment}-rds-stack",
        config=config,
        vpc=vpc_stack.vpc,
        security_groups={
            'rds': vpc_stack.security_groups['rds'],
            'lambda': vpc_stack.security_groups['lambda']
        },
        env=Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=config.region
        ),
        description=f"RDS MySQL database for {config.environment} environment"
    )
    
    # Add dependency: RDS depends on VPC
    rds_stack.add_dependency(vpc_stack)
    
    # Create ECS Stack
    ecs_stack = EcsStack(
        app, 
        f"{config.environment}-ecs-stack",
        config=config,
        vpc=vpc_stack.vpc,
        security_groups={
            'ecs': vpc_stack.security_groups['ecs'],
            'alb': vpc_stack.security_groups['alb']
        },
        database=rds_stack.database,
        env=Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=config.region
        ),
        description=f"ECS Fargate service and load balancer for {config.environment} environment"
    )
    
    # Add dependency: ECS depends on VPC and RDS
    ecs_stack.add_dependency(vpc_stack)
    ecs_stack.add_dependency(rds_stack)
    
    # Create Lambda Stack
    lambda_stack = LambdaStack(
        app, 
        f"{config.environment}-lambda-stack",
        config=config,
        vpc=vpc_stack.vpc,
        security_groups={
            'lambda': vpc_stack.security_groups['lambda']
        },
        ecs_service=ecs_stack.service,
        rds_instance=rds_stack.database,
        env=Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=config.region
        ),
        description=f"Lambda functions for auto-start/stop functionality in {config.environment} environment"
    )
    
    # Add dependency: Lambda depends on VPC, ECS, and RDS
    lambda_stack.add_dependency(vpc_stack)
    lambda_stack.add_dependency(ecs_stack)
    lambda_stack.add_dependency(rds_stack)
    
    # Create API Stack (Route53, SSL, Domain)
    api_stack = ApiStack(
        app, 
        f"{config.environment}-api-stack",
        config=config,
        load_balancer=ecs_stack.load_balancer,
        target_group=ecs_stack.target_group,
        env=Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=config.region
        ),
        description=f"Domain, SSL certificate, and DNS configuration for {config.environment} environment"
    )
    
    # Add dependency: API depends on ECS
    api_stack.add_dependency(ecs_stack)
    
    # Add tags to all stacks
    all_stacks = [vpc_stack, rds_stack, ecs_stack, lambda_stack, api_stack]
    for stack in all_stacks:
        Tags.of(stack).add('Environment', config.environment)
        Tags.of(stack).add('Project', 'bluepansy')
        Tags.of(stack).add('ManagedBy', 'cdk')
        Tags.of(stack).add('CostCenter', config.tags.get('CostCenter', 'development'))
    
    print(f"✅ Infrastructure stacks created for {environment.upper()} environment")
    print(f"📋 Stack names:")
    for stack in all_stacks:
        print(f"   - {stack.stack_name}")
    print(f"\n🚀 To deploy, run: cdk deploy --all")
    print(f"🔍 To preview changes, run: cdk diff")
    print(f"📊 To synthesize templates, run: cdk synth")
    
    app.synth()

if __name__ == '__main__':
    main()
