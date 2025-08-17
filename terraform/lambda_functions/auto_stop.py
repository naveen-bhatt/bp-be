import json
import boto3
import logging
import os
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ecs = boto3.client('ecs')
rds = boto3.client('rds')
elbv2 = boto3.client('elbv2')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    """
    Auto-stop Lambda function that stops ECS service and RDS instance after 60 minutes of inactivity.
    """
    try:
        # Get environment variables
        ecs_cluster = os.environ['ECS_CLUSTER']
        ecs_service = os.environ['ECS_SERVICE']
        rds_instance = os.environ['RDS_INSTANCE']
        alb_name = os.environ['ALB_NAME']
        
        logger.info(f"Starting auto-stop check for cluster: {ecs_cluster}, service: {ecs_service}")
        
        # Check if there's been any recent activity on the ALB
        if has_recent_activity(alb_name):
            logger.info("Recent activity detected, skipping auto-stop")
            return {
                'statusCode': 200,
                'body': json.dumps('Recent activity detected, skipping auto-stop')
            }
        
        # Check ECS service status
        service_response = ecs.describe_services(
            cluster=ecs_cluster,
            services=[ecs_service]
        )
        
        if not service_response['services']:
            logger.error(f"Service {ecs_service} not found")
            return {
                'statusCode': 404,
                'body': json.dumps(f'Service {ecs_service} not found')
            }
        
        service = service_response['services'][0]
        current_desired_count = service['desiredCount']
        
        if current_desired_count == 0:
            logger.info(f"Service {ecs_service} is already stopped (desired count: 0)")
        else:
            # Stop ECS service by setting desired count to 0
            logger.info(f"Stopping ECS service {ecs_service} (current desired count: {current_desired_count})")
            
            ecs.update_service(
                cluster=ecs_cluster,
                service=ecs_service,
                desiredCount=0
            )
            
            logger.info(f"Successfully stopped ECS service {ecs_service}")
        
        # Check RDS instance status
        try:
            rds_response = rds.describe_db_instances(DBInstanceIdentifier=rds_instance)
            if rds_response['DBInstances']:
                db_instance = rds_response['DBInstances'][0]
                db_status = db_instance['DBInstanceStatus']
                
                if db_status == 'available':
                    logger.info(f"Stopping RDS instance {rds_instance}")
                    rds.stop_db_instance(DBInstanceIdentifier=rds_instance)
                    logger.info(f"Successfully stopped RDS instance {rds_instance}")
                elif db_status == 'stopped':
                    logger.info(f"RDS instance {rds_instance} is already stopped")
                else:
                    logger.info(f"RDS instance {rds_instance} is in {db_status} state, cannot stop")
            else:
                logger.warning(f"RDS instance {rds_instance} not found")
        except Exception as e:
            logger.warning(f"Could not stop RDS instance {rds_instance}: {str(e)}")
        
        # Send CloudWatch metric
        cloudwatch.put_metric_data(
            Namespace='BluePansy/AutoStop',
            MetricData=[
                {
                    'MetricName': 'AutoStopExecuted',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': 'dev'
                        },
                        {
                            'Name': 'Service',
                            'Value': ecs_service
                        }
                    ]
                }
            ]
        )
        
        logger.info("Auto-stop execution completed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Auto-stop executed successfully')
        }
        
    except Exception as e:
        logger.error(f"Error in auto-stop lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def has_recent_activity(alb_name):
    """
    Check if there's been recent activity on the ALB in the last 60 minutes.
    Returns True if activity detected, False otherwise.
    """
    try:
        # Get ALB metrics for the last 60 minutes
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=60)
        
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='RequestCount',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': alb_name
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5-minute periods
            Statistics=['Sum']
        )
        
        # Check if there are any requests in the last 60 minutes
        for datapoint in response['Datapoints']:
            if datapoint['Sum'] > 0:
                logger.info(f"Recent activity detected: {datapoint['Sum']} requests at {datapoint['Timestamp']}")
                return True
        
        logger.info("No recent activity detected in the last 60 minutes")
        return False
        
    except Exception as e:
        logger.warning(f"Could not check ALB activity: {str(e)}")
        # If we can't check activity, assume there might be activity and don't stop
        return True
