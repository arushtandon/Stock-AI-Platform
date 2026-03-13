# Deploy Stock AI Platform on Google Cloud (GCP)

Deploy the API and workers on **Cloud Run**, with **Cloud SQL (PostgreSQL)** and **Memorystore (Redis)**. Frontend can be served from **Cloud Run** or **Firebase Hosting / Cloud Storage + Load Balancer**.

## Prerequisites

- `gcloud` CLI installed and configured
- Docker (for building images)
- Optional: Terraform for `terraform/` in this folder

## 1. Enable APIs

```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com redis.googleapis.com artifactregistry.googleapis.com
```

## 2. Create Cloud SQL (PostgreSQL)

```bash
gcloud sql instances create stock-ai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=CHANGE_ME

gcloud sql databases create stock_ai --instance=stock-ai-db
# Create user and set password via Console or:
# gcloud sql users create stockai --instance=stock-ai-db --password=CHANGE_ME
```

Note the **connection name** (e.g. `PROJECT:REGION:stock-ai-db`) for Cloud Run connection.

## 3. Create Memorystore (Redis)

```bash
gcloud redis instances create stock-ai-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

Note the **host** and **port** (default 6379). Build Redis URL: `redis://REDIS_HOST:6379/0`.

## 4. Artifact Registry and images

```bash
gcloud auth configure-docker REGION-docker.pkg.dev

# Create repo
gcloud artifacts repositories create stock-ai --repository-format=docker --location=REGION

# From repo root
export REGION=us-central1
export PROJECT_ID=$(gcloud config get-value project)

docker build -f cloud/deployment_scripts/Dockerfile.api -t $REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/api:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/api:latest

docker build -f cloud/deployment_scripts/Dockerfile.worker -t $REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/worker:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/worker:latest

cd frontend && docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/frontend:latest . && docker push $REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/frontend:latest && cd ..
```

## 5. Store secrets in Secret Manager

```bash
echo -n "postgresql://USER:PASSWORD@/stock_ai?host=/cloudsql/PROJECT:REGION:stock-ai-db" | \
  gcloud secrets create stock-ai-database-url --data-file=-
echo -n "redis://REDIS_IP:6379/0" | \
  gcloud secrets create stock-ai-redis-url --data-file=-
```

Grant Cloud Run access:

```bash
gcloud secrets add-iam-policy-binding stock-ai-database-url \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud secrets add-iam-policy-binding stock-ai-redis-url \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
```

## 6. Deploy API to Cloud Run

```bash
gcloud run deploy stock-ai-api \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/api:latest \
  --platform=managed \
  --region=$REGION \
  --add-cloudsql-instances=PROJECT:REGION:stock-ai-db \
  --set-secrets=DATABASE_URL=stock-ai-database-url:latest,REDIS_URL=stock-ai-redis-url:latest \
  --set-env-vars="CORS_ORIGINS=https://your-domain.com,PYTHONPATH=/app" \
  --allow-unauthenticated \
  --port=8000
```

Use `--no-allow-unauthenticated` and IAP for private API. Note the **service URL** (HTTPS).

## 7. Deploy Worker to Cloud Run (Jobs or long-running)

For **scheduled tasks** (daily recommendations), use **Cloud Run Jobs**:

```bash
gcloud run jobs create stock-ai-daily-job \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/worker:latest \
  --region=$REGION \
  --set-secrets=DATABASE_URL=stock-ai-database-url:latest,REDIS_URL=stock-ai-redis-url:latest \
  --set-env-vars=PYTHONPATH=/app \
  --task-timeout=3600 \
  --max-retries=2
```

Trigger on schedule via **Cloud Scheduler**:

```bash
# Run job daily at 6 AM (e.g. Eastern)
gcloud scheduler jobs create http stock-ai-daily \
  --schedule="0 10 * * 1-5" \
  --uri="https://REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT_ID/jobs/stock-ai-daily-job:run" \
  --http-method=POST \
  --oauth-service-account-email=PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

For **24/7 Celery workers**, run the worker image on **GKE** or **Compute Engine** with Redis; Cloud Run is request-driven and not ideal for long-lived workers.

## 8. Deploy Frontend to Cloud Run

```bash
gcloud run deploy stock-ai-frontend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/stock-ai/frontend:latest \
  --platform=managed \
  --region=$REGION \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://stock-ai-api-xxx.run.app" \
  --allow-unauthenticated \
  --port=3000
```

## 9. HTTPS

Cloud Run provides HTTPS by default (e.g. `https://stock-ai-api-xxx.run.app`). For a custom domain:

1. In Cloud Run, map your domain to the service.
2. Verify ownership and ensure DNS points to the provided target.

## Files in this folder

- `terraform/` – Optional Terraform for Cloud SQL, Memorystore, and Cloud Run (see `terraform/README.md` if present).
- Use the steps above or automate with your own Terraform/Deployment Manager.
