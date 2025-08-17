terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Use local state for simplicity
  backend "local" {}
}

provider "aws" {
  region = "ap-south-1"
  
  default_tags {
    tags = {
      Environment = "dev"
      Project     = "bluepansy"
      ManagedBy   = "terraform"
    }
  }
}

# Data sources for existing resources
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["dev-vpc-stack/dev-vpc"]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
  
  filter {
    name   = "tag:Name"
    values = ["*privateSubnet*"]
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
  
  filter {
    name   = "tag:Name"
    values = ["*publicSubnet*"]
  }
}

data "aws_security_group" "ecs" {
  filter {
    name   = "group-name"
    values = ["dev-vpc-stack-devecssg*"]
  }
  
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
}

data "aws_security_group" "alb" {
  filter {
    name   = "group-name"
    values = ["dev-vpc-stack-devalbsg*"]
  }
  
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
}

# ECR Repository
resource "aws_ecr_repository" "api" {
  name                 = "${var.environment}-${var.project}-api"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  force_delete = true
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-${var.project}-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "${var.environment}-${var.project}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "${var.environment}-api"
      image = "${aws_ecr_repository.api.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "LOG_LEVEL"
          value = "DEBUG"
        }
      ]
      
      secrets = [
        {
          name      = "SECRET_KEY"
          valueFrom = "/${var.environment}/secret_key"
        },
        {
          name      = "DATABASE_URL"
          valueFrom = "/${var.environment}/database_url"
        },
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:070949690701:secret:${var.environment}rdsstack${var.environment}databaseSecre-yCMu2q5ZHYce-EbeNms:password::"
        },
        {
          name      = "JWT_ALGORITHM"
          valueFrom = "/${var.environment}/jwt_algorithm"
        },
        {
          name      = "ACCESS_TOKEN_TTL_MINUTES"
          valueFrom = "/${var.environment}/access_token_ttl_minutes"
        },
        {
          name      = "REFRESH_TOKEN_TTL_DAYS"
          valueFrom = "/${var.environment}/refresh_token_ttl_days"
        },
        {
          name      = "CORS_ORIGINS"
          valueFrom = "/${var.environment}/cors_origins"
        },
        {
          name      = "FRONTEND_URL"
          valueFrom = "/${var.environment}/frontend_url"
        },
        {
          name      = "GOOGLE_CLIENT_ID"
          valueFrom = "/${var.environment}/google_client_id"
        },
        {
          name      = "GOOGLE_CLIENT_SECRET"
          valueFrom = "/${var.environment}/google_client_secret"
        },
        {
          name      = "STRIPE_SECRET_KEY"
          valueFrom = "/${var.environment}/stripe_secret_key"
        },
        {
          name      = "RAZORPAY_KEY_ID"
          valueFrom = "/${var.environment}/razorpay_key_id"
        },
        {
          name      = "RAZORPAY_KEY_SECRET"
          valueFrom = "/${var.environment}/razorpay_key_secret"
        },
        {
          name      = "ADMIN_EMAIL"
          valueFrom = "/${var.environment}/admin_email"
        },
        {
          name      = "ADMIN_PASSWORD"
          valueFrom = "/${var.environment}/admin_password"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.environment}-${var.project}-api"
  retention_in_days = 7
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.environment}-${var.project}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [data.aws_security_group.alb.id]
  subnets            = data.aws_subnets.public.ids
  
  enable_deletion_protection = false
}

# ALB Target Group
resource "aws_lb_target_group" "api" {
  name        = "${var.environment}-${var.project}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.existing.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

# ALB Listener (HTTP)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

# ECS Service
resource "aws_ecs_service" "api" {
  name            = "${var.environment}-${var.project}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = data.aws_subnets.private.ids
    security_groups  = [data.aws_security_group.ecs.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "${var.environment}-api"
    container_port   = 8000
  }
  
  depends_on = [aws_lb_listener.http]
}

# IAM Execution Role
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.environment}-${var.project}-ecs-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Custom policy for Parameter Store access
resource "aws_iam_role_policy" "ecs_execution_parameter_store_policy" {
  name = "${var.environment}-${var.project}-ecs-execution-parameter-store"
  role = aws_iam_role.ecs_execution_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:*:parameter/${var.environment}/*",
          "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.environment}*"
        ]
      }
    ]
  })
}

# Additional policy for database password from Secrets Manager
resource "aws_iam_role_policy" "ecs_execution_secrets_policy" {
  name = "${var.environment}-${var.project}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.environment}rdsstack${var.environment}databaseSecre*"
        ]
      }
    ]
  })
}

# IAM Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.environment}-${var.project}-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Basic policy for task role
resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "${var.environment}-${var.project}-ecs-task-basic"
  role = aws_iam_role.ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Functions for Auto-Start/Stop
# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}-${var.project}-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.environment}-${var.project}-lambda-policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:ListServices"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:StartDBInstance",
          "rds:StopDBInstance",
          "rds:DescribeDBInstances"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeTargetHealth"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.environment}-${var.project}-auto-stop"
  retention_in_days = 7
}

# Auto-Stop Lambda Function
resource "aws_lambda_function" "auto_stop" {
  filename         = "../lambda_functions.zip"
  function_name    = "${var.environment}-${var.project}-auto-stop"
  role            = aws_iam_role.lambda_role.arn
  handler         = "auto_stop.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  
  environment {
    variables = {
      ECS_CLUSTER = aws_ecs_cluster.main.name
      ECS_SERVICE = aws_ecs_service.api.name
      RDS_INSTANCE = "${var.environment}-rds-stack-${var.environment}databased0b326ba-gbmc1lawuaw0"
      ALB_NAME = aws_lb.main.name
    }
  }
  
  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.lambda_logs
  ]
}

# CloudWatch Event Rule for Auto-Stop (every 60 minutes)
resource "aws_cloudwatch_event_rule" "auto_stop_rule" {
  name                = "${var.environment}-${var.project}-auto-stop-rule"
  description         = "Trigger auto-stop Lambda every 60 minutes"
  schedule_expression = "rate(60 minutes)"
}

# CloudWatch Event Target
resource "aws_cloudwatch_event_target" "auto_stop_target" {
  rule      = aws_cloudwatch_event_rule.auto_stop_rule.name
  target_id = "AutoStopTarget"
  arn       = aws_lambda_function.auto_stop.arn
}

# Lambda Permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auto_stop.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.auto_stop_rule.arn
}

# Auto-Start Lambda Function (triggered by ALB requests)
resource "aws_lambda_function" "auto_start" {
  filename         = "../lambda_functions.zip"
  function_name    = "${var.environment}-${var.project}-auto-start"
  role            = aws_iam_role.lambda_role.arn
  handler         = "auto_start.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  
  environment {
    variables = {
      ECS_CLUSTER = aws_ecs_cluster.main.name
      ECS_SERVICE = aws_ecs_service.api.name
      RDS_INSTANCE = "${var.environment}-rds-stack-${var.environment}databased0b326ba-gbmc1lawuaw0"
    }
  }
  
  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.lambda_logs
  ]
}

# CloudWatch Event Rule for Auto-Start (when ALB receives requests)
resource "aws_cloudwatch_event_rule" "auto_start_rule" {
  name                = "${var.environment}-${var.project}-auto-start-rule"
  description         = "Trigger auto-start Lambda when ALB receives requests"
  
  event_pattern = jsonencode({
    source      = ["aws.elasticloadbalancing"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventName = ["RegisterTargets", "DeregisterTargets"]
      requestParameters = {
        targetGroupArn = [aws_lb_target_group.api.arn]
      }
    }
  })
}

# CloudWatch Event Target for Auto-Start
resource "aws_cloudwatch_event_target" "auto_start_target" {
  rule      = aws_cloudwatch_event_rule.auto_start_rule.name
  target_id = "AutoStartTarget"
  arn       = aws_lambda_function.auto_start.arn
}

# Lambda Permission for Auto-Start CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch_start" {
  statement_id  = "AllowExecutionFromCloudWatchStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auto_start.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.auto_start_rule.arn
}

# Outputs
output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.api.name
}
