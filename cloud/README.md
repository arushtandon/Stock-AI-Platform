# Stock AI Platform – Cloud Deployment

The platform is designed to run **entirely in the cloud** on AWS, GCP, or Azure with:

- **Managed PostgreSQL** (RDS / Cloud SQL / Azure Database for PostgreSQL)
- **Managed Redis** (ElastiCache / Memorystore / Azure Cache for Redis)
- **Containerized API & workers** (ECS Fargate / Cloud Run / Container Apps)
- **HTTPS** via load balancer / API gateway with TLS termination
- **Object storage** for artifacts if needed (S3 / GCS / Blob)

## Quick links

| Cloud | Folder | Services |
|-------|--------|----------|
| **AWS** | [cloud/aws/](aws/) | ECS Fargate, RDS, ElastiCache, ALB, ECR |
| **GCP** | [cloud/gcp/](gcp/) | Cloud Run, Cloud SQL, Memorystore, Load Balancer |
| **Azure** | [cloud/azure/](azure/) | Container Apps, Azure Database for PostgreSQL, Azure Cache for Redis |
| **Vultr** | [cloud/vultr/](vultr/) | Cloud Compute (VPS), Managed PostgreSQL, Managed Redis, Load Balancer + SSL |
| **Render** | [docs/DEPLOY_RENDER.md](../docs/DEPLOY_RENDER.md) | Free/Starter Postgres + Redis, web + worker + cron (very low cost) |

## Common cloud architecture

```
                    [HTTPS]
                        │
              ┌─────────▼─────────┐
              │  Load Balancer /   │
              │  API Gateway       │
              └─────────┬─────────┘
                        │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐     ┌─────▼─────┐   ┌─────▼─────┐
   │ Next.js │     │  FastAPI   │   │  Celery   │
   │ Frontend│     │  (API)    │   │  Workers  │
   └────┬────┘     └─────┬─────┘   └─────┬─────┘
        │                │                │
        │         ┌──────┴──────┐         │
        │         │  PostgreSQL │         │
        │         │  Redis      │◄────────┘
        │         └─────────────┘
        │
   [Optional: CDN / Object storage for static assets]
```

## Deployment order

1. **Create managed database and Redis** in your cloud (see each cloud folder: [AWS](aws/README.md), [GCP](gcp/README.md), [Azure](azure/README.md)).
2. **Build and push container images** (API, worker, frontend) to the cloud registry (ECR / Artifact Registry / ACR). Use the Dockerfiles in `cloud/deployment_scripts/` and `frontend/Dockerfile`; see [deployment_scripts/README.md](deployment_scripts/README.md).
3. **Deploy API and workers** using the provided task definitions / Cloud Run services / Container Apps. All traffic over **HTTPS**.
4. **Deploy frontend** and set `NEXT_PUBLIC_API_URL` to the API’s **HTTPS** URL.
5. **Configure secrets**: Store `DATABASE_URL`, `REDIS_URL`, and any premium data source API keys in the cloud secret manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault).

## Environment variables (production)

Set these in your cloud runtime (e.g. ECS task def, Cloud Run env, App Service config):

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (from RDS/Cloud SQL/Azure) |
| `REDIS_URL` | Redis connection string (from ElastiCache/Memorystore/Azure Cache) |
| `CORS_ORIGINS` | Comma-separated allowed origins (e.g. `https://your-domain.com`) |
| `DANELFIN_API_KEY` | Optional: Danelfin API key |
| `SEEKING_ALPHA_API_KEY` | Optional: Seeking Alpha API key |
| `INVESTING_PRO_API_KEY` | Optional: Investing.com Pro API key |
| `TRADINGVIEW_API_KEY` | Optional: TradingView API key |

## Docker images (from repo root)

- **API**: `cloud/deployment_scripts/Dockerfile.api`
- **Worker**: `cloud/deployment_scripts/Dockerfile.worker`
- **Frontend**: `frontend/Dockerfile`

Build and push to your registry; use the same images across AWS/GCP/Azure.
