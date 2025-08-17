"""
Lambda Stack for BluePansy Infrastructure
Creates auto-start/stop Lambda functions for cost optimization
"""

from aws_cdk import (
    Stack, CfnOutput, Tags, Duration
)
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from constructs import Construct
from config.environment_config import EnvironmentConfig


class LambdaStack(Stack):
    """Lambda Stack for auto-start/stop functionality."""
    
    def __init__(self, scope: Construct, construct_id: str, config: EnvironmentConfig, 
                 vpc: ec2.Vpc, security_groups: dict, ecs_service, rds_instance, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        self.vpc = vpc
        self.security_groups = security_groups
        self.ecs_service = ecs_service
        self.rds_instance = rds_instance
        
        # Create auto-start Lambda function
        self.auto_start_lambda = lambda_.Function(
            self, 
            f"{config.environment}-auto-start",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler='index.handler',
            code=lambda_.Code.from_inline("import json\ndef handler(event, context): return {'statusCode': 200, 'body': 'Auto-start placeholder'}"),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            security_groups=[security_groups['lambda']],
            timeout=Duration.seconds(300),
            memory_size=128,
            environment={
                'ECS_CLUSTER_NAME': ecs_service.cluster.cluster_name,
                'ECS_SERVICE_NAME': ecs_service.service_name,
                'RDS_INSTANCE_ID': rds_instance.instance_identifier,
            },
        )
        
        # Create auto-stop Lambda function
        self.auto_stop_lambda = lambda_.Function(
            self, 
            f"{config.environment}-auto-stop",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler='index.handler',
            code=lambda_.Code.from_inline("import json\ndef handler(event, context): return {'statusCode': 200, 'body': 'Auto-stop placeholder'}"),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            security_groups=[security_groups['lambda']],
            timeout=Duration.seconds(300),
            memory_size=128,
            environment={
                'ECS_CLUSTER_NAME': ecs_service.cluster.cluster_name,
                'ECS_SERVICE_NAME': ecs_service.service_name,
                'RDS_INSTANCE_ID': rds_instance.instance_identifier,
            },
        )
        
        # Grant Lambda permissions
        self._grant_permissions()
        
        # Create CloudWatch Event Rule for auto-stop (only for dev/qa)
        if config.environment in ['dev', 'qa', "beta"]:
            auto_stop_rule = events.Rule(
                self, 
                f"{config.environment}-auto-stop-rule",
                schedule=events.Schedule.rate(Duration.minutes(60)),
                description=f"Auto-stop services every 60 minutes for {config.environment} environment",
            )
            
            auto_stop_rule.add_target(targets.LambdaFunction(self.auto_stop_lambda))
        
        # Add tags
        Tags.of(self.auto_start_lambda).add('Environment', config.environment)
        Tags.of(self.auto_start_lambda).add('Project', 'bluepansy')
        Tags.of(self.auto_start_lambda).add('ManagedBy', 'cdk')
        Tags.of(self.auto_start_lambda).add('Purpose', 'auto-start')
        
        Tags.of(self.auto_stop_lambda).add('Environment', config.environment)
        Tags.of(self.auto_stop_lambda).add('Project', 'bluepansy')
        Tags.of(self.auto_stop_lambda).add('ManagedBy', 'cdk')
        Tags.of(self.auto_stop_lambda).add('Purpose', 'auto-stop')
        
        # Outputs
        CfnOutput(
            self, 
            f"{config.environment}-auto-start-lambda",
            value=self.auto_start_lambda.function_name,
            description=f"Auto-start Lambda function name for {config.environment} environment",
            export_name=f"{config.environment}-auto-start-lambda",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-auto-stop-lambda",
            value=self.auto_stop_lambda.function_name,
            description=f"Auto-stop Lambda function name for {config.environment} environment",
            export_name=f"{config.environment}-auto-stop-lambda",
        )
    
    def _grant_permissions(self):
        """Grant necessary permissions to Lambda functions."""
        
        # Auto-start Lambda permissions
        self.auto_start_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'ecs:DescribeServices',
                'ecs:UpdateService',
            ],
            resources=['*'],
        ))
        
        self.auto_start_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'rds:DescribeDBInstances',
                'rds:StartDBInstance',
            ],
            resources=['*'],
        ))
        
        # Auto-stop Lambda permissions
        self.auto_stop_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'ecs:DescribeServices',
                'ecs:UpdateService',
            ],
            resources=['*'],
        ))
        
        self.auto_stop_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'rds:DescribeDBInstances',
                'rds:StopDBInstance',
            ],
            resources=['*'],
        ))
