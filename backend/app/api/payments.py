from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.refund import Refund
from app.models.audit_log import AuditLog
from app.schemas.payment import PaymentResponse
from app.schemas.refund import RefundResponse
from app.core.dependencies import require_role
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_event(db: Session, entity_type: str, entity_id: int, event: str, actor: str):
    entry = AuditLog(entity_type=entity_type, entity_id=entity_id, event=event, actor=actor)
    db.add(entry)
    db.commit()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/{payment_id}/refund", response_model=RefundResponse)
def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != "succeeded":
        raise HTTPException(
            status_code=400,
            detail=f"Only succeeded payments can be refunded (current status: {payment.status})",
        )

    payment.status = "refunded"
    db.commit()

    invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
    if invoice:
        invoice.status = "refunded"
        db.commit()
        log_event(db, "invoice", invoice.id, "invoice.refunded", current_user.email)

    refund = Refund(
        payment_id=payment.id,
        invoice_id=payment.invoice_id,
        subscription_id=invoice.subscription_id if invoice else None,
        amount=float(payment.amount),
        reason="admin_manual",
    )
    db.add(refund)
    db.commit()
    db.refresh(refund)

    log_event(db, "payment", payment.id, "payment.refunded", current_user.email)

    return refund
# Add these to app/api/payments.py, alongside your existing get_payment / refund_payment

@router.get("/", response_model=list[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return db.query(Payment).all()


@router.post("/{payment_id}/success", response_model=PaymentResponse)
def mark_payment_success(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """
    Admin/testing endpoint to manually force a payment to succeeded —
    separate from the automatic mock outcome in POST /invoices/{id}/pay,
    useful when testing downstream effects (invoice paid, subscription
    reactivated) without relying on the random success/fail simulation.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "succeeded"
    db.commit()

    invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
    if invoice:
        invoice.status = "paid"
        from datetime import datetime, timezone
        invoice.paid_at = datetime.now(timezone.utc)
        db.commit()
        log_event(db, "invoice", invoice.id, "invoice.paid", current_user.email)

    log_event(db, "payment", payment.id, "payment.marked_succeeded_manually", current_user.email)

    db.refresh(payment)
    return payment


@router.post("/{payment_id}/failed", response_model=PaymentResponse)
def mark_payment_failed(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "failed"
    db.commit()

    log_event(db, "payment", payment.id, "payment.marked_failed_manually", current_user.email)

    db.refresh(payment)
    return payment