# Stock AI Platform – Architecture

## Overview

The platform aggregates analysis from **Danelfin**, **Seeking Alpha Premium**, **Investing.com InvestingPro**, and **TradingView**, normalizes it into a unified schema, runs a weighted composite ranking, applies risk filters, and publishes the **Top 20** daily stock recommendations. It runs 24/7 with scheduled ingestion and daily pre-market recommendation generation.

## High-Level Flow

```
[Data Sources] → [Ingestion Pipeline] → [Central DB]
       ↑                    ↓
       |            [Ranking Engine] → [Selection Engine]
       |                    ↓
       |            [Risk Module] → Entry / Stop / Take Profit
       |                    ↓
       |            [Daily Engine] → Top 20 Recommendations
       |                    ↓
       +------------ [API] ← [Alerts]
                         ↓
                  [Next.js Dashboard]
```

## Components

### 1. Data Ingestion (`/data_ingestion`)

- **Base collector**: Abstract interface; each platform implements `collect(symbols)` and `health_check()`.
- **Collectors**:
  - `danelfin_collector`: AI score, fundamental/technical/sentiment.
  - `seekingalpha_collector`: Quant rating, analyst recommendation.
  - `investingpro_collector`: Financial health, valuation.
  - `tradingview_collector`: Technical rating, RSI, signals.
- **Pipeline** (`pipeline.py`): Runs all collectors for the universe, returns a list of `StockAnalysis` (unified schema).
- **Unified schema** (`core/schemas.py`): `StockAnalysis` with `symbol`, `source`, `fundamental_score`, `technical_score`, `sentiment_score`, `analyst_rating`, `ai_rating`, `timestamp`, plus optional fields.

### 2. Analysis (`/analysis`)

- **Fundamental engine**: Aggregates fundamental scores by symbol (average across sources).
- **Technical engine**: Aggregates technical scores by symbol.
- **Ranking engine**: Composite score:
  - `0.35 * Fundamental + 0.35 * Technical + 0.20 * Analyst + 0.10 * Sentiment`
  - All inputs normalized 0–100; analyst text mapped to numeric.
- **Selection engine**: Filters by min market cap and min average volume; sorts by composite score; returns Top N (default 20).

### 3. Risk (`/risk`)

- **Stoploss engine**: `Stop Loss = Entry - k * ATR`, `Take Profit = Entry + m * ATR` (k, m configurable; vary by holding period).
- **Volatility engine**: ATR, support/resistance placeholders (to be wired to market data).
- **Holding periods**: Short (1–7d), Swing (1–4w), Medium (1–3m), Long (6–12m); ATR multipliers adjusted per period.

### 4. Daily Recommendation Engine (`core/daily_engine.py`)

1. Run ingestion for the universe.
2. Build composite scores.
3. Filter and select Top N.
4. For each pick: compute entry (placeholder from market data), ATR, stop loss, take profit, risk/reward, expected return %, position risk %.
5. Return list of `StockRecommendation`; optionally persist via repository and trigger alerts.

### 5. Database (`/database`)

- **Models**: `StockAnalysisModel`, `RecommendationModel`, `RecommendationPerformanceModel` (SQLAlchemy).
- **Repository**: `save_analyses`, `save_recommendations`, `get_latest_recommendations`.
- **Storage**: PostgreSQL (production); SQLite supported for dev.

### 6. API (`/api`)

- **FastAPI** with CORS, rate limiting (SlowAPI), OAuth2/API key auth (placeholder), subscription check.
- **Endpoints**:
  - `GET /health`
  - `GET /api/v1/recommendations` – list latest recommendations (cached).
  - `POST /api/v1/recommendations/refresh` – trigger full run (auth required).
  - Routers: `/api/v1/recommendations`, `/api/v1/analysis/stock/{symbol}`, `/api/v1/portfolio`, `/api/v1/performance`, `/api/v1/alerts`.

### 7. Workers (`/workers`)

- **Celery** with Redis broker/backend.
- **Tasks**:
  - `daily_recommendation_task`: Runs daily engine, saves recommendations, can trigger alerts.
  - `ingestion_task`: Periodic ingestion and save.
  - `alert_task`: Placeholder for email/push/Telegram/Slack.
- **Beat schedule**: Daily run (e.g. 24h; can be crontab for 6 AM); hourly ingestion.

### 8. Airflow (`/airflow/dags`)

- **DAG** `daily_stock_recommendations`: Schedule (e.g. 6 AM weekdays); single task that runs the same logic as the daily engine (ingestion → composite → selection → save).

### 9. Frontend (`/frontend`)

- **Next.js 14**, React, Tailwind, React Query.
- **Pages**: Home, Dashboard (Top 20 table), Stock Analysis (per-symbol detail), Portfolio, Performance.
- **API**: Uses `NEXT_PUBLIC_API_URL` or Next rewrites to backend.

### 10. Cloud (`/cloud/deployment_scripts`)

- **Docker Compose**: API, frontend, Celery worker, Celery beat, PostgreSQL, Redis.
- **Dockerfiles**: API, worker, frontend (multi-stage Next.js).
- **AWS**: Example script to build and push API image to ECR.

## Security

- OAuth2 / API key auth for protected endpoints.
- Encrypted credentials via env vars / secrets manager (no keys in code).
- HTTPS for all public endpoints; firewall and secure API keys for premium data sources.

## Scaling

- **Ingestion**: Parallelize per-source collectors; batch symbols.
- **API**: Stateless; scale behind load balancer.
- **Workers**: Scale Celery workers and queues (e.g. `daily`, `ingestion`, `alerts`).
- **DB**: Connection pooling; read replicas for dashboard reads if needed.
