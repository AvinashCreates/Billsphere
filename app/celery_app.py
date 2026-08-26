from celery import Celery
from celery.schedules import crontab

from app.config.settings import settings

# Event -> Celery Task -> Redis Queue -> Worker -> Customer Notification
celery_app = Celery(
    "billing_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.notification_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Celery Beat schedule - periodic checks for renewal / expiry notifications.
# Requires a separate `celery -A app.celery_app beat` process to be running.
celery_app.conf.beat_schedule = {
    "check-expiring-subscriptions-daily": {
        "task": "app.tasks.notification_tasks.check_expiring_subscriptions",
        "schedule": crontab(hour=8, minute=0),
    },
}