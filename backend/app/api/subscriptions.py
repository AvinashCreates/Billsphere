from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from datetime import datetime, timedelta, timezone
from app.database.database import SessionLocal
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.models.plan import Plan
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionCancelRequest,
    SubscriptionResponse,
)
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.subscription_logic import period_length_days, log_event, promote_pending_subscription
from app.workers.email_tasks import (
    send_subscription_confirmation,
    send_trial_activated_email,
    send_cancellation_email,
    send_reactivation_email,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_customer(db: Session, user: User) -> Customer:
    customer = db.query(Customer).filter(Customer.email == user.email).first()
    if customer:
        return customer

    new_customer = Customer(
        name=user.email.split("@")[0],
        email=user.email,
        billing_country="IN",
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def get_owned_subscription(db: Session, sub_id: int, current_user: User) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if current_user.role == "admin":
        return sub

    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer or sub.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this subscription")

    return sub


# ---------------------------------------------------------------------
# CREATE — same-platform queuing, plus trial-vs-pay branching
# ---------------------------------------------------------------------
@router.post("/", response_model=SubscriptionResponse)
def subscribe(
    sub: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status != "active":
        raise HTTPException(status_code=400, detail="This plan is not currently available")

    customer = get_or_create_customer(db, current_user)
    now = datetime.now(timezone.utc)

    running_same_platform = (
        db.query(Subscription)
        .join(Plan, Plan.id == Subscription.plan_id)
        .filter(
            Subscription.customer_id == customer.id,
            Subscription.status.in_(["active", "trial"]),
            Plan.name == plan.name,
        )
        .first()
    )

    already_pending = (
        db.query(Subscription)
        .join(Plan, Plan.id == Subscription.plan_id)
        .filter(
            Subscription.customer_id == customer.id,
            Subscription.status == "pending",
            Plan.name == plan.name,
        )
        .first()
    )
    if already_pending:
        raise HTTPException(status_code=400, detail=f"You already have a pending {plan.name} plan queued")

    if running_same_platform:
        # Queue it — auto-activates once the currently running plan ends. No email here;
        # the customer already gets one when it actually goes live.
        new_sub = Subscription(
            customer_id=customer.id,
            plan_id=plan.id,
            status="pending",
            trial_ends_at=None,
            current_period_start=running_same_platform.current_period_end,
            current_period_end=running_same_platform.current_period_end + timedelta(days=period_length_days(plan)),
            cancel_at_period_end=False,
        )
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)
        log_event(db, new_sub.id, "subscription.queued_pending", current_user.email)
        return new_sub

    # No conflict — decide trial vs paid based on the plan and the customer's choice
    effective_trial_days = 0 if sub.skip_trial else plan.trial_period_days

    if effective_trial_days and effective_trial_days > 0:
        status_value = "trial"
        trial_ends_at = now + timedelta(days=effective_trial_days)
        period_end = trial_ends_at
    else:
        status_value = "active"
        trial_ends_at = None
        period_end = now + timedelta(days=period_length_days(plan))

    new_sub = Subscription(
        customer_id=customer.id,
        plan_id=plan.id,
        status=status_value,
        trial_ends_at=trial_ends_at,
        current_period_start=now,
        current_period_end=period_end,
        cancel_at_period_end=False,
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    log_event(db, new_sub.id, f"subscription.created:{status_value}", current_user.email)

    if status_value == "trial":
        send_trial_activated_email.delay(
            customer.email, customer.name, plan.name, effective_trial_days, trial_ends_at.isoformat(),
        )
    else:
        send_subscription_confirmation.delay(
            customer.email, customer.name, plan.name, plan.billing_interval, period_end.isoformat(),
        )

    return new_sub


# ---------------------------------------------------------------------
# LIST ALL (admin)
# ---------------------------------------------------------------------
@router.get("/")
def list_all_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    subs = db.query(Subscription).all()
    result = []

    for sub in subs:
        customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()

        result.append({
            "id": sub.id,
            "status": sub.status,
            "trial_ends_at": sub.trial_ends_at,
            "current_period_start": sub.current_period_start,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "customer_id": sub.customer_id,
            "customer_name": customer.name if customer else None,
            "customer_email": customer.email if customer else None,
            "plan_id": sub.plan_id,
            "plan_name": plan.name if plan else None,
            "plan_price": float(plan.price) if plan else None,
        })

    return result


# ---------------------------------------------------------------------
# LIST MINE
# ---------------------------------------------------------------------
@router.get("/me")
def my_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        return []

    subs = db.query(Subscription).filter(Subscription.customer_id == customer.id).all()
    result = []
    for sub in subs:
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
        result.append({
            "id": sub.id,
            "plan_id": sub.plan_id,
            "plan_name": plan.name if plan else None,
            "billing_interval": plan.billing_interval if plan else None,
            "price": float(plan.price) if plan else None,
            "status": sub.status,
            "trial_ends_at": sub.trial_ends_at,
            "current_period_start": sub.current_period_start,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
        })
    return result


# ---------------------------------------------------------------------
# STATS (admin)
# ---------------------------------------------------------------------
@router.get("/stats")
def subscription_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    rows = (
        db.query(Subscription.status, sql_func.count(Subscription.id))
        .group_by(Subscription.status)
        .all()
    )
    stats = {status: count for status, count in rows}
    for s in ["trial", "active", "past_due", "cancelled", "pending"]:
        stats.setdefault(s, 0)
    return stats


# ---------------------------------------------------------------------
# GET single subscription
# ---------------------------------------------------------------------
@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_subscription(db, subscription_id, current_user)


# ---------------------------------------------------------------------
# UPDATE subscription (change plan / toggle cancel_at_period_end)
# ---------------------------------------------------------------------
@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    update: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = get_owned_subscription(db, subscription_id, current_user)

    if sub.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot update a cancelled subscription")

    if update.plan_id is not None:
        new_plan = db.query(Plan).filter(Plan.id == update.plan_id).first()
        if not new_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        sub.plan_id = new_plan.id
        log_event(db, sub.id, f"subscription.plan_changed:{new_plan.id}", current_user.email)

    if update.cancel_at_period_end is not None:
        sub.cancel_at_period_end = update.cancel_at_period_end

    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------
# CANCEL — immediate promotes a pending plan; both branches send a cancellation email
# ---------------------------------------------------------------------
@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: int,
    cancel: SubscriptionCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = get_owned_subscription(db, subscription_id, current_user)

    if sub.status == "cancelled":
        raise HTTPException(status_code=400, detail="Subscription is already cancelled")

    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()

    if cancel.immediate:
        sub.status = "cancelled"
        sub.cancel_at_period_end = False
        sub.current_period_end = datetime.now(timezone.utc)
        log_event(db, sub.id, "subscription.cancelled_immediately", current_user.email)
        db.commit()
        db.refresh(sub)

        if plan and customer:
            send_cancellation_email.delay(
                customer.email, customer.name, plan.name, True, sub.current_period_end.isoformat(),
            )
            promote_pending_subscription(db, sub.customer_id, plan.name, current_user.email)
    else:
        sub.cancel_at_period_end = True
        log_event(db, sub.id, "subscription.cancel_scheduled_at_period_end", current_user.email)
        db.commit()
        db.refresh(sub)

        if plan and customer:
            send_cancellation_email.delay(
                customer.email, customer.name, plan.name, False, sub.current_period_end.isoformat(),
            )

    return sub


# ---------------------------------------------------------------------
# EXTEND
# ---------------------------------------------------------------------
@router.post("/{subscription_id}/extend", response_model=SubscriptionResponse)
def extend_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = get_owned_subscription(db, subscription_id, current_user)

    if sub.status not in ("active", "trial"):
        raise HTTPException(status_code=400, detail="Only active or trial subscriptions can be extended")

    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    sub.current_period_end = sub.current_period_end + timedelta(days=period_length_days(plan))
    db.commit()
    db.refresh(sub)

    log_event(db, sub.id, "subscription.extended", current_user.email)
    return sub


# ---------------------------------------------------------------------
# CONVERT TRIAL → PAID
# ---------------------------------------------------------------------
@router.post("/{subscription_id}/convert-trial", response_model=SubscriptionResponse)
def convert_trial_to_paid(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = get_owned_subscription(db, subscription_id, current_user)
    if sub.status != "trial":
        raise HTTPException(status_code=400, detail="Only trial subscriptions can be converted")

    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    now = datetime.now(timezone.utc)
    sub.status = "active"
    sub.trial_ends_at = None
    sub.current_period_start = now
    sub.current_period_end = now + timedelta(days=period_length_days(plan))
    db.commit()
    db.refresh(sub)

    log_event(db, sub.id, "subscription.trial_converted_to_paid", current_user.email)

    customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()
    if customer:
        send_subscription_confirmation.delay(
            customer.email, customer.name, plan.name, plan.billing_interval, sub.current_period_end.isoformat(),
        )

    return sub


# ---------------------------------------------------------------------
# RENEW — past_due recovery; sends the reactivation email
# ---------------------------------------------------------------------
@router.post("/{subscription_id}/renew", response_model=SubscriptionResponse)
def renew_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = get_owned_subscription(db, subscription_id, current_user)

    if sub.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot renew a cancelled subscription")

    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    now = datetime.now(timezone.utc)
    sub.current_period_start = now
    sub.current_period_end = now + timedelta(days=period_length_days(plan))
    sub.status = "active"
    sub.cancel_at_period_end = False

    db.commit()
    db.refresh(sub)

    log_event(db, sub.id, "subscription.renewed", current_user.email)

    customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()
    if customer:
        send_reactivation_email.delay(customer.email, customer.name, plan.name, sub.current_period_end.isoformat())

    return sub


# ---------------------------------------------------------------------
# EXPIRE (admin manual trigger)
# ---------------------------------------------------------------------
@router.post("/{subscription_id}/expire", response_model=SubscriptionResponse)
def expire_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.status == "cancelled":
        raise HTTPException(status_code=400, detail="Subscription is already cancelled")

    if sub.cancel_at_period_end:
        sub.status = "cancelled"
        log_event(db, sub.id, "subscription.expired_to_cancelled", current_user.email)
    else:
        sub.status = "past_due"
        log_event(db, sub.id, "subscription.expired_to_past_due", current_user.email)

    db.commit()
    db.refresh(sub)
    return sub