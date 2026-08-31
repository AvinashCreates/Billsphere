from datetime import datetime, UTC, timedelta

from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.database.database import SessionLocal
from app.models.subscription import Subscription
from app.models.notification import Notification

from app.services.notifications import (
    notify_subscription_renewal_due,
    notify_subscription_expired,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

# Send renewal reminder when subscription expires
# within this many days.

RENEWAL_REMINDER_DAYS = 3


# ==========================================================
# CELERY TEST TASK
# ==========================================================

@celery_app.task
def test_task():

    timestamp = datetime.now(UTC).isoformat()

    message = (
        f"Celery test task executed at {timestamp}"
    )

    print(message)

    return message


# ==========================================================
# SUBSCRIPTION SCHEDULER
# ==========================================================

@celery_app.task(
    name="check_subscriptions"
)
def check_subscriptions():

    db: Session = SessionLocal()

    try:

        now = datetime.now(UTC)

        # --------------------------------------------------
        # 1. Find subscriptions approaching expiry
        # --------------------------------------------------

        reminder_limit = (
            now + timedelta(
                days=RENEWAL_REMINDER_DAYS
            )
        )

        approaching_subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.status == "active",

                Subscription.current_period_end > now,

                Subscription.current_period_end <= reminder_limit,

                # IMPORTANT:
                # Only subscriptions for which
                # reminder has not already been sent.
                Subscription.renewal_reminder_sent.is_(False),
            )
            .all()
        )

        reminder_count = 0

        for subscription in approaching_subscriptions:

            print(
                f"Subscription {subscription.id} "
                f"is approaching expiry."
            )

            # --------------------------------------------------
            # Mark reminder as sent BEFORE queuing the task.
            # This prevents duplicate reminders when Celery Beat
            # runs again.
            # --------------------------------------------------

            subscription.renewal_reminder_sent = True

            send_renewal_reminder.delay(
                subscription.id
            )

            reminder_count += 1

        # --------------------------------------------------
        # 2. Find expired subscriptions
        # --------------------------------------------------

        expired_subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.status == "active",

                Subscription.current_period_end <= now,
            )
            .all()
        )

        expired_count = 0
        newly_expired_ids = []

        for subscription in expired_subscriptions:

            subscription.status = "expired"

            expired_count += 1
            newly_expired_ids.append(
                (subscription.id, subscription.user_id)
            )

            print(
                f"Subscription "
                f"{subscription.id} "
                f"has expired."
            )

        # --------------------------------------------------
        # Commit all changes
        # --------------------------------------------------

        db.commit()

        # --------------------------------------------------
        # Task 3 integration: fire expiry notifications only
        # AFTER the status change is safely committed, so a
        # notification is never created for a subscription
        # whose "expired" status didn't actually persist.
        # --------------------------------------------------

        for subscription_id, user_id in newly_expired_ids:
            notify_subscription_expired(db, user_id, subscription_id)

        return {
            "checked_at": now.isoformat(),

            "approaching_renewals": reminder_count,

            "expired_subscriptions": expired_count,
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ==========================================================
# RENEWAL REMINDER TASK
# ==========================================================

@celery_app.task(
    name="send_renewal_reminder"
)
def send_renewal_reminder(
    subscription_id: int
):

    print(
        f"Renewal reminder for "
        f"subscription {subscription_id}"
    )

    db: Session = SessionLocal()

    try:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.id == subscription_id)
            .first()
        )

        if not subscription:
            print(
                f"send_renewal_reminder: subscription "
                f"{subscription_id} not found, skipping."
            )
            return {
                "subscription_id": subscription_id,
                "message": "Subscription not found",
            }

        now = datetime.now(UTC)
        period_end = subscription.current_period_end

        if period_end.tzinfo is None:
            period_end = period_end.replace(tzinfo=UTC)

        days_left = max((period_end - now).days, 0)

        notify_subscription_renewal_due(
            db,
            subscription.user_id,
            subscription.id,
            days_left,
        )

        return {
            "subscription_id": subscription_id,
            "message": "Renewal reminder triggered",
            "days_left": days_left,
        }

    finally:
        db.close()


# ==========================================================
# NOTIFICATION DELIVERY TASK
# ==========================================================
#
# Worker-side delivery task for Task 3. Pulled off the Redis queue by
# the SAME worker process as the tasks above (registered on this app's
# celery_app, not a separate one) after a notification is queued via
# app.services.notifications._create_and_queue().

@celery_app.task(
    name="send_notification_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_notification_task(self, notification_id: int):

    db: Session = SessionLocal()

    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            print(
                f"send_notification_task: notification "
                f"{notification_id} not found, skipping."
            )
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
            print(f"Failed to deliver notification {notification_id}: {exc}")
            raise self.retry(exc=exc)

    finally:
        db.close()


def _send_email(notification: Notification):
    """
    Placeholder for real email delivery (SMTP / SendGrid / SES / etc).
    For now this just logs, so the pipeline is fully testable without
    any email provider credentials. Swap the body of this function for
    a real provider call when real SMTP credentials are available -
    everything upstream (queueing, retries, status tracking) stays the
    same.
    """
    print(
        f"EMAIL -> user_id={notification.user_id} | "
        f"{notification.title} | {notification.message}"
    )
