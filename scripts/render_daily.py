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
    all_recs = []
    for period in (
        HoldingPeriod.SHORT_TERM,
        HoldingPeriod.SWING,
        HoldingPeriod.MEDIUM_TERM,
        HoldingPeriod.LONG_TERM,
    ):
        recs = generate_daily_recommendations(holding_period=period, top_n=10)
        all_recs.extend(recs)
    if all_recs:
        save_recommendations(all_recs)
    print(len(all_recs), "recommendations saved (short/swing/medium/long)")
