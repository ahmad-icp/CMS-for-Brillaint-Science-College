from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "college_erp",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.maintenance"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "cleanup-expired-refresh-tokens-daily": {
            "task": "maintenance.cleanup_expired_refresh_tokens",
            "schedule": 86400.0,
        }
    },
)
