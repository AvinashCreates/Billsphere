from sqlalchemy.orm import Session

from app.models.subscription import Subscription

from app.schemas.subscription import SubscriptionCreate

from app.repositories.subscription_repository import (
    create_subscription,
    get_user_subscription,
    get_all_subscriptions,
)
from app.repositories.subscription_repository import (
    create_subscription,
    get_user_subscription,
    get_all_subscriptions,
    get_active_subscription,
    update_subscription,
)

def subscribe(
    db: Session,
    user_id: int,
    plan: SubscriptionCreate,
):

    existing = get_active_subscription(
        db,
        user_id,
    )

    if existing:
        raise ValueError(
            "You already have an active subscription."
        )

    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.plan_id,
    )

    return create_subscription(
        db,
        subscription,
    )


def my_subscription(
    db: Session,
    user_id: int,
):
    return get_user_subscription(
        db,
        user_id,
    )


def subscriptions(
    db: Session,
):
    return get_all_subscriptions(
        db
    )

def block_subscription(
    db: Session,
    subscription_id: int,
):

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id
        )
        .first()
    )

    if not subscription:
        return None

    subscription.status = "blocked"

    return update_subscription(
        db,
        subscription,
    )

def unblock_subscription(
    db: Session,
    subscription_id: int,
):

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id
        )
        .first()
    )

    if not subscription:
        return None

    subscription.status = "active"

    return update_subscription(
        db,
        subscription,
    )
