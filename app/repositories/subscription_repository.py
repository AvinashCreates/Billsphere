from sqlalchemy.orm import Session
from sqlalchemy import case

from app.models.subscription import Subscription


def create_subscription(
    db: Session,
    subscription: Subscription
):
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def get_user_subscription(
    db: Session,
    user_id: int
):
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .order_by(
            # Prefer an active subscription over any old
            # cancelled/expired ones; among ties, prefer
            # the most recently created row.
            case((Subscription.status == "active", 0), else_=1),
            Subscription.id.desc(),
        )
        .first()
    )


def get_all_subscriptions(
    db: Session
):
    return db.query(Subscription).all()

def get_active_subscription(
    db: Session,
    user_id: int,
):
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        )
        .first()
    )


def update_subscription(
    db: Session,
    subscription: Subscription,
):
    db.commit()
    db.refresh(subscription)
    return subscription

def get_subscription_by_id(
    db: Session,
    subscription_id: int,
):
    return (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id
        )
        .first()
    )