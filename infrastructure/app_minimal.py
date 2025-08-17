#!/usr/bin/env python3
"""
Minimal CDK app to test all stacks
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
    print(f"🚀 Testing all stacks for {environment.upper()} environment...")
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
    
    # Create API Stack
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
    
    # Add dependencies
    rds_stack.add_dependency(vpc_stack)
    ecs_stack.add_dependency(vpc_stack)
    ecs_stack.add_dependency(rds_stack)
    lambda_stack.add_dependency(vpc_stack)
    lambda_stack.add_dependency(ecs_stack)
    lambda_stack.add_dependency(rds_stack)
    api_stack.add_dependency(ecs_stack)
    
    # Add tags
    Tags.of(vpc_stack).add('Environment', config.environment)
    Tags.of(vpc_stack).add('Project', 'bluepansy')
    Tags.of(vpc_stack).add('ManagedBy', 'cdk')
    
    Tags.of(rds_stack).add('Environment', config.environment)
    Tags.of(rds_stack).add('Project', 'bluepansy')
    Tags.of(rds_stack).add('ManagedBy', 'cdk')
    
    Tags.of(ecs_stack).add('Environment', config.environment)
    Tags.of(ecs_stack).add('Project', 'bluepansy')
    Tags.of(ecs_stack).add('ManagedBy', 'cdk')
    
    Tags.of(lambda_stack).add('Environment', config.environment)
    Tags.of(lambda_stack).add('Project', 'bluepansy')
    Tags.of(lambda_stack).add('ManagedBy', 'cdk')
    
    Tags.of(api_stack).add('Environment', config.environment)
    Tags.of(api_stack).add('Project', 'bluepansy')
    Tags.of(api_stack).add('ManagedBy', 'cdk')
    
    print(f"✅ All stacks created for {environment.upper()} environment")
    print(f"📋 Stack names:")
    print(f"   - {vpc_stack.stack_name}")
    print(f"   - {rds_stack.stack_name}")
    print(f"   - {ecs_stack.stack_name}")
    print(f"   - {lambda_stack.stack_name}")
    print(f"   - {api_stack.stack_name}")
    print(f"\n🚀 To deploy, run: cdk deploy --all")
    print(f"🔍 To preview changes, run: cdk diff")
    print(f"📊 To synthesize templates, run: cdk synth")
    
    app.synth()

if __name__ == '__main__':
    main()
