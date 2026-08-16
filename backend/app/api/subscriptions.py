from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from datetime import datetime, timedelta, timezone
from app.database.database import SessionLocal
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.audit_log import AuditLog
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.refund import Refund
from app.services.proration_service import calculate_proration
from app.services.refund_service import calculate_unused_period_refund
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionCancelRequest,
    SubscriptionResponse,
)
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

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


def log_event(db: Session, entity_id: int, event: str, actor: str):
    entry = AuditLog(
        entity_type="subscription",
        entity_id=entity_id,
        event=event,
        actor=actor,
    )
    db.add(entry)
    db.commit()


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


def period_length_days(plan: Plan) -> int:
    return 365 if plan.billing_interval == "yearly" else 30


# ---------------------------------------------------------------------
# CREATE
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

    customer = get_or_create_customer(db, current_user)
    now = datetime.now(timezone.utc)

    # If the customer already has a live (active or trial) subscription,
    # the new one is queued as "pending" rather than starting right away.
    # It gets auto-promoted once the current one ends (see Celery task).
    existing_live_sub = (
        db.query(Subscription)
        .filter(
            Subscription.customer_id == customer.id,
            Subscription.status.in_(["active", "trial"]),
        )
        .first()
    )

    if plan.trial_period_days and plan.trial_period_days > 0:
        trial_ends_at = now + timedelta(days=plan.trial_period_days)
        period_end = trial_ends_at
        status_value = "pending" if existing_live_sub else "trial"
    else:
        trial_ends_at = None
        period_end = now + timedelta(days=period_length_days(plan))
        status_value = "pending" if existing_live_sub else "active"

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
    return new_sub


# ---------------------------------------------------------------------
# LIST MINE
# ---------------------------------------------------------------------
@router.get("/me", response_model=list[SubscriptionResponse])
def my_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        return []
    return db.query(Subscription).filter(Subscription.customer_id == customer.id).all()


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
    for s in ["trial", "active", "pending", "past_due", "cancelled"]:
        stats.setdefault(s, 0)
    return stats


# ---------------------------------------------------------------------
# GET single
# ---------------------------------------------------------------------
@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_subscription(db, subscription_id, current_user)


# ---------------------------------------------------------------------
# UPDATE
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

        old_plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()

        proration_result = None
        if old_plan and old_plan.id != new_plan.id:
            proration_result = calculate_proration(sub, old_plan, new_plan)

            # Only generate a payable invoice if the customer actually owes
            # money (upgrade case). A downgrade produces a credit, which we
            # log but don't invoice for in this simplified version.
            if proration_result["net_amount"] > 0:
                proration_invoice = Invoice(
                    invoice_number="TEMP",
                    customer_id=sub.customer_id,
                    subscription_id=sub.id,
                    subtotal=proration_result["net_amount"],
                    tax_amount=0,
                    total=proration_result["net_amount"],
                    status="pending",
                    due_date=datetime.now(timezone.utc) + timedelta(days=3),
                )
                db.add(proration_invoice)
                db.commit()
                db.refresh(proration_invoice)
                proration_invoice.invoice_number = f"INV-PRO-{proration_invoice.id:06d}"
                db.commit()

            log_event(
                db,
                sub.id,
                f"subscription.plan_changed:{new_plan.id}:proration_net={proration_result['net_amount']}",
                current_user.email,
            )
        else:
            log_event(db, sub.id, f"subscription.plan_changed:{new_plan.id}", current_user.email)

        sub.plan_id = new_plan.id

    if update.cancel_at_period_end is not None:
        sub.cancel_at_period_end = update.cancel_at_period_end

    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------
# CANCEL
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

    if cancel.immediate:
        # Calculate any unused-period refund BEFORE we touch current_period_end,
        # since the calculation depends on how much time was left.
        latest_paid_invoice = (
            db.query(Invoice)
            .filter(Invoice.subscription_id == sub.id, Invoice.status == "paid")
            .order_by(Invoice.created_at.desc())
            .first()
        )

        if latest_paid_invoice:
            succeeded_payment = (
                db.query(Payment)
                .filter(Payment.invoice_id == latest_paid_invoice.id, Payment.status == "succeeded")
                .order_by(Payment.attempted_at.desc())
                .first()
            )

            if succeeded_payment:
                refund_calc = calculate_unused_period_refund(sub, float(succeeded_payment.amount))

                if refund_calc["refund_amount"] > 0:
                    refund = Refund(
                        payment_id=succeeded_payment.id,
                        invoice_id=latest_paid_invoice.id,
                        subscription_id=sub.id,
                        amount=refund_calc["refund_amount"],
                        reason="cancellation_unused_period",
                    )
                    db.add(refund)
                    db.commit()
                    log_event(
                        db,
                        sub.id,
                        f"subscription.refund_issued:{refund_calc['refund_amount']}:days_remaining={refund_calc['days_remaining']}",
                        current_user.email,
                    )

        sub.status = "cancelled"
        sub.cancel_at_period_end = False
        sub.current_period_end = datetime.now(timezone.utc)
        log_event(db, sub.id, "subscription.cancelled_immediately", current_user.email)
    else:
        sub.cancel_at_period_end = True
        log_event(db, sub.id, "subscription.cancel_scheduled_at_period_end", current_user.email)

    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------
# RENEW / EXTEND
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
    return sub


# ---------------------------------------------------------------------
# EXPIRE (admin / system)
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