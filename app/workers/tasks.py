from datetime import datetime, UTC, timedelta

from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.database.database import SessionLocal
from app.models.subscription import Subscription


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

        for subscription in expired_subscriptions:

            subscription.status = "expired"

            expired_count += 1

            print(
                f"Subscription "
                f"{subscription.id} "
                f"has expired."
            )

        # --------------------------------------------------
        # Commit all changes
        # --------------------------------------------------

        db.commit()

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

    # ------------------------------------------------------
    # Email notification will be implemented later.
    # ------------------------------------------------------

    return {
        "subscription_id": subscription_id,

        "message": (
            "Renewal reminder triggered"
        ),
    }