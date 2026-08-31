from celery import Celery

from app.config.settings import settings


celery_app = Celery(
    "billing_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)


celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,

    # ======================================================
    # CELERY BEAT SCHEDULE
    # ======================================================

    beat_schedule={
        "check-subscriptions-every-minute": {
            "task": "check_subscriptions",
            "schedule": 60.0,
        },
    },
)