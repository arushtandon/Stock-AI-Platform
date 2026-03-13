# Deploy Stock AI Platform on AWS

Deploy the API, workers, and frontend on **Amazon ECS (Fargate)** with **RDS PostgreSQL**, **ElastiCache Redis**, and an **Application Load Balancer** with HTTPS.

## Prerequisites

- AWS CLI configured
- Terraform 1.x (optional; for `terraform/`)
- Docker (for building images)

## 1. Create RDS and ElastiCache (manual or Terraform)

### Option A – Terraform

```bash
cd cloud/aws/terraform
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Note the outputs: `rds_endpoint`, `redis_endpoint`, `vpc_id`, `private_subnet_ids`, `alb_dns_name`.

### Option B – AWS Console

1. **RDS**: Create a PostgreSQL 15 instance (single-AZ or Multi-AZ). Note endpoint and port. Create database `stock_ai` and user/password.
2. **ElastiCache**: Create a Redis 7 cluster (single node or cluster mode). Note primary endpoint and port.
3. **VPC**: Use default VPC or create one; ensure RDS and ElastiCache are in private subnets and security groups allow:
   - RDS: inbound 5432 from API/worker security group
   - Redis: inbound 6379 from API/worker security group

## 2. Build and push images to ECR

```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# From repo root
docker build -f cloud/deployment_scripts/Dockerfile.api -t stock-ai-api .
docker tag stock-ai-api:latest $ECR_URI/stock-ai-api:latest
docker push $ECR_URI/stock-ai-api:latest

docker build -f cloud/deployment_scripts/Dockerfile.worker -t stock-ai-worker .
docker tag stock-ai-worker:latest $ECR_URI/stock-ai-worker:latest
docker push $ECR_URI/stock-ai-worker:latest

cd frontend && docker build -t stock-ai-frontend . && cd ..
docker tag stock-ai-frontend:latest $ECR_URI/stock-ai-frontend:latest
docker push $ECR_URI/stock-ai-frontend:latest
```

Create ECR repos if needed:

```bash
aws ecr create-repository --repository-name stock-ai-api    --region $AWS_REGION
aws ecr create-repository --repository-name stock-ai-worker  --region $AWS_REGION
aws ecr create-repository --repository-name stock-ai-frontend --region $AWS_REGION
```

## 3. Create ECS cluster and services

Use the task definitions and service definitions in `cloud/aws/ecs/` (see below). Replace placeholders:

- `DATABASE_URL=postgresql://USER:PASSWORD@RDS_ENDPOINT:5432/stock_ai`
- `REDIS_URL=redis://REDIS_ENDPOINT:6379/0`
- `CORS_ORIGINS=https://your-domain.com`
- ECR image URIs and subnets/security groups from your VPC.

Run:

```bash
cd cloud/aws/ecs
# Register task definitions (after editing JSON)
aws ecs register-task-definition --cli-input-json file://task-def-api.json
aws ecs register-task-definition --cli-input-json file://task-def-worker.json
aws ecs register-task-definition --cli-input-json file://task-def-frontend.json

# Create cluster
aws ecs create-cluster --cluster-name stock-ai-cluster

# Create services (after creating ALB, target groups, and updating subnet/SG IDs)
aws ecs create-service --cli-input-json file://service-api.json
aws ecs create-service --cli-input-json file://service-worker.json
aws ecs create-service --cli-input-json file://service-frontend.json
```

## 4. HTTPS (ALB + ACM)

1. Request or import a certificate in **AWS Certificate Manager** for your domain.
2. Create an **Application Load Balancer** with a listener on 443 (HTTPS) forwarding to the API and frontend target groups.
3. Point your domain (e.g. `api.yourdomain.com`, `app.yourdomain.com`) to the ALB DNS name.

## 5. Secrets

Store sensitive values in **AWS Secrets Manager** and reference them in the ECS task definition (`secrets` block). Example:

- `stock-ai/database-url`
- `stock-ai/redis-url`
- `stock-ai/danelfin-api-key` (optional)

## Files in this folder

- `terraform/` – Terraform for VPC, RDS, ElastiCache, ECS cluster (optional).
- `ecs/` – ECS task definitions and service definitions (edit and run with AWS CLI).
