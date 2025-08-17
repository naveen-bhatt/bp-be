"""
ECS Stack for BluePansy Infrastructure
Creates ECS Fargate service and Application Load Balancer
"""

from aws_cdk import (
    Stack, CfnOutput, Tags, Duration, RemovalPolicy
)
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from constructs import Construct
from config.environment_config import EnvironmentConfig


class EcsStack(Stack):
    """ECS Stack for Fargate service and load balancer."""
    
    def __init__(self, scope: Construct, construct_id: str, config: EnvironmentConfig, 
                 vpc: ec2.Vpc, security_groups: dict, database, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        self.vpc = vpc
        self.security_groups = security_groups
        self.database = database
        
        # Create ECR Repository
        ecr_repository = ecr.Repository(
            self, 
            f"{config.environment}-ecr-repo",
            repository_name=f"{config.environment}-bluepansy-api",
            removal_policy=RemovalPolicy.DESTROY,
            image_scan_on_push=True,
        )
        
        # Create ECS Cluster
        self.cluster = ecs.Cluster(
            self, 
            f"{config.environment}-ecs-cluster",
            vpc=vpc,
            cluster_name=f"{config.environment}-bluepansy-cluster",
            container_insights_v2=ecs.ContainerInsights.ENABLED,
        )
        
        # Create Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self, 
            f"{config.environment}-task-def",
            cpu=config.ecs.cpu,
            memory_limit_mib=config.ecs.memory_limit_mib,
            execution_role=self._create_execution_role(),
            task_role=self._create_task_role(),
        )
        
        # Add container to task definition
        container = task_definition.add_container(
            f"{config.environment}-api-container",
            image=ecs.ContainerImage.from_ecr_repository(ecr_repository, 'latest'),
            container_name=f"{config.environment}-api",
            port_mappings=[ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)],
            environment={
                'ENVIRONMENT': config.environment,
                'LOG_LEVEL': 'INFO' if config.environment == 'production' else 'DEBUG',
            },
            secrets={
                'DATABASE_PASSWORD': ecs.Secret.from_secrets_manager(database.secret, 'password'),
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f"{config.environment}-api",
                log_retention=logs.RetentionDays.ONE_WEEK if config.environment == 'production' else logs.RetentionDays.THREE_DAYS,
            ),
            health_check=ecs.HealthCheck(
                command=['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )
        
        # Create Application Load Balancer
        self.load_balancer = elbv2.ApplicationLoadBalancer(
            self, 
            f"{config.environment}-alb",
            vpc=vpc,
            internet_facing=True,
            security_group=security_groups['alb'],
            load_balancer_name=f"{config.environment}-bluepansy-alb",
        )
        
        # Create Target Group
        self.target_group = elbv2.ApplicationTargetGroup(
            self, 
            f"{config.environment}-target-group",
            vpc=vpc,
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path='/health',
                port='8000',
                protocol=elbv2.Protocol.HTTP,
                healthy_http_codes='200',
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            ),
        )
        
        # Create HTTP Listener (redirects to HTTPS)
        http_listener = self.load_balancer.add_listener(
            f"{config.environment}-http-listener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_action=elbv2.ListenerAction.redirect(
                protocol='HTTPS',
                port='443',
                permanent=True,
            ),
        )
        
        # Create a second HTTP listener that forwards to the target group
        # This ensures the target group is properly associated with the load balancer
        # We'll manually create the HTTPS listener after deployment with the certificate
        self.target_listener = self.load_balancer.add_listener(
            f"{config.environment}-target-listener",
            port=8080,  # Use a different port to avoid conflicts
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_action=elbv2.ListenerAction.forward([self.target_group]),
        )
        
        # Create ECS Service
        self.service = ecs.FargateService(
            self, 
            f"{config.environment}-ecs-service",
            cluster=self.cluster,
            task_definition=task_definition,
            service_name=f"{config.environment}-bluepansy-service",
            desired_count=config.ecs.desired_count,
            security_groups=[security_groups['ecs']],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            assign_public_ip=False,
            enable_execute_command=True,
        )
        
        # Attach service to target group AFTER the target group is properly associated with the load balancer
        self.service.attach_to_application_target_group(self.target_group)
        
        # Add tags
        Tags.of(self.cluster).add('Environment', config.environment)
        Tags.of(self.cluster).add('Project', 'bluepansy')
        Tags.of(self.cluster).add('ManagedBy', 'cdk')
        
        Tags.of(self.service).add('Environment', config.environment)
        Tags.of(self.service).add('Project', 'bluepansy')
        Tags.of(self.service).add('ManagedBy', 'cdk')
        
        Tags.of(self.load_balancer).add('Environment', config.environment)
        Tags.of(self.load_balancer).add('Project', 'bluepansy')
        Tags.of(self.load_balancer).add('ManagedBy', 'cdk')
        
        # Outputs
        CfnOutput(
            self, 
            f"{config.environment}-cluster-name",
            value=self.cluster.cluster_name,
            description=f"ECS cluster name for {config.environment} environment",
            export_name=f"{config.environment}-cluster-name",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-service-name",
            value=self.service.service_name,
            description=f"ECS service name for {config.environment} environment",
            export_name=f"{config.environment}-service-name",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-alb-dns",
            value=self.load_balancer.load_balancer_dns_name,
            description=f"ALB DNS name for {config.environment} environment",
            export_name=f"{config.environment}-alb-dns",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-ecr-repo-uri",
            value=ecr_repository.repository_uri,
            description=f"ECR repository URI for {config.environment} environment",
            export_name=f"{config.environment}-ecr-repo-uri",
        )
    
    def _create_execution_role(self) -> iam.Role:
        """Create execution role for ECS tasks."""
        return iam.Role(
            self, 
            f"{self.config.environment}-ecs-execution-role",
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonECSTaskExecutionRolePolicy'),
            ],
        )
    
    def _create_task_role(self) -> iam.Role:
        """Create task role for ECS tasks."""
        return iam.Role(
            self, 
            f"{self.config.environment}-ecs-task-role",
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3ReadOnlyAccess'),
            ],
        )
