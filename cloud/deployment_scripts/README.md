# Deployment scripts

This folder contains **Docker** and **docker-compose** assets used for both **local** runs and **cloud** deployment.

## Contents

- **Dockerfile.api** – FastAPI backend (build from repo root).
- **Dockerfile.worker** – Celery worker (build from repo root).
- **docker-compose.yml** – Runs API, frontend, worker, beat, PostgreSQL, and Redis in one stack.

## Use in the cloud

**Production should use managed services in the cloud:**

1. **Database**: Use **managed PostgreSQL** (AWS RDS, GCP Cloud SQL, Azure Database for PostgreSQL). Set `DATABASE_URL` in your cloud runtime.
2. **Redis**: Use **managed Redis** (ElastiCache, Memorystore, Azure Cache for Redis). Set `REDIS_URL` in your cloud runtime.
3. **Containers**: Build these Dockerfiles and push to your cloud registry (ECR, Artifact Registry, ACR), then deploy to ECS / Cloud Run / Container Apps as described in:
   - [../aws/README.md](../aws/README.md)
   - [../gcp/README.md](../gcp/README.md)
   - [../azure/README.md](../azure/README.md)

Do **not** rely on the PostgreSQL and Redis services in `docker-compose.yml` for production; they are for local or single-node dev only.

## Local / single-node

From the **repo root**:

```bash
docker-compose -f cloud/deployment_scripts/docker-compose.yml up -d
```

Or from this directory:

```bash
docker-compose up -d
```

This starts API (port 8000), frontend (3000), worker, beat, Postgres, and Redis. Override `DATABASE_URL` and `REDIS_URL` if you want the app to use external DB/Redis.
