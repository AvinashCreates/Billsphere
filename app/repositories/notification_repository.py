from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    notification: Notification,
):
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notification_by_id(
    db: Session,
    notification_id: int,
):
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )


def get_user_notifications(
    db: Session,
    user_id: int,
):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_all_notifications(
    db: Session,
):
    return (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_unread_count(
    db: Session,
    user_id: int,
):
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        .count()
    )


def update_notification(
    db: Session,
    notification: Notification,
):
    db.commit()
    db.refresh(notification)
    return notification