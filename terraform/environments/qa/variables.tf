variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "qa"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "bluepansy"
}

variable "vpc_name" {
  description = "Name of existing VPC"
  type        = string
  default     = "qa-vpc-stack/qa-vpc"
}

variable "ecs_cpu" {
  description = "ECS task CPU units"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "ECS task memory in MiB"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}
