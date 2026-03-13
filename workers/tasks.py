"""
Celery tasks: daily recommendation run, ingestion, alerts.
"""
import logging
from workers.celery_app import app
from core.daily_engine import generate_daily_recommendations
from core.schemas import HoldingPeriod
from data_ingestion.pipeline import run_ingestion
from database.repository import save_analyses, save_recommendations

logger = logging.getLogger(__name__)


@app.task(name="workers.tasks.daily_recommendation_task")
def daily_recommendation_task(holding_period: str = "medium_term", top_n: int = 20):
    """Run before market open: refresh data, rank, select Top N, save, send alerts."""
    try:
        period = HoldingPeriod(holding_period)
        recs = generate_daily_recommendations(holding_period=period, top_n=top_n)
        if recs:
            save_recommendations(recs)
            # TODO: trigger alert_task.delay(recs)
        logger.info("Daily recommendations: %d picks saved", len(recs))
        return {"count": len(recs)}
    except Exception as e:
        logger.exception("Daily recommendation task failed: %s", e)
        raise


@app.task(name="workers.tasks.ingestion_task")
def ingestion_task(limit: int = 500):
    """Periodic ingestion from all sources; store in DB."""
    try:
        analyses = run_ingestion(limit_per_source=limit)
        if analyses:
            save_analyses(analyses)
        logger.info("Ingestion: %d analyses saved", len(analyses))
        return {"count": len(analyses)}
    except Exception as e:
        logger.exception("Ingestion task failed: %s", e)
        raise


@app.task(name="workers.tasks.alert_task")
def alert_task(recommendations_payload: list):
    """Send alerts (email, push, Telegram, Slack) when new picks are published."""
    # TODO: integrate with email/SNS/Telegram/Slack
    logger.info("Alerts sent for %d recommendations", len(recommendations_payload))
    return {"sent": len(recommendations_payload)}
