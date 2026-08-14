from datetime import datetime, UTC

from app.workers.celery_app import celery_app


@celery_app.task
def test_task():
    timestamp = datetime.now(UTC).isoformat()

    message = f"Celery test task executed at {timestamp}"

    print(message)

    return message