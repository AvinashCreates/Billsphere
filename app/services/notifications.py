from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

from app.repositories.notification_repository import (
    create_notification,
    get_notification_by_id,
    get_user_notifications,
    get_all_notifications,
    get_unread_count,
    update_notification,
)


def _create_and_queue(
    db: Session,
    data: NotificationCreate,
):
    """
    Event -> Celery Task -> Redis Queue -> Worker -> Customer Notification

    Writes the notification to the DB in "pending" state, then hands the
    notification id off to Celery. The worker (running separately) picks
    the task up from Redis and actually delivers it.
    """
    notification = Notification(
        user_id=data.user_id,
        type=data.type,
        title=data.title,
        message=data.message,
        channel=data.channel,
        related_id=data.related_id,
        status="pending",
    )

    notification = create_notification(db, notification)

    # Imported locally so importing notification_service never requires a
    # running Celery/Redis connection (e.g. simple unit tests still work).
    from app.workers.tasks import send_notification_task

    try:
            send_notification_task.apply_async(args=[notification.id], ignore_result=True)

    except Exception as e:
            
            print(f"[notifications] failed to queue task: {e}")  # or proper logging

    return notification


# ------------------------------------------------------------------
# Event-specific triggers
# Call these from wherever the underlying event happens (subscription
# service today; invoice/payment services once those modules land).
# ------------------------------------------------------------------

def notify_subscription_created(db: Session, user_id: int, plan):
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="subscription",
            title="Subscription Activated",
            message=f"Your subscription to '{plan.name}' is now active.",
            channel="email",
            related_id=plan.id,
        ),
    )


def notify_subscription_blocked(db: Session, user_id: int, subscription_id: int):
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="expiry",
            title="Subscription Suspended",
            message="Your subscription has been suspended by the administrator.",
            channel="email",
            related_id=subscription_id,
        ),
    )


def notify_subscription_unblocked(db: Session, user_id: int, subscription_id: int):
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="subscription",
            title="Subscription Reactivated",
            message="Your subscription has been reactivated.",
            channel="email",
            related_id=subscription_id,
        ),
    )


def notify_subscription_renewal_due(db: Session, user_id: int, subscription_id: int, days_left: int):
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="renewal",
            title="Subscription Renewal Reminder",
            message=f"Your subscription expires in {days_left} day(s). Renew to avoid interruption.",
            channel="email",
            related_id=subscription_id,
        ),
    )


def notify_subscription_expired(db: Session, user_id: int, subscription_id: int):
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="expiry",
            title="Subscription Expired",
            message="Your subscription has expired. Renew now to continue using the service.",
            channel="email",
            related_id=subscription_id,
        ),
    )


def notify_invoice_generated(db: Session, user_id: int, invoice_id: int, amount: float):
    """Call this from the Invoice module once app/services/invoice_service.py exists."""
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="invoice",
            title="New Invoice Generated",
            message=f"A new invoice of ${amount:.2f} has been generated for your account.",
            channel="email",
            related_id=invoice_id,
        ),
    )


def notify_payment_success(db: Session, user_id: int, payment_id: int, amount: float):
    """Call this from the Payment module once app/services/payment_service.py exists."""
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="payment_success",
            title="Payment Successful",
            message=f"Your payment of ${amount:.2f} was received successfully.",
            channel="email",
            related_id=payment_id,
        ),
    )


def notify_payment_failed(db: Session, user_id: int, payment_id: int, amount: float, reason: str = ""):
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="payment_failure",
            title="Payment Failed",
            message=f"Your payment of ${amount:.2f} could not be processed. {reason}".strip(),
            channel="email",
            related_id=payment_id,
        ),
    )


def send_test_notification(db: Session, user_id: int, title: str, message: str):
    """Admin-triggered notification, useful for verifying the Redis/Celery pipeline end to end."""
    return _create_and_queue(
        db,
        NotificationCreate(
            user_id=user_id,
            type="general",
            title=title,
            message=message,
            channel="email",
        ),
    )


# ------------------------------------------------------------------
# Query / history operations
# ------------------------------------------------------------------

def fetch_my_notifications(db: Session, user_id: int):
    return get_user_notifications(db, user_id)


def fetch_all_notifications(db: Session):
    return get_all_notifications(db)


def unread_count(db: Session, user_id: int):
    return get_unread_count(db, user_id)


def mark_as_read(db: Session, notification_id: int, user_id: int):
    notification = get_notification_by_id(db, notification_id)

    if not notification or notification.user_id != user_id:
        return None

    notification.is_read = True
    notification.read_at = datetime.now(UTC)

    return update_notification(db, notification)


def mark_all_as_read(db: Session, user_id: int):
    notifications = get_user_notifications(db, user_id)

    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(UTC)
            update_notification(db, notification)

    return True