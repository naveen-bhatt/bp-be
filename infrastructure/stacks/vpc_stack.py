"""
VPC Stack for BluePansy Infrastructure
Creates VPC, subnets, and security groups
"""

from aws_cdk import (
    Stack, CfnOutput, Tags
)
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from config.environment_config import EnvironmentConfig


class VpcStack(Stack):
    """VPC Stack for networking infrastructure."""
    
    def __init__(self, scope: Construct, construct_id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # Create VPC
        self.vpc = ec2.Vpc(
            self, 
            f"{config.environment}-vpc",
            ip_addresses=ec2.IpAddresses.cidr(config.vpc.cidr),
            max_azs=config.vpc.max_azs,
            nat_gateways=config.vpc.nat_gateways,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='isolated',
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )
        
        # Create Security Groups
        self.security_groups = {
            # ECS Security Group
            'ecs': ec2.SecurityGroup(
                self, 
                f"{config.environment}-ecs-sg",
                vpc=self.vpc,
                description=f"Security group for {config.environment} ECS tasks",
                allow_all_outbound=True,
            ),
            
            # RDS Security Group
            'rds': ec2.SecurityGroup(
                self, 
                f"{config.environment}-rds-sg",
                vpc=self.vpc,
                description=f"Security group for {config.environment} RDS instance",
                allow_all_outbound=False,
            ),
            
            # Lambda Security Group
            'lambda': ec2.SecurityGroup(
                self, 
                f"{config.environment}-lambda-sg",
                vpc=self.vpc,
                description=f"Security group for {config.environment} Lambda functions",
                allow_all_outbound=True,
            ),
            
            # ALB Security Group
            'alb': ec2.SecurityGroup(
                self, 
                f"{config.environment}-alb-sg",
                vpc=self.vpc,
                description=f"Security group for {config.environment} Application Load Balancer",
                allow_all_outbound=True,
            ),
        }
        
        # Configure Security Group Rules
        
        # ALB Security Group - Allow HTTP/HTTPS from internet
        self.security_groups['alb'].add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            'Allow HTTP from internet'
        )
        self.security_groups['alb'].add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            'Allow HTTPS from internet'
        )
        
        # ECS Security Group - Allow traffic from ALB
        self.security_groups['ecs'].add_ingress_rule(
            self.security_groups['alb'],
            ec2.Port.tcp(8000),  # Assuming your app runs on port 8000
            'Allow traffic from ALB'
        )
        
        # RDS Security Group - Allow MySQL from ECS
        self.security_groups['rds'].add_ingress_rule(
            self.security_groups['ecs'],
            ec2.Port.tcp(3306),
            'Allow MySQL access from ECS'
        )
        
        # Lambda Security Group - Allow access to ECS and RDS
        self.security_groups['lambda'].add_ingress_rule(
            self.security_groups['ecs'],
            ec2.Port.tcp(8000),
            'Allow Lambda to access ECS'
        )
        
        # Add tags
        Tags.of(self).add('Environment', config.environment)
        Tags.of(self).add('Project', 'bluepansy')
        Tags.of(self).add('ManagedBy', 'cdk')
        
        # Outputs
        CfnOutput(
            self, 
            f"{config.environment}-vpc-id",
            value=self.vpc.vpc_id,
            description=f"VPC ID for {config.environment} environment",
            export_name=f"{config.environment}-vpc-id",
        )
        
        # Note: Subnet outputs removed to avoid token validation issues
        # Subnets can be accessed via VPC object directly
