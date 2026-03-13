variable "aws_region" {
  default = "us-east-1"
}

variable "vpc_id" {
  description = "Existing VPC ID"
  type        = string
}

variable "private_cidrs" {
  description = "CIDR blocks allowed to reach RDS/Redis (e.g. VPC CIDR)"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for RDS and ElastiCache"
  type        = list(string)
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "rds_instance_class" {
  default = "db.t3.micro"
}

variable "redis_node_type" {
  default = "cache.t3.micro"
}

variable "skip_final_snapshot" {
  default = true
}
