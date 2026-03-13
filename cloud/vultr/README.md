# Deploy Stock AI Platform on Vultr

Deploy the full stack on **Vultr** using **Cloud Compute** (VPS) with Docker, **Vultr Managed PostgreSQL**, **Vultr Managed Redis**, and optional **Vultr Load Balancer** with HTTPS.

## Architecture on Vultr

```
                    [HTTPS - Load Balancer or Nginx on VPS]
                                    │
              ┌─────────────────────▼─────────────────────┐
              │         Vultr Cloud Compute (VPS)         │
              │  ┌─────────┐  ┌─────────┐  ┌──────────┐  │
              │  │ Next.js │  │ FastAPI │  │  Celery  │  │
              │  │ :3000   │  │  :8000  │  │  worker  │  │
              │  └────┬────┘  └────┬────┘  └────┬─────┘  │
              └───────┼───────────┼────────────┼─────────┘
                      │           │            │
              ┌───────▼───────────▼────────────▼─────────┐
              │  Vultr Managed PostgreSQL (DATABASE_URL)  │
              │  Vultr Managed Redis (REDIS_URL)         │
              └──────────────────────────────────────────┘
```

---

## Step 1: Create a Vultr account and resources

1. Sign up at [vultr.com](https://www.vultr.com).
2. Add a payment method and ensure you have enough credit for:
   - 1× Cloud Compute instance (e.g. $12–24/mo for 2 vCPU, 4 GB RAM)
   - 1× Managed PostgreSQL (small plan)
   - 1× Managed Redis (small plan)
   - Optional: 1× Load Balancer

---

## Step 2: Create Vultr Managed PostgreSQL

1. In the **Vultr Customer Portal**, go to **Products** → **Add** → **Managed Database**.
2. Choose **PostgreSQL**, pick a **region** (same as your VPS for lower latency).
3. Select a plan (e.g. **Starter** or **Business**).
4. Set **Database Name**: `stock_ai`, **Username** and **Password** (save them).
5. Create the database. Wait until it is **Active**.
6. In the database details, note:
   - **Host** (e.g. `vultr-prod-xxx.vultrdb.com`)
   - **Port** (usually `16751` for managed DB; see your instance)
   - **Username**, **Password**, **Database** (`stock_ai`)

**Connection string format:**

```text
postgresql://USERNAME:PASSWORD@HOST:PORT/stock_ai?sslmode=require
```

Replace `USERNAME`, `PASSWORD`, `HOST`, and `PORT` with the values from the portal. Use **Private Network** host if your VPS is in the same region and you enabled private networking.

---

## Step 3: Create Vultr Managed Redis

1. Go to **Products** → **Add** → **Managed Database**.
2. Choose **Redis**, same **region** as the VPS and PostgreSQL.
3. Select a plan and create the instance.
4. When **Active**, note **Host** and **Port** (e.g. `6379` or the one shown). If a password is set, note it.

**Redis URL format:**

```text
redis://default:PASSWORD@HOST:PORT
# or if no password:
redis://HOST:PORT/0
```

Use the **private network** host if available for better security.

---

## Step 4: Create a Cloud Compute instance (VPS)

1. Go to **Products** → **Add** → **Cloud Compute**.
2. **Region**: same as PostgreSQL and Redis.
3. **Image**: **Ubuntu 22.04 LTS**.
4. **Plan**: at least 2 vCPU, 4 GB RAM (e.g. **Regular Performance** or **High Frequency**).
5. Add your **SSH key** (recommended) or set a root password.
6. Create the instance. Note the **Public IP**.

---

## Step 5: Connect to the VPS and install Docker

1. SSH into the server:

   ```bash
   ssh root@YOUR_VPS_IP
   ```

2. Update and install Docker and Docker Compose:

   ```bash
   apt update && apt upgrade -y
   apt install -y docker.io docker-compose-v2 git
   systemctl enable docker && systemctl start docker
   ```

3. Confirm Docker works:

   ```bash
   docker run --rm hello-world
   ```

---

## Step 6: Clone the repo and configure environment

1. Clone the project (replace with your repo URL if you use one):

   ```bash
   cd /opt
   git clone https://github.com/YOUR_ORG/stock-ai-platform.git
   cd stock-ai-platform
   ```

   If you don’t use Git, upload the project (e.g. with `scp` or SFTP) to `/opt/stock-ai-platform`.

2. Create a production env file:

   ```bash
   cp .env.example .env
   nano .env
   ```

3. Set these variables (use your real values from Steps 2 and 3):

   ```env
   DATABASE_URL=postgresql://USER:PASSWORD@YOUR_PG_HOST:PORT/stock_ai?sslmode=require
   REDIS_URL=redis://:PASSWORD@YOUR_REDIS_HOST:PORT
   CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
   ```

   Add any optional API keys (Danelfin, Seeking Alpha, etc.) in the same file.

4. Save and restrict permissions:

   ```bash
   chmod 600 .env
   ```

---

## Step 7: Deploy with Docker Compose on Vultr

Use the Vultr-specific compose file that expects `DATABASE_URL` and `REDIS_URL` (no local Postgres/Redis containers).

1. From the project root on the VPS:

   ```bash
   cd /opt/stock-ai-platform
   docker compose -f cloud/vultr/docker-compose.vultr.yml --env-file .env up -d --build
   ```

   This will:

   - Build and run the **API** (port 8000)
   - Build and run the **frontend** (port 3000) with `NEXT_PUBLIC_API_URL` set to your API URL (see below).
   - Build and run the **Celery worker** and **Celery beat** using `REDIS_URL` and `DATABASE_URL`.

2. Set the API URL for the frontend:

   - If you will use **your domain** (e.g. `https://api.your-domain.com`), set that in the compose file or in `.env` as `NEXT_PUBLIC_API_URL=https://api.your-domain.com`, then rebuild the frontend.
   - For a quick test, you can use `http://YOUR_VPS_IP:8000` (no HTTPS).

   Example for production: in `cloud/vultr/docker-compose.vultr.yml` the frontend env can be:

   ```yaml
   environment:
     - NEXT_PUBLIC_API_URL=https://api.your-domain.com
   ```

   Rebuild after changing:  
   `docker compose -f cloud/vultr/docker-compose.vultr.yml --env-file .env up -d --build`

3. Check that containers are running:

   ```bash
   docker compose -f cloud/vultr/docker-compose.vultr.yml ps
   docker compose -f cloud/vultr/docker-compose.vultr.yml logs -f api
   ```

4. Open in browser (replace with your VPS IP or domain):

   - Frontend: `http://YOUR_VPS_IP:3000`
   - API: `http://YOUR_VPS_IP:8000`
   - API docs: `http://YOUR_VPS_IP:8000/docs`

---

## Step 8: HTTPS – Option A (recommended): Vultr Load Balancer + Auto SSL

1. In Vultr, go to **Products** → **Add** → **Load Balancer**.
2. **Region**: same as your VPS.
3. **Forwarding rules**:
   - **Frontend**: HTTPS 443 → VPS IP, port 3000 (or 80 → 3000 if you only use HTTP first).
   - **API**: e.g. HTTPS 443 on a different subdomain or path, or a second LB; or use one LB with path-based rules if supported. Alternatively, use one subdomain for the app and one for the API (e.g. `app.your-domain.com` → 3000, `api.your-domain.com` → 8000).
4. Enable **Auto SSL** for your domain (e.g. `app.your-domain.com`, `api.your-domain.com`) per [Vultr’s Auto SSL docs](https://docs.vultr.com/how-to-enable-automatic-ssl-http2-and-http3-on-a-vultr-load-balancer).
5. Point your DNS A records for the chosen hostnames to the **Load Balancer IP** (or the hostnames Vultr gives you).

Traffic will be HTTPS at the LB; the LB forwards to your VPS on 3000 and 8000.

---

## Step 9: HTTPS – Option B: Nginx (or Caddy) on the VPS

If you prefer to terminate SSL on the VPS instead of using the Load Balancer:

1. Install Nginx (or Caddy):

   ```bash
   apt install -y nginx certbot python3-certbot-nginx
   ```

2. Point your domain’s A record to **YOUR_VPS_IP**.

3. Use the sample config (edit domain and paths):

   ```bash
   cp /opt/stock-ai-platform/cloud/vultr/nginx.conf.sample /etc/nginx/sites-available/stock-ai
   nano /etc/nginx/sites-available/stock-ai
   # Set server_name to your-domain.com and api.your-domain.com (or one domain with paths)
   ln -s /etc/nginx/sites-available/stock-ai /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx
   certbot --nginx -d your-domain.com -d api.your-domain.com
   ```

4. (Optional) If you want only Nginx to receive traffic, bind the app ports to localhost by running with an override:

   ```bash
   # Publish ports only on 127.0.0.1 so Nginx can proxy without exposing 3000/8000 to the internet
   docker compose -f cloud/vultr/docker-compose.vultr.yml --env-file .env -f cloud/vultr/docker-compose.nginx.yml up -d
   ```

   Create `cloud/vultr/docker-compose.nginx.yml` with:

   ```yaml
   services:
     api:    { ports: ["127.0.0.1:8000:8000"] }
     frontend: { ports: ["127.0.0.1:3000:3000"] }
   ```

---

## Step 10: Run the daily recommendation pipeline (first time)

Either trigger via API (with auth) or run the seed script once inside the API container:

```bash
docker compose -f cloud/vultr/docker-compose.vultr.yml exec api python -c "
from core.daily_engine import generate_daily_recommendations
from core.schemas import HoldingPeriod
from database.repository import save_analyses, save_recommendations
from data_ingestion.pipeline import run_ingestion
analyses = run_ingestion(limit_per_source=200)
if analyses: save_analyses(analyses)
recs = generate_daily_recommendations(holding_period=HoldingPeriod.MEDIUM_TERM, top_n=20)
if recs: save_recommendations(recs)
print(len(recs), 'recommendations saved')
"
```

Or use the script:

```bash
docker compose -f cloud/vultr/docker-compose.vultr.yml exec api python scripts/seed_recommendations.py
```

After this, the Celery beat schedule will run the daily job automatically; you can also call the refresh endpoint (with auth) if you implemented it.

---

## Step 11: Firewall (optional but recommended)

Restrict access so only the Load Balancer (or Nginx) and SSH are exposed:

```bash
ufw allow 22
ufw allow 80
ufw allow 443
# If you use Vultr LB, allow from LB only; else allow 3000, 8000 only from localhost if Nginx is on same box
ufw enable
```

If the LB is in front, you can close 3000 and 8000 from the internet and only allow 80/443 (and 22 for SSH).

---

## Summary checklist

| Step | Action |
|------|--------|
| 1 | Create Vultr account |
| 2 | Create **Managed PostgreSQL**; note host, port, user, password, DB name |
| 3 | Create **Managed Redis**; note host, port, password |
| 4 | Create **Cloud Compute** (Ubuntu 22.04) VPS |
| 5 | SSH in; install Docker and Docker Compose |
| 6 | Clone/upload project; create `.env` with `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS` |
| 7 | Run `docker compose -f cloud/vultr/docker-compose.vultr.yml --env-file .env up -d --build` |
| 8 | Configure **HTTPS**: Vultr Load Balancer (Auto SSL) or Nginx + Certbot on VPS |
| 9 | Point DNS to LB or VPS; set `NEXT_PUBLIC_API_URL` and rebuild frontend if needed |
| 10 | Run seed/refresh once; rely on Celery beat for daily runs |

---

## Files in this folder

- **README.md** (this file) – step-by-step deployment on Vultr.
- **docker-compose.vultr.yml** – Compose file using **Vultr Managed PostgreSQL and Redis** (no local DB/Redis containers).
- **nginx.conf.sample** – Sample Nginx reverse proxy for API + frontend with SSL.

For more on the app (env vars, architecture), see the main [cloud/README.md](../README.md).
