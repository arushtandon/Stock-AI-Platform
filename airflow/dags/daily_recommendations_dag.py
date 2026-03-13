"""
Airflow DAG: run daily recommendation pipeline before market open (e.g. 6 AM ET).
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default args
default_args = {
    "owner": "stock-ai",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_daily_pipeline():
    """Call the daily engine and persist results."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from core.daily_engine import generate_daily_recommendations
    from core.schemas import HoldingPeriod
    from database.repository import save_analyses, save_recommendations
    from data_ingestion.pipeline import run_ingestion
    analyses = run_ingestion(limit_per_source=500)
    if analyses:
        save_analyses(analyses)
    recs = generate_daily_recommendations(holding_period=HoldingPeriod.MEDIUM_TERM, top_n=20)
    if recs:
        save_recommendations(recs)
    return len(recs)


with DAG(
    dag_id="daily_stock_recommendations",
    default_args=default_args,
    description="Generate Top 20 stock recommendations daily before market open",
    schedule_interval="0 6 * * 1-5",  # 6 AM weekdays (adjust for timezone)
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["stock-ai", "recommendations"],
) as dag:
    task = PythonOperator(
        task_id="generate_and_save_recommendations",
        python_callable=run_daily_pipeline,
    )
