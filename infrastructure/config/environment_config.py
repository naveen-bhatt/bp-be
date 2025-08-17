"""
Environment configuration for different deployment stages
Supports: dev, qa, beta, production
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from aws_cdk import Duration


@dataclass
class VpcConfig:
    """VPC configuration settings."""
    max_azs: int
    nat_gateways: int
    cidr: str


@dataclass
class RdsConfig:
    """RDS configuration settings."""
    instance_type: str
    allocated_storage: int
    multi_az: bool
    backup_retention: int
    deletion_protection: bool
    auto_stop: bool
    auto_stop_minutes: int
    mysql_version: str


@dataclass
class EcsConfig:
    """ECS configuration settings."""
    cpu: int
    memory_limit_mib: int
    desired_count: int
    max_capacity: int
    min_capacity: int
    enable_auto_scaling: bool
    use_spot: bool


@dataclass
class LambdaConfig:
    """Lambda configuration settings."""
    memory_size: int
    timeout: Duration
    runtime: str


@dataclass
class MonitoringConfig:
    """Monitoring configuration settings."""
    enable_detailed_monitoring: bool
    enable_logging: bool
    retention_days: int


@dataclass
class EnvironmentConfig:
    """Complete environment configuration."""
    environment: str
    domain: str
    subdomain: str
    full_domain: str
    region: str
    vpc: VpcConfig
    rds: RdsConfig
    ecs: EcsConfig
    lambda_config: LambdaConfig
    monitoring: MonitoringConfig
    tags: Dict[str, str]


class EnvironmentConfigBuilder:
    """Builder class for environment configuration."""
    
    def __init__(self):
        self.config = {}
    
    def with_environment(self, env: str) -> 'EnvironmentConfigBuilder':
        """Set the environment name."""
        self.config['environment'] = env
        return self
    
    def with_domain(self, domain: str) -> 'EnvironmentConfigBuilder':
        """Set the domain name."""
        self.config['domain'] = domain
        return self
    
    def with_subdomain(self, subdomain: str) -> 'EnvironmentConfigBuilder':
        """Set the subdomain."""
        self.config['subdomain'] = subdomain
        return self
    
    def with_region(self, region: str) -> 'EnvironmentConfigBuilder':
        """Set the AWS region."""
        self.config['region'] = region
        return self
    
    def with_vpc(self, config: VpcConfig) -> 'EnvironmentConfigBuilder':
        """Set VPC configuration."""
        self.config['vpc'] = config
        return self
    
    def with_rds(self, config: RdsConfig) -> 'EnvironmentConfigBuilder':
        """Set RDS configuration."""
        self.config['rds'] = config
        return self
    
    def with_ecs(self, config: EcsConfig) -> 'EnvironmentConfigBuilder':
        """Set ECS configuration."""
        self.config['ecs'] = config
        return self
    
    def with_lambda(self, config: LambdaConfig) -> 'EnvironmentConfigBuilder':
        """Set Lambda configuration."""
        self.config['lambda'] = config
        return self
    
    def with_monitoring(self, config: MonitoringConfig) -> 'EnvironmentConfigBuilder':
        """Set monitoring configuration."""
        self.config['monitoring'] = config
        return self
    
    def with_tags(self, tags: Dict[str, str]) -> 'EnvironmentConfigBuilder':
        """Set environment tags."""
        self.config['tags'] = tags
        return self
    
    def build(self) -> EnvironmentConfig:
        """Build the environment configuration."""
        if not all(key in self.config for key in ['environment', 'domain', 'subdomain']):
            raise ValueError('Environment, domain, and subdomain are required')
        
        env = self.config['environment']
        domain = self.config['domain']
        subdomain = self.config['subdomain']
        
        return EnvironmentConfig(
            environment=env,
            domain=domain,
            subdomain=subdomain,
            full_domain=f"{subdomain}.{domain}",
            region=self.config.get('region', 'ap-south-1'),
            vpc=self.config.get('vpc', self._get_default_vpc_config(env)),
            rds=self.config.get('rds', self._get_default_rds_config(env)),
            ecs=self.config.get('ecs', self._get_default_ecs_config(env)),
            lambda_config=self.config.get('lambda', self._get_default_lambda_config(env)),
            monitoring=self.config.get('monitoring', self._get_default_monitoring_config(env)),
            tags={
                'Environment': env,
                'Project': 'bluepansy',
                'ManagedBy': 'cdk',
                **self.config.get('tags', {})
            }
        )
    
    def _get_default_vpc_config(self, env: str) -> VpcConfig:
        """Get default VPC configuration for environment."""
        return VpcConfig(
            max_azs=2,
            nat_gateways=2 if env == 'production' else 1,
            cidr='10.0.0.0/16'
        )
    
    def _get_default_rds_config(self, env: str) -> RdsConfig:
        """Get default RDS configuration for environment."""
        is_production = env == 'production'
        is_dev = env == 'dev'
        
        return RdsConfig(
            instance_type='db.t3.small' if is_production else 'db.t3.micro',
            allocated_storage=100 if is_production else 20,
            multi_az=is_production,
            backup_retention=7 if is_production else 0,
            deletion_protection=is_production,
            auto_stop=is_dev or env == 'qa',
            auto_stop_minutes=60,
            mysql_version='8.0.39'  # Use MySQL 8.0.39 as requested
        )
    
    def _get_default_ecs_config(self, env: str) -> EcsConfig:
        """Get default ECS configuration for environment."""
        is_production = env == 'production'
        is_dev = env == 'dev'
        
        return EcsConfig(
            cpu=512 if is_production else 256,
            memory_limit_mib=1024 if is_production else 512,
            desired_count=2 if is_production else 1,
            max_capacity=4 if is_production else 1,
            min_capacity=1 if is_production else 0,
            enable_auto_scaling=is_production,
            use_spot=not is_production
        )
    
    def _get_default_lambda_config(self, env: str) -> LambdaConfig:
        """Get default Lambda configuration for environment."""
        return LambdaConfig(
            memory_size=128,
            timeout=Duration.seconds(300),
            runtime='python3.11'
        )
    
    def _get_default_monitoring_config(self, env: str) -> MonitoringConfig:
        """Get default monitoring configuration for environment."""
        is_production = env == 'production'
        
        return MonitoringConfig(
            enable_detailed_monitoring=is_production,
            enable_logging=True,
            retention_days=30 if is_production else 7
        )


# Predefined environment configurations
ENVIRONMENTS = {
    'dev': EnvironmentConfigBuilder()
        .with_environment('dev')
        .with_domain('bluepansy.in')
        .with_subdomain('dev-api')
        .with_region('ap-south-1')
        .with_tags({
            'CostCenter': 'development',
            'AutoStop': 'true'
        })
        .build(),

    'qa': EnvironmentConfigBuilder()
        .with_environment('qa')
        .with_domain('bluepansy.in')
        .with_subdomain('qa-api')
        .with_region('ap-south-1')
        .with_tags({
            'CostCenter': 'testing',
            'AutoStop': 'true'
        })
        .build(),

    'beta': EnvironmentConfigBuilder()
        .with_environment('beta')
        .with_domain('bluepansy.in')
        .with_subdomain('beta-api')
        .with_region('ap-south-1')
        .with_tags({
            'CostCenter': 'staging',
            'AutoStop': 'false'
        })
        .build(),

    'production': EnvironmentConfigBuilder()
        .with_environment('production')
        .with_domain('bluepansy.in')
        .with_subdomain('api')
        .with_region('ap-south-1')
        .with_tags({
            'CostCenter': 'production',
            'AutoStop': 'false'
        })
        .build()
}


def get_environment_config(env: str) -> EnvironmentConfig:
    """Get environment configuration by name."""
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: {env}. Available: {', '.join(ENVIRONMENTS.keys())}")
    return ENVIRONMENTS[env]
