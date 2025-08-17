"""
RDS Stack for BluePansy Infrastructure
Creates MySQL database
"""

from aws_cdk import (
    Stack, CfnOutput, Tags, Duration, RemovalPolicy
)
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from constructs import Construct
from config.environment_config import EnvironmentConfig


class RdsStack(Stack):
    """RDS Stack for MySQL database."""
    
    def __init__(self, scope: Construct, construct_id: str, config: EnvironmentConfig, 
                 vpc: ec2.Vpc, security_groups: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        self.vpc = vpc
        self.security_groups = security_groups
        
        # Create RDS instance
        self.database = rds.DatabaseInstance(
            self, 
            f"{config.environment}-database",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_39,  # Use MySQL 8.0.39 as requested
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO if 'micro' in config.rds.instance_type else ec2.InstanceSize.SMALL
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
            ),
            security_groups=[security_groups['rds']],
            allocated_storage=config.rds.allocated_storage,
            max_allocated_storage=config.rds.allocated_storage * 2,  # Allow some growth
            storage_type=rds.StorageType.GP3,
            storage_encrypted=True,
            backup_retention=Duration.days(config.rds.backup_retention),
            deletion_protection=config.rds.deletion_protection,
            removal_policy=RemovalPolicy.RETAIN if config.environment == 'production' else RemovalPolicy.DESTROY,
            database_name=f"bluepansy_{config.environment}",
            credentials=rds.Credentials.from_generated_secret('admin'),
            monitoring_interval=Duration.minutes(1),
            enable_performance_insights=config.environment == 'production',
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT if config.environment == 'production' else None,
            parameter_group=rds.ParameterGroup(
                self, 
                f"{config.environment}-db-params",
                engine=rds.DatabaseInstanceEngine.mysql(
                    version=rds.MysqlEngineVersion.VER_8_0_39,  # Use MySQL 8.0.39 as requested
                ),
                parameters={
                    'innodb_buffer_pool_size': '536870912' if config.environment == 'production' else '134217728',  # 512MB for prod, 128MB for others
                    'max_connections': '200' if config.environment == 'production' else '50',
                },
            ),
        )
        
        # Add tags
        Tags.of(self.database).add('Environment', config.environment)
        Tags.of(self.database).add('Project', 'bluepansy')
        Tags.of(self.database).add('ManagedBy', 'cdk')
        
        # Outputs
        CfnOutput(
            self, 
            f"{config.environment}-db-endpoint",
            value=self.database.instance_endpoint.hostname,
            description=f"Database endpoint for {config.environment} environment",
            export_name=f"{config.environment}-db-endpoint",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-db-port",
            value=str(self.database.instance_endpoint.port),
            description=f"Database port for {config.environment} environment",
            export_name=f"{config.environment}-db-port",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-db-name",
            value=self.database.instance_identifier,
            description=f"Database instance name for {config.environment} environment",
            export_name=f"{config.environment}-db-instance-name",
        )
