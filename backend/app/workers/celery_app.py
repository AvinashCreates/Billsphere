from celery import Celery

celery_app = Celery(
    "billing_platform",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.timezone = "UTC"

# Import tasks so Celery registers them
celery_app.autodiscover_tasks(["app.workers"])

# Beat schedule — runs the billing check periodically
celery_app.conf.beat_schedule = {
    "process-billing-cycles-every-minute": {
        "task": "app.workers.tasks.process_due_subscriptions",
        "schedule": 60.0,  # every 60 seconds, for demo purposes
        # In production this would be something like crontab(hour=0, minute=0) — once daily
    },
}
