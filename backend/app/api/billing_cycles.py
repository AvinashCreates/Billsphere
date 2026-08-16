from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.database import SessionLocal
from app.models.billing_cycle import BillingCycle
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog
from app.schemas.billing_cycle import BillingCycleResponse
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

# Reuses the invoice-generation logic already built in invoices.py so a
# billing cycle being "processed" produces the exact same kind of invoice.
from app.api.invoices import generate_invoice_for_subscription

router = APIRouter(prefix="/billing-cycles", tags=["Billing Cycles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_event(db: Session, entity_id: int, event: str, actor: str):
    entry = AuditLog(entity_type="billing_cycle", entity_id=entity_id, event=event, actor=actor)
    db.add(entry)
    db.commit()


@router.get("/subscription/{subscription_id}", response_model=list[BillingCycleResponse])
def list_subscription_cycles(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(BillingCycle)
        .filter(BillingCycle.subscription_id == subscription_id)
        .order_by(BillingCycle.cycle_start.desc())
        .all()
    )


@router.post("/subscription/{subscription_id}/start", response_model=BillingCycleResponse)
def start_cycle(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Opens a new billing cycle record matching the subscription's current period."""
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    new_cycle = BillingCycle(
        subscription_id=sub.id,
        cycle_start=sub.current_period_start,
        cycle_end=sub.current_period_end,
        status="pending",
    )
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)

    log_event(db, new_cycle.id, "billing_cycle.started", current_user.email)
    return new_cycle


@router.post("/subscription/{subscription_id}/process", response_model=BillingCycleResponse)
def process_cycle(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Finds the subscription's latest pending cycle and generates its invoice."""
    cycle = (
        db.query(BillingCycle)
        .filter(BillingCycle.subscription_id == subscription_id, BillingCycle.status == "pending")
        .order_by(BillingCycle.cycle_start.desc())
        .first()
    )
    if not cycle:
        raise HTTPException(status_code=404, detail="No pending billing cycle found for this subscription")

    generate_invoice_for_subscription(db, subscription_id)

    cycle.status = "invoiced"
    db.commit()
    db.refresh(cycle)

    log_event(db, cycle.id, "billing_cycle.processed", current_user.email)
    return cycle


@router.post("/process-due")
def process_due_cycles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Admin-triggered equivalent of what the Celery scheduler does automatically."""
    now = datetime.now(timezone.utc)
    due_cycles = (
        db.query(BillingCycle)
        .filter(BillingCycle.status == "pending", BillingCycle.cycle_end <= now)
        .all()
    )

    processed_ids = []
    for cycle in due_cycles:
        generate_invoice_for_subscription(db, cycle.subscription_id)
        cycle.status = "invoiced"
        log_event(db, cycle.id, "billing_cycle.auto_processed", current_user.email)
        processed_ids.append(cycle.id)

    db.commit()
    return {"processed_cycle_ids": processed_ids}