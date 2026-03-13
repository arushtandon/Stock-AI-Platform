#!/usr/bin/env python3
"""Run daily recommendation pipeline (for Render cron job)."""
import os
import sys

# Render runs from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.daily_engine import generate_daily_recommendations
from core.schemas import HoldingPeriod
from database.repository import save_analyses, save_recommendations
from data_ingestion.pipeline import run_ingestion

if __name__ == "__main__":
    analyses = run_ingestion(limit_per_source=200)
    if analyses:
        save_analyses(analyses)
    recs = generate_daily_recommendations(holding_period=HoldingPeriod.MEDIUM_TERM, top_n=20)
    if recs:
        save_recommendations(recs)
    print(len(recs), "recommendations saved")
