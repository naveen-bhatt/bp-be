import json
import boto3
import logging
import os
import time

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ecs = boto3.client('ecs')
rds = boto3.client('rds')

def lambda_handler(event, context):
    """
    Auto-start Lambda function that starts ECS service and RDS instance when requests come in.
    """
    try:
        # Get environment variables
        ecs_cluster = os.environ['ECS_CLUSTER']
        ecs_service = os.environ['ECS_SERVICE']
        rds_instance = os.environ['RDS_INSTANCE']
        
        logger.info(f"Starting auto-start for cluster: {ecs_cluster}, service: {ecs_service}")
        
        # Start RDS instance first (takes longer)
        start_rds_instance(rds_instance)
        
        # Start ECS service
        start_ecs_service(ecs_cluster, ecs_service)
        
        logger.info("Auto-start execution completed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Auto-start executed successfully')
        }
        
    except Exception as e:
        logger.error(f"Error in auto-start lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def start_rds_instance(rds_instance):
    """
    Start the RDS instance if it's stopped.
    """
    try:
        rds_response = rds.describe_db_instances(DBInstanceIdentifier=rds_instance)
        if rds_response['DBInstances']:
            db_instance = rds_response['DBInstances'][0]
            db_status = db_instance['DBInstanceStatus']
            
            if db_status == 'stopped':
                logger.info(f"Starting RDS instance {rds_instance}")
                rds.start_db_instance(DBInstanceIdentifier=rds_instance)
                logger.info(f"Successfully started RDS instance {rds_instance}")
            elif db_status == 'available':
                logger.info(f"RDS instance {rds_instance} is already running")
            elif db_status == 'starting':
                logger.info(f"RDS instance {rds_instance} is already starting")
            else:
                logger.info(f"RDS instance {rds_instance} is in {db_status} state, cannot start")
        else:
            logger.warning(f"RDS instance {rds_instance} not found")
    except Exception as e:
        logger.warning(f"Could not start RDS instance {rds_instance}: {str(e)}")

def start_ecs_service(ecs_cluster, ecs_service):
    """
    Start the ECS service by setting desired count to 1.
    """
    try:
        # Check current service status
        service_response = ecs.describe_services(
            cluster=ecs_cluster,
            services=[ecs_service]
        )
        
        if not service_response['services']:
            logger.error(f"Service {ecs_service} not found")
            return
        
        service = service_response['services'][0]
        current_desired_count = service['desiredCount']
        
        if current_desired_count == 0:
            logger.info(f"Starting ECS service {ecs_service} (current desired count: {current_desired_count})")
            
            # Start ECS service by setting desired count to 1
            ecs.update_service(
                cluster=ecs_cluster,
                service=ecs_service,
                desiredCount=1
            )
            
            logger.info(f"Successfully started ECS service {ecs_service}")
            
            # Wait for service to be stable
            wait_for_service_stable(ecs_cluster, ecs_service)
            
        elif current_desired_count > 0:
            logger.info(f"ECS service {ecs_service} is already running (desired count: {current_desired_count})")
        else:
            logger.warning(f"ECS service {ecs_service} has unexpected desired count: {current_desired_count}")
            
    except Exception as e:
        logger.error(f"Could not start ECS service {ecs_service}: {str(e)}")

def wait_for_service_stable(ecs_cluster, ecs_service):
    """
    Wait for the ECS service to become stable.
    """
    try:
        logger.info(f"Waiting for ECS service {ecs_service} to become stable...")
        
        max_attempts = 30  # 5 minutes with 10-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            service_response = ecs.describe_services(
                cluster=ecs_cluster,
                services=[ecs_service]
            )
            
            if service_response['services']:
                service = service_response['services'][0]
                deployments = service.get('deployments', [])
                
                # Check if there's an active deployment
                active_deployment = None
                for deployment in deployments:
                    if deployment['status'] == 'PRIMARY':
                        active_deployment = deployment
                        break
                
                if active_deployment:
                    if active_deployment['desiredCount'] == active_deployment['runningCount']:
                        logger.info(f"ECS service {ecs_service} is now stable")
                        return
                    else:
                        logger.info(f"ECS service {ecs_service} still starting... (desired: {active_deployment['desiredCount']}, running: {active_deployment['runningCount']})")
                else:
                    logger.info(f"ECS service {ecs_service} has no active deployment")
            
            attempt += 1
            time.sleep(10)  # Wait 10 seconds before checking again
        
        logger.warning(f"ECS service {ecs_service} did not become stable within timeout")
        
    except Exception as e:
        logger.warning(f"Could not wait for service stability: {str(e)}")
