# Stock AI Platform – Complete Setup Guide

This guide covers **cloud deployment** (recommended) and **local development**.

---

## Part I: Cloud deployment (recommended)

The platform is intended to run **in the cloud** with managed services. Each cloud has a dedicated guide:

- **AWS**: [cloud/aws/README.md](../cloud/aws/README.md) — ECS Fargate, RDS PostgreSQL, ElastiCache Redis, ALB with HTTPS
- **GCP**: [cloud/gcp/README.md](../cloud/gcp/README.md) — Cloud Run, Cloud SQL, Memorystore, Secret Manager
- **Azure**: [cloud/azure/README.md](../cloud/azure/README.md) — Container Apps, Azure Database for PostgreSQL, Azure Cache for Redis

**Summary:**

1. Create **managed PostgreSQL** and **managed Redis** in your chosen cloud.
2. Build and push **Docker images** to the cloud container registry.
3. Deploy **API** and **Celery workers** to the cloud (ECS / Cloud Run / Container Apps).
4. Deploy **frontend** and set `NEXT_PUBLIC_API_URL` to the API’s **HTTPS** URL.
5. Store `DATABASE_URL`, `REDIS_URL`, and any API keys in the **cloud secret manager** (Secrets Manager / Secret Manager / Key Vault).

See **[cloud/README.md](../cloud/README.md)** for the common architecture and production env vars.

---

## Part II: Local development

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- PostgreSQL 15+ (or SQLite for dev)
- Redis (for Celery)

### 1. Backend (API + Workers)

```bash
cd stock-ai-platform
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Environment

Create `.env` in project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stock_ai
# Or SQLite (no Redis/Postgres): leave unset or use sqlite:///./stock_ai.db
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
# Optional: API keys for premium sources (otherwise demo data is used)
# DANELFIN_API_KEY=...
# SEEKING_ALPHA_API_KEY=...
# INVESTING_PRO_API_KEY=...
# TRADINGVIEW_API_KEY=...
```

### Run API

From project root (so that `config`, `core`, `api`, etc. are on the path):

```bash
set PYTHONPATH=%CD%   # Windows
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### Run Celery (optional)

```bash
set PYTHONPATH=%CD%
celery -A workers.celery_app worker -l info -Q default,daily
```

In another terminal for scheduled tasks:

```bash
celery -A workers.celery_app beat -l info
```

### Generate recommendations (one-off)

**Option A – Seed script (no auth):**

```bash
python scripts/seed_recommendations.py
```

**Option B – API refresh (requires auth):**

```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/refresh?holding_period=medium_term&top_n=20" -H "X-API-Key: your-key"
```

**Option C – Run the daily engine in Python:**

```python
import sys
sys.path.insert(0, ".")
from core.daily_engine import generate_daily_recommendations
from core.schemas import HoldingPeriod
recs = generate_daily_recommendations(holding_period=HoldingPeriod.MEDIUM_TERM, top_n=20)
from database.repository import save_recommendations, save_analyses
from data_ingestion.pipeline import run_ingestion
analyses = run_ingestion(limit_per_source=200)
save_analyses(analyses)
save_recommendations(recs)
```

## 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run:

```bash
npm run dev
```

Open http://localhost:3000. Dashboard loads recommendations from `GET /api/v1/recommendations`.

## 3. Docker (all services)

From `cloud/deployment_scripts`:

```bash
docker-compose up -d
```

- API: 8000, Frontend: 3000, PostgreSQL: 5432, Redis: 6379.

Build context for API/worker is project root; copy paths in Dockerfiles may need adjusting (e.g. copy from `../..`).

## 4. Airflow (optional)

Point Airflow to `airflow/dags` and set `PYTHONPATH` (or install the project as a package) so that `core`, `database`, `data_ingestion` are importable. DAG `daily_stock_recommendations` runs the same pipeline as the Celery daily task.

## 5. Premium data sources

- Add API keys to `.env` as above.
- Implement real HTTP calls in each collector’s `_fetch_symbol()` using the platform’s official API (replace current placeholder/synthetic responses).
- Keep normalization in `_normalize()` so the rest of the pipeline stays unchanged.

## 6. HTTPS & production (cloud)

In production, **always use the cloud**:

- **HTTPS**: Use the load balancer or platform default (ALB + ACM, Cloud Run, Container Apps) so all traffic is HTTPS.
- **Secrets**: Use the cloud secret manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault); never commit keys.
- **Database & Redis**: Use managed PostgreSQL and Redis in the same cloud (RDS, Cloud SQL, Azure Database; ElastiCache, Memorystore, Azure Cache).

## 7. Alerts

- Implement `workers.tasks.alert_task`: call your email provider (e.g. SendGrid), push (e.g. FCM), Telegram Bot API, Slack webhook.
- Trigger `alert_task.delay(recs)` from `daily_recommendation_task` after saving recommendations.
