"""
API Stack for BluePansy Infrastructure
Handles Route53, ACM SSL certificates, and domain configuration
"""

from aws_cdk import (
    Stack, CfnOutput, Tags
)
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct
from config.environment_config import EnvironmentConfig


class ApiStack(Stack):
    """API Stack for domain and SSL configuration."""
    
    def __init__(self, scope: Construct, construct_id: str, config: EnvironmentConfig, 
                 load_balancer: elbv2.ApplicationLoadBalancer, target_group: elbv2.ApplicationTargetGroup, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        self.load_balancer = load_balancer
        self.target_group = target_group
        
        # Create new hosted zone for the domain
        # Note: This will create a new hosted zone. You'll need to update your domain's nameservers
        # to point to the AWS nameservers after deployment
        self.hosted_zone = route53.HostedZone(
            self, 
            f"{config.environment}-hosted-zone",
            zone_name=config.domain,
        )
        
        # Create ACM certificate for the subdomain
        self.certificate = acm.Certificate(
            self, 
            f"{config.environment}-certificate",
            domain_name=config.full_domain,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
            subject_alternative_names=[config.domain],  # Also cover root domain
        )
        
        # Note: HTTPS Listener is created by ECS stack
        # Certificate will be attached during deployment
        
        # Create A record for subdomain pointing to ALB
        self.subdomain_record = route53.ARecord(
            self, 
            f"{config.environment}-subdomain-record",
            zone=self.hosted_zone,
            record_name=config.subdomain,
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(self.load_balancer)
            ),
        )
        
        # Create A record for root domain pointing to ALB
        self.root_record = route53.ARecord(
            self, 
            f"{config.environment}-root-record",
            zone=self.hosted_zone,
            record_name="",  # Root domain
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(self.load_balancer)
            ),
        )
        
        # Add tags
        Tags.of(self.hosted_zone).add('Environment', config.environment)
        Tags.of(self.hosted_zone).add('Project', 'bluepansy')
        Tags.of(self.hosted_zone).add('ManagedBy', 'cdk')
        
        Tags.of(self.certificate).add('Environment', config.environment)
        Tags.of(self.certificate).add('Project', 'bluepansy')
        Tags.of(self.certificate).add('ManagedBy', 'cdk')
        
        # Outputs
        CfnOutput(
            self, 
            f"{config.environment}-full-domain",
            value=config.full_domain,
            description=f"Full domain for {config.environment} environment",
            export_name=f"{config.environment}-full-domain",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-certificate-arn",
            value=self.certificate.certificate_arn,
            description=f"SSL certificate ARN for {config.environment} environment",
            export_name=f"{config.environment}-certificate-arn",
        )
        
        CfnOutput(
            self, 
            f"{config.environment}-hosted-zone-id",
            value=self.hosted_zone.hosted_zone_id,
            description=f"Route53 hosted zone ID for {config.environment} environment",
            export_name=f"{config.environment}-hosted-zone-id",
        )
        
        # Note: Nameservers output removed to avoid token validation issues
        # Nameservers can be accessed via the hosted zone object directly
