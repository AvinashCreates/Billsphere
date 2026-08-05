from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.plan import Plan
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.workers.email_tasks import send_reactivation_email


def period_length_days(plan: Plan) -> int:
    return 365 if plan.billing_interval == "yearly" else 30


def log_event(db: Session, entity_id: int, event: str, actor: str):
    entry = AuditLog(entity_type="subscription", entity_id=entity_id, event=event, actor=actor)
    db.add(entry)
    db.commit()


def promote_pending_subscription(db: Session, customer_id: int, plan_name: str, actor: str = "system:auto-promote"):
    pending = (
        db.query(Subscription)
        .join(Plan, Plan.id == Subscription.plan_id)
        .filter(
            Subscription.customer_id == customer_id,
            Subscription.status == "pending",
            Plan.name == plan_name,
        )
        .order_by(Subscription.id.asc())
        .first()
    )
    if not pending:
        return None

    plan = db.query(Plan).filter(Plan.id == pending.plan_id).first()
    now = datetime.now(timezone.utc)

    if plan.trial_period_days and plan.trial_period_days > 0:
        pending.status = "trial"
        pending.trial_ends_at = now + timedelta(days=plan.trial_period_days)
        pending.current_period_end = pending.trial_ends_at
    else:
        pending.status = "active"
        pending.trial_ends_at = None
        pending.current_period_end = now + timedelta(days=period_length_days(plan))

    pending.current_period_start = now
    db.commit()
    db.refresh(pending)

    log_event(db, pending.id, f"subscription.promoted_from_pending:{pending.status}", actor)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        send_reactivation_email.delay(customer.email, customer.name, plan.name, pending.current_period_end.isoformat())

    return pending