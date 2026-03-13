# Deploy Stock AI Platform on Microsoft Azure

Deploy the API and workers using **Azure Container Apps** (or **Azure App Service**), with **Azure Database for PostgreSQL** and **Azure Cache for Redis**. Frontend can run in the same Container Apps environment or as a static site.

## Prerequisites

- Azure CLI (`az`) installed and logged in
- Docker (for building images)
- Resource group and region (e.g. `eastus`)

## 1. Create resource group and services

```bash
RESOURCE_GROUP=stock-ai-rg
LOCATION=eastus
POSTGRES_ADMIN=stockai
POSTGRES_PASSWORD=CHANGE_ME_STRONG

az group create --name $RESOURCE_GROUP --location $LOCATION
```

## 2. Azure Database for PostgreSQL (Flexible Server)

```bash
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name stock-ai-db \
  --location $LOCATION \
  --admin-user $POSTGRES_ADMIN \
  --admin-password $POSTGRES_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15

az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name stock-ai-db \
  --database-name stock_ai
```

Allow Azure services to connect:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name stock-ai-db \
  --rule-name AllowAzure \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

Connection string: `postgresql://USER:PASSWORD@stock-ai-db.postgres.database.azure.com:5432/stock_ai?sslmode=require`

## 3. Azure Cache for Redis

```bash
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name stock-ai-redis \
  --location $LOCATION \
  --sku Basic \
  --vm-size c0
```

Get host and key:

```bash
az redis list-keys --resource-group $RESOURCE_GROUP --name stock-ai-redis
REDIS_HOST=$(az redis show --resource-group $RESOURCE_GROUP --name stock-ai-redis --query hostName -o tsv)
# Redis URL: redis://:ACCESS_KEY@REDIS_HOST:6380 (Azure Redis uses port 6380 for SSL)
# Or non-SSL: redis://REDIS_HOST:6379 if you enable non-SSL (not recommended in prod)
```

Use: `redis://:PRIMARY_KEY@stock-ai-redis.redis.cache.windows.net:6380` with `ssl=True` in app if needed.

## 4. Container Registry and images

```bash
ACR_NAME=stockaiacr
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
az acr login --name $ACR_NAME

# From repo root
docker build -f cloud/deployment_scripts/Dockerfile.api -t $ACR_NAME.azurecr.io/stock-ai-api:latest .
docker push $ACR_NAME.azurecr.io/stock-ai-api:latest

docker build -f cloud/deployment_scripts/Dockerfile.worker -t $ACR_NAME.azurecr.io/stock-ai-worker:latest .
docker push $ACR_NAME.azurecr.io/stock-ai-worker:latest

cd frontend && docker build -t $ACR_NAME.azurecr.io/stock-ai-frontend:latest . && docker push $ACR_NAME.azurecr.io/stock-ai-frontend:latest && cd ..
```

## 5. Container Apps environment and API

```bash
ENVIRONMENT=stock-ai-env
az containerapp env create \
  --resource-group $RESOURCE_GROUP \
  --name $ENVIRONMENT \
  --location $LOCATION

# Create API app (use Key Vault or env for secrets in production)
az containerapp create \
  --resource-group $RESOURCE_GROUP \
  --name stock-ai-api \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/stock-ai-api:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --ingress external \
  --target-port 8000 \
  --env-vars \
    "CORS_ORIGINS=https://your-domain.com" \
    "PYTHONPATH=/app" \
    "DATABASE_URL=postgresql://$POSTGRES_ADMIN:$POSTGRES_PASSWORD@stock-ai-db.postgres.database.azure.com:5432/stock_ai?sslmode=require" \
    "REDIS_URL=redis://:KEY@stock-ai-redis.redis.cache.windows.net:6380"
```

For production, store `DATABASE_URL` and `REDIS_URL` in **Azure Key Vault** and reference from the Container App (managed identity + Key Vault references).

## 6. Worker (Container App or Azure Container Instances)

Run the Celery worker as a separate Container App (always-on):

```bash
az containerapp create \
  --resource-group $RESOURCE_GROUP \
  --name stock-ai-worker \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/stock-ai-worker:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --command "celery -A workers.celery_app worker -l info -Q default,daily" \
  --env-vars "PYTHONPATH=/app" "DATABASE_URL=..." "REDIS_URL=..."
```

For **Celery Beat** (scheduler), run a second worker container with command `celery -A workers.celery_app beat -l info`, or use **Azure Logic Apps / Timer trigger** to call an HTTP endpoint that triggers the daily job.

## 7. Frontend

```bash
az containerapp create \
  --resource-group $RESOURCE_GROUP \
  --name stock-ai-frontend \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/stock-ai-frontend:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --ingress external \
  --target-port 3000 \
  --env-vars "NEXT_PUBLIC_API_URL=https://stock-ai-api.REGION.azurecontainerapps.io"
```

## 8. HTTPS

Container Apps provide HTTPS by default (e.g. `https://stock-ai-api.REGION.azurecontainerapps.io`). Add a **custom domain** in the app’s Custom domains blade and bind a certificate.

## Files in this folder

- `bicep/` or `arm/` – Optional ARM/Bicep templates to automate the above (can be added).
- Use the CLI steps above or integrate into your CI/CD (e.g. GitHub Actions with `azure/container-apps-deploy`).
