import logging
from datetime import datetime, timedelta, UTC

from app.celery_app import celery_app
from app.database.database import SessionLocal
from app.models.notification import Notification
from app.models.subscription import Subscription
from app.models.plan import Plan

logger = logging.getLogger("notifications")


@celery_app.task(
    name="app.tasks.notification_tasks.send_notification_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_notification_task(self, notification_id: int):
    """
    Worker-side delivery task. Pulled off the Redis queue by a running
    `celery -A app.celery_app worker` process.

    The DB row already exists (status="pending") by the time this runs -
    this task is only responsible for "delivering" it and updating status.
    """
    db = SessionLocal()

    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            logger.warning("Notification %s not found, skipping", notification_id)
            return

        try:
            if notification.channel == "email":
                _send_email(notification)
            # channel == "in_app" needs no extra delivery step - the DB
            # row itself is what the frontend polls / displays.

            notification.status = "sent"
            notification.sent_at = datetime.now(UTC)
            db.commit()

        except Exception as exc:
            notification.status = "failed"
            db.commit()
            logger.exception("Failed to deliver notification %s", notification_id)
            raise self.retry(exc=exc)

    finally:
        db.close()


def _send_email(notification: Notification):
    """
    Placeholder for real email delivery (SMTP / SendGrid / SES / etc).
    For now this just logs, so the pipeline is fully testable without
    any email provider credentials. Swap the body of this function for
    a real provider call when you're ready - everything upstream
    (queueing, retries, status tracking) stays the same.
    """
    logger.info(
        "EMAIL -> user_id=%s | %s | %s",
        notification.user_id,
        notification.title,
        notification.message,
    )


@celery_app.task(name="app.tasks.notification_tasks.check_expiring_subscriptions")
def check_expiring_subscriptions():
    """
    Periodic task (Celery Beat). Scans active subscriptions and queues a
    renewal reminder when a plan is about to expire, or an expiry
    notification (and status flip) once it has.
    """
    from app.services.notification_service import (
        notify_subscription_renewal_due,
        notify_subscription_expired,
    )

    db = SessionLocal()

    try:
        now = datetime.now(UTC).replace(tzinfo=None)

        subscriptions = (
            db.query(Subscription)
            .filter(Subscription.status == "active")
            .all()
        )

        for sub in subscriptions:
            plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()

            if not plan:
                continue

            subscribed_at = sub.subscribed_at
            if subscribed_at.tzinfo is not None:
                subscribed_at = subscribed_at.replace(tzinfo=None)

            expires_at = subscribed_at + timedelta(days=plan.duration)
            days_left = (expires_at - now).days

            if expires_at <= now:
                sub.status = "expired"
                db.commit()
                notify_subscription_expired(db, sub.user_id, sub.id)

            elif 0 <= days_left <= 3:
                notify_subscription_renewal_due(db, sub.user_id, sub.id, days_left)

    finally:
        db.close()