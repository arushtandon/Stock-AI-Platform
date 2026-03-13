# Deploy Stock AI Platform on Render

Render is **much cheaper** than Vultr’s managed database ($150/mo). You can run the full stack on **free and low-cost tiers**.

## Cost comparison

| Resource        | Vultr (your screenshot) | Render (this guide)   |
|----------------|--------------------------|------------------------|
| PostgreSQL     | **$150/mo** (1 vCPU, 4 GB) | **Free** (90 days) or **~$7/mo** (Starter) |
| Redis          | Extra                    | **Free** tier          |
| API + Frontend | VPS                      | **Free** tier (spin down when idle) |
| Worker         | VPS                      | **~$7/mo** (Starter)   |
| Cron (daily)   | VPS                      | **~$1/mo** (prorated)  |

**Rough total on Render:** **$0–15/mo** vs **$150+/mo** on Vultr for similar setup.

---

## Steps to deploy on Render

### 1. Push the repo to GitHub

Ensure the `stock-ai-platform` repo (with `render.yaml` at the root) is on **GitHub** (or GitLab). Render will deploy from this repo.

### 2. Create a Render account

1. Go to [render.com](https://render.com) and sign up (GitHub login is easiest).
2. Confirm your email if required.

### 3. Deploy with the Blueprint

1. In the **Render Dashboard**, click **New** → **Blueprint**.
2. Connect your **GitHub** (or GitLab) account and select the **stock-ai-platform** repository.
3. Render will detect `render.yaml` and show the services (PostgreSQL, Redis, API, Worker, Cron, Frontend).
4. Click **Apply**. Render will create:
   - **PostgreSQL** (free or starter)
   - **Redis** (Key Value, free)
   - **stock-ai-api** (Python web service)
   - **stock-ai-worker** (Celery worker)
   - **stock-ai-daily** (cron job, weekdays)
   - **stock-ai-frontend** (Next.js)

5. Wait for the first deploy to finish. Fix any build errors from the build logs if needed.

### 4. Set environment variables (required for frontend)

1. Open the **stock-ai-frontend** service → **Environment**.
2. Set **NEXT_PUBLIC_API_URL** to your API URL, e.g.:
   - `https://stock-ai-api.onrender.com`  
   (Use the exact URL Render shows for **stock-ai-api**.)
3. **Redeploy** the frontend so the build picks up this value.

Optional: for **stock-ai-api**, set **CORS_ORIGINS** to your frontend URL (e.g. `https://stock-ai-frontend.onrender.com`) if you use a custom domain later.

### 5. Optional: premium data source API keys

In **stock-ai-api** → **Environment**, add any of these (marked “sync: false” in the Blueprint so Render will prompt or let you paste):

- `DANELFIN_API_KEY`
- `SEEKING_ALPHA_API_KEY`
- `INVESTING_PRO_API_KEY`
- `TRADINGVIEW_API_KEY`

If you leave them unset, the app uses demo/synthetic data.

### 6. Run the first recommendation set

After the API is deployed and healthy:

1. **Option A – Cron:** Wait for the **stock-ai-daily** cron (e.g. 14:00 UTC on weekdays), or  
2. **Option B – Manual:** In the **stock-ai-api** shell (or a one-off job if you add one), run:
   ```bash
   python scripts/render_daily.py
   ```
   or call the refresh endpoint (if you added auth).

Then open the **frontend** URL and check the dashboard for recommendations.

---

## URLs after deploy

- **API:** `https://stock-ai-api.onrender.com` (or your custom domain)
- **API docs:** `https://stock-ai-api.onrender.com/docs`
- **Frontend:** `https://stock-ai-frontend.onrender.com`

(Exact hostnames depend on the service names you use in Render.)

---

## Free tier limits (Render)

- **One free PostgreSQL and one free Redis per account.** If you already have a free database or Redis from another project, the Blueprint will fail with "cannot have more than one active free tier database" or "cannot have more than 1 free tier Redis instance". The `render.yaml` in this repo uses **Starter** for the database and Redis so this project gets its own resources (~\$7 + ~\$10/mo). You can change back to `plan: free` only if this is the only project using free DB/Redis.
- **Free web services** spin down after ~15 minutes of no traffic; the first request may be slow (cold start).
- **Free PostgreSQL** is limited (e.g. 1 GB, 90-day expiration); for production, **Starter** or higher is recommended.
- **Free Redis** has usage limits; for heavy Celery use, use a paid plan.

With **Starter** for DB + Redis + worker, total is still low (~\$25/mo) compared to Vultr's \$150/mo for managed DB alone.

---

## Troubleshooting

- **Sync fails (plan / "Starter" errors):** Render’s Blueprint uses specific plan names. For **PostgreSQL** use `plan: basic-1gb` (not `starter`). The repo’s `render.yaml` is updated. Push, then **Manual sync** again.
- **Sync fails (billing):** Paid DB and Redis need a **payment method**. Render Dashboard → Account Settings → Billing → add a card.
- **API or worker "deploy failed":** Open the service (e.g. **stock-ai-api**) → **Logs** tab and check the **Build** and **Deploy** logs for the exact error. Common fixes: (1) `PYTHONPATH=.` is set in the Blueprint so imports work; (2) `apache-airflow` was removed from `requirements.txt` to avoid heavy builds; (3) add `runtime.txt` with `python-3.11.7` at repo root for Python version. Push changes and trigger **Manual Deploy** on the service.
- **Build fails (Python):** Ensure `requirements.txt` is at the **repo root** and that the build command is `pip install -r requirements.txt`. No need to set `PYTHONPATH` if the repo root is the project root.
- **Build fails (frontend):** Ensure **rootDir** is `frontend` and **NEXT_PUBLIC_API_URL** is set before building.
- **API can’t connect to DB/Redis:** Blueprint links them automatically. If you created DB/Redis manually, set **DATABASE_URL** and **REDIS_HOST** / **REDIS_PORT** (or **REDIS_URL**) in the API and worker services.
- **CORS errors:** Set **CORS_ORIGINS** on the API to your frontend URL (e.g. `https://stock-ai-frontend.onrender.com`).

For more on the app (env vars, architecture), see [ARCHITECTURE.md](ARCHITECTURE.md) and [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md).
