#!/usr/bin/env python3
"""Seed the database with sample recommendations for local testing."""
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.chdir(root)

from core.daily_engine import generate_daily_recommendations
from core.schemas import HoldingPeriod
from database.repository import save_analyses, save_recommendations
from data_ingestion.pipeline import run_ingestion


def main():
    print("Running ingestion...")
    analyses = run_ingestion(limit_per_source=100)
    if analyses:
        save_analyses(analyses)
        print(f"Saved {len(analyses)} analyses.")
    print("Generating recommendations for each holding period...")
    all_recs = []
    for period in (HoldingPeriod.SHORT_TERM, HoldingPeriod.SWING, HoldingPeriod.MEDIUM_TERM, HoldingPeriod.LONG_TERM):
        recs = generate_daily_recommendations(holding_period=period, top_n=10)
        all_recs.extend(recs)
    if all_recs:
        save_recommendations(all_recs)
        print(f"Saved {len(all_recs)} recommendations (short/swing/medium/long).")
    else:
        print("No recommendations generated.")
    print("Done. Start the API and open the dashboard.")


if __name__ == "__main__":
    main()
