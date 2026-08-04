import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "billing_platform",
    broker=redis_url,
    backend=redis_url,
    include=["app.workers.email_tasks", "app.workers.tasks"],
)

celery_app.conf.timezone = "UTC"

celery_app.autodiscover_tasks(["app.workers"])

# Beat schedule — runs the billing check periodically
celery_app.conf.beat_schedule = {
    "process-billing-cycles-every-minute": {
        "task": "app.workers.tasks.process_due_subscriptions",
        "schedule": 60.0,  # every 60 seconds, for demo purposes
        # In production this would be something like crontab(hour=0, minute=0) — once daily
    },
}
