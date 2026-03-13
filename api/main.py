"""
FastAPI application: recommendations, auth, rate limiting.
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.auth import get_current_user_optional, require_subscription
from api.routes import analysis, portfolio, performance, alerts
from config import TOP_N_RECOMMENDATIONS
from core.schemas import HoldingPeriod
from core.daily_engine import generate_daily_recommendations
from database.repository import get_latest_recommendations, save_analyses, save_recommendations
from data_ingestion.pipeline import run_ingestion

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database.models import Base
    from database.repository import _engine
    Base.metadata.create_all(_engine)
    yield
    pass


app = FastAPI(
    title="Stock AI Platform API",
    description="Daily stock recommendations from multi-source analysis",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/integrations/status")
def integrations_status():
    """Which premium data sources have credentials configured (no values exposed)."""
    return {
        "danelfin": bool(os.getenv("DANELFIN_API_KEY")),
        "seeking_alpha": bool(os.getenv("SEEKING_ALPHA_API_KEY")),
        "investing_pro": bool(os.getenv("INVESTING_PRO_API_KEY")),
        "tradingview": bool(os.getenv("TRADINGVIEW_API_KEY")),
    }


@app.get("/api/v1/recommendations", response_model=list)
@limiter.limit("60/minute")
def list_recommendations(
    request: Request,
    since: datetime | None = Query(None, description="Only recommendations after this time"),
    limit: int = Query(TOP_N_RECOMMENDATIONS, ge=1, le=100),
    _=Depends(get_current_user_optional),
):
    """Top N daily stock picks (cached in DB)."""
    return get_latest_recommendations(since=since, limit=limit)


@app.post("/api/v1/recommendations/refresh")
@limiter.limit("10/minute")
def refresh_recommendations(
    request: Request,
    holding_period: HoldingPeriod = Query(HoldingPeriod.MEDIUM_TERM),
    top_n: int = Query(20, ge=1, le=50),
    _=Depends(require_subscription),
):
    """Trigger refresh: run ingestion, ranking, and save new Top N. Admin/scheduled use."""
    recs = generate_daily_recommendations(holding_period=holding_period, top_n=top_n)
    if recs:
        analyses = run_ingestion(limit_per_source=200)
        save_analyses(analyses)
        save_recommendations(recs)
    return {"count": len(recs), "recommendations": [r.model_dump() for r in recs]}


# Mount route modules (recommendations are defined above with rate limiting)
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(performance.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
