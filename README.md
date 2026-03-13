# Stock AI Platform

**Cloud-based** stock analysis and recommendation platform that aggregates insights from Danelfin, Seeking Alpha Premium, Investing.com InvestingPro, and TradingView to produce daily top 20 stock recommendations. The system is built to run **24/7 in the cloud** on AWS, GCP, or Azure.

## Deploy to the cloud

The platform is designed for **cloud deployment**. Use managed PostgreSQL, Redis, and container runtimes:

| Cloud | Stack | Guide |
|-------|--------|--------|
| **AWS** | ECS Fargate, RDS, ElastiCache, ALB (HTTPS) | [cloud/aws/README.md](cloud/aws/README.md) |
| **GCP** | Cloud Run, Cloud SQL, Memorystore | [cloud/gcp/README.md](cloud/gcp/README.md) |
| **Azure** | Container Apps, Azure Database for PostgreSQL, Azure Cache for Redis | [cloud/azure/README.md](cloud/azure/README.md) |
| **Vultr** | Cloud Compute (VPS), Managed PostgreSQL & Redis, Load Balancer + SSL | [cloud/vultr/README.md](cloud/vultr/README.md) |
| **Render** | **Low-cost:** Free/Starter Postgres + Redis, Python/Node services, cron | [docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md) |

**Common steps:**

1. Create **managed PostgreSQL** and **managed Redis** in your cloud.
2. Build and push **Docker images** (API, worker, frontend) to your cloud registry (ECR / Artifact Registry / ACR).
3. Deploy **API** and **workers** to the cloud runtime (ECS / Cloud Run / Container Apps).
4. Put traffic behind **HTTPS** (load balancer or built-in TLS).
5. Store **secrets** (e.g. `DATABASE_URL`, `REDIS_URL`, API keys) in the cloud secret manager.

See **[cloud/README.md](cloud/README.md)** for architecture and environment variables.

## Architecture overview

- **Data ingestion**: Collectors for each premium research platform; unified schema
- **Analysis**: Fundamental, technical, and multi-source ranking engines
- **Risk**: Stop-loss, volatility, ATR-based targets
- **API**: FastAPI with OAuth, rate limiting, subscription tiers
- **Frontend**: Next.js + React + Tailwind UI
- **Infrastructure**: **Cloud-first** — AWS / GCP / Azure, managed PostgreSQL, managed Redis, Airflow/Celery

## Local development

For local runs (SQLite, optional Redis):

- [docs/COMPLETE_SETUP_GUIDE.md](docs/COMPLETE_SETUP_GUIDE.md) — backend, frontend, Docker Compose
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — component details

## License

Proprietary.
