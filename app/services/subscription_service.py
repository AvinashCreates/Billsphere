from sqlalchemy.orm import Session
from datetime import datetime, UTC, timedelta

from app.services.invoice_service import generate_invoice
from app.services.notifications import (
    notify_subscription_created,
    notify_subscription_blocked,
    notify_subscription_unblocked,
    notify_subscription_expired,
    notify_invoice_generated,
)
from app.models.subscription import Subscription
from app.models.plan import Plan

from app.schemas.subscription import SubscriptionCreate

from app.repositories.subscription_repository import (
    create_subscription,
    get_user_subscription,
    get_all_subscriptions,
    get_active_subscription,
    update_subscription,
    get_subscription_by_id,
)


# ==========================================================
# CREATE SUBSCRIPTION
# ==========================================================

def subscribe(
    db: Session,
    user_id: int,
    plan: SubscriptionCreate,
):
    # ------------------------------------------------------
    # 1. Check whether the selected plan exists
    # ------------------------------------------------------

    selected_plan = (
        db.query(Plan)
        .filter(Plan.id == plan.plan_id)
        .first()
    )

    if not selected_plan:
        raise ValueError(
            "Selected plan does not exist."
        )

    # ------------------------------------------------------
    # 2. Check whether the plan is active
    # ------------------------------------------------------

    if selected_plan.status != "active":
        raise ValueError(
            "Selected plan is currently inactive."
        )

    # ------------------------------------------------------
    # 3. Check whether user already has an active subscription
    # ------------------------------------------------------

    existing = get_active_subscription(
        db,
        user_id,
    )

    if existing:
        raise ValueError(
            "You already have an active subscription."
        )

    # ------------------------------------------------------
    # 4. Create subscription
    # ------------------------------------------------------

    period_start = datetime.now(UTC)

    period_end = period_start + timedelta(
        days=selected_plan.duration
    )

    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.plan_id,
        status="active",
        current_period_start=period_start,
        current_period_end=period_end,
    )

    subscription = create_subscription(
        db,
        subscription,
    )

    invoice = generate_invoice(
         db=db,
         subscription_id=subscription.id,
         user_id=subscription.user_id,
         amount=selected_plan.price,
         billing_period_start=subscription.current_period_start,
         billing_period_end=subscription.current_period_end,
    )

    # --- Task 3 integration: notify on subscribe + invoice generated ---
    notify_subscription_created(db, user_id, selected_plan)

    if invoice is not None:
        notify_invoice_generated(db, user_id, invoice.id, selected_plan.price)

    return subscription


# ==========================================================
# GET MY SUBSCRIPTION
# ==========================================================

def my_subscription(
    db: Session,
    user_id: int,
):
    return get_user_subscription(
        db,
        user_id,
    )


# ==========================================================
# GET ALL SUBSCRIPTIONS - ADMIN
# ==========================================================

def subscriptions(
    db: Session,
):
    return get_all_subscriptions(
        db
    )


# ==========================================================
# BLOCK SUBSCRIPTION - ADMIN
# ==========================================================

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

    subscription = update_subscription(
        db,
        subscription,
    )

    notify_subscription_blocked(db, subscription.user_id, subscription.id)

    return subscription


# ==========================================================
# UNBLOCK SUBSCRIPTION - ADMIN
# ==========================================================

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

    subscription = update_subscription(
        db,
        subscription,
    )

    notify_subscription_unblocked(db, subscription.user_id, subscription.id)

    return subscription


def get_subscription(
    db: Session,
    subscription_id: int,
):
    return get_subscription_by_id(
        db,
        subscription_id,
    )


def edit_subscription(
    db: Session,
    subscription_id: int,
    plan_id: int,
):
    subscription = get_subscription_by_id(
        db,
        subscription_id,
    )

    if not subscription:
        return None

    selected_plan = (
        db.query(Plan)
        .filter(
            Plan.id == plan_id
        )
        .first()
    )

    if not selected_plan:
        raise ValueError(
            "Selected plan does not exist."
        )

    if selected_plan.status != "active":
        raise ValueError(
            "Selected plan is currently inactive."
        )

    subscription.plan_id = plan_id

    return update_subscription(
        db,
        subscription,
    )


# ==========================================================
# CANCEL SUBSCRIPTION
# ==========================================================

def cancel_subscription(
    db: Session,
    subscription_id: int,
):
    subscription = get_subscription_by_id(
        db,
        subscription_id,
    )

    if not subscription:
        return None

    if subscription.status == "cancelled":
        raise ValueError(
            "Subscription is already cancelled."
        )

    subscription.status = "cancelled"

    return update_subscription(
        db,
        subscription,
    )


# ==========================================================
# RENEW SUBSCRIPTION
# ==========================================================

def renew_subscription(
    db: Session,
    subscription_id: int,
):
    subscription = get_subscription_by_id(
        db,
        subscription_id,
    )

    if not subscription:
        return None

    if subscription.status == "active":
        raise ValueError(
            "Subscription is already active."
        )

    if subscription.status != "cancelled":
        raise ValueError(
            "Only cancelled subscriptions can be renewed."
        )

    # Make sure the subscription's plan is still active
    selected_plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not selected_plan:
        raise ValueError(
            "Subscription plan does not exist."
        )

    if selected_plan.status != "active":
        raise ValueError(
            "Subscription plan is currently inactive."
        )

    subscription.status = "active"

    return update_subscription(
        db,
        subscription,
    )


# ==========================================================
# EXPIRE SUBSCRIPTION
# ==========================================================

def expire_subscription(
    db: Session,
    subscription_id: int,
):
    subscription = get_subscription_by_id(
        db,
        subscription_id,
    )

    if not subscription:
        return None

    if subscription.status == "expired":
        raise ValueError(
            "Subscription is already expired."
        )

    if subscription.status != "active":
        raise ValueError(
            "Only active subscriptions can be expired."
        )

    subscription.status = "expired"

    subscription = update_subscription(
        db,
        subscription,
    )

    notify_subscription_expired(db, subscription.user_id, subscription.id)

    return subscription
