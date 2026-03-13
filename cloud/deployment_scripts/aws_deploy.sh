#!/bin/bash
# Example AWS deployment (ECS/Fargate or EC2). Adjust for your account.
set -e
REGION=${AWS_REGION:-us-east-1}
ECR_URI=${AWS_ECR_URI:-}
if [ -z "$ECR_URI" ]; then
  echo "Set AWS_ECR_URI (e.g. 123456789.dkr.ecr.us-east-1.amazonaws.com/stock-ai-api)"
  exit 1
fi
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI
docker build -f Dockerfile.api -t stock-ai-api .
docker tag stock-ai-api:latest $ECR_URI:latest
docker push $ECR_URI:latest
# Trigger ECS service update or run your task definition
echo "Image pushed. Update ECS service or run task."
