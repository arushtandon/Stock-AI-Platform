"""
Celery app for 24/7 tasks: ingestion, re-ranking, alerts.
"""
from celery import Celery
from config import REDIS_URL

app = Celery(
    "stock_ai",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["workers.tasks"],
)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={"workers.tasks.daily_recommendation_task": {"queue": "daily"}},
    beat_schedule={
        "daily-recommendations": {
            "task": "workers.tasks.daily_recommendation_task",
            "schedule": 60.0 * 60 * 24,  # every 24h; use crontab(hour=6, minute=0) for pre-market
        },
        "continuous-ingestion": {
            "task": "workers.tasks.ingestion_task",
            "schedule": 60.0 * 60,  # every hour
        },
    },
)
