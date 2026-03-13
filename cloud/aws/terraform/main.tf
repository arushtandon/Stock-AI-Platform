# Stock AI Platform - AWS Infrastructure (Terraform)
# Run from cloud/aws/terraform with: terraform init && terraform plan -var-file=terraform.tfvars && terraform apply

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC (use existing)
data "aws_vpc" "main" {
  id = var.vpc_id
}

# Subnets for RDS/ElastiCache (pass IDs via variable)
data "aws_subnet" "private" {
  for_each = toset(var.private_subnet_ids)
  id       = each.value
}

# DB subnet group for RDS
resource "aws_db_subnet_group" "main" {
  name       = "stock-ai-db-subnet"
  subnet_ids = var.private_subnet_ids
}

# Security group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "stock-ai-rds-"
  vpc_id      = data.aws_vpc.main.id
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.private_cidrs
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier     = "stock-ai-db"
  engine         = "postgres"
  engine_version = "15"
  instance_class = var.rds_instance_class
  allocated_storage = 20
  storage_type   = "gp3"
  db_name  = "stock_ai"
  username = var.db_username
  password = var.db_password
  port     = 5432
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  publicly_accessible    = false
  skip_final_snapshot   = var.skip_final_snapshot
}

# Security group for Redis
resource "aws_security_group" "redis" {
  name_prefix = "stock-ai-redis-"
  vpc_id      = data.aws_vpc.main.id
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.private_cidrs
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "stock-ai-redis-subnet"
  subnet_ids = var.private_subnet_ids
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "stock-ai-redis"
  node_type            = var.redis_node_type
  num_cache_clusters   = 1
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = false
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "redis_primary_endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "vpc_id" {
  value = data.aws_vpc.main.id
}

output "private_subnet_ids" {
  value = var.private_subnet_ids
}
