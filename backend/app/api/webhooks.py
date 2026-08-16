from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.database import SessionLocal
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog
from app.schemas.webhook import WebhookPaymentPayload

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# In a real system this would be a long random secret shared only with the
# payment provider, used to verify the webhook genuinely came from them.
WEBHOOK_SECRET = "mock-webhook-secret-2026"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_event(db: Session, entity_type: str, entity_id: int, event: str, actor: str = "webhook:payment_gateway"):
    entry = AuditLog(entity_type=entity_type, entity_id=entity_id, event=event, actor=actor)
    db.add(entry)
    db.commit()


@router.post("/payment")
def payment_webhook(
    payload: WebhookPaymentPayload,
    db: Session = Depends(get_db),
    x_webhook_secret: str = Header(None),
):
    """
    Simulates an incoming webhook from a payment gateway confirming the
    real outcome of a payment attempt. Verified via a shared secret header
    rather than a user login, since the caller here is the gateway itself,
    not a logged-in person.
    """
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payment = (
        db.query(Payment)
        .filter(Payment.gateway_reference == payload.gateway_reference)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="No matching payment found for this reference")

    if payment.status in ("succeeded", "failed") and payment.status == payload.status:
        # Idempotency: webhook delivered twice with the same outcome — no-op
        return {"detail": "Webhook already processed, no change made"}

    payment.status = payload.status
    db.commit()

    invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()

    if payload.status == "succeeded" and invoice:
        invoice.status = "paid"
        invoice.paid_at = datetime.now(timezone.utc)

        sub = db.query(Subscription).filter(Subscription.id == invoice.subscription_id).first()
        if sub and sub.status == "past_due":
            sub.status = "active"
            log_event(db, "subscription", sub.id, "subscription.reactivated_after_webhook_confirmation")

        log_event(db, "invoice", invoice.id, "invoice.paid_via_webhook")

    elif payload.status == "failed" and invoice:
        log_event(db, "invoice", invoice.id, "invoice.payment_failed_via_webhook")

    db.commit()
    return {"detail": f"Payment {payload.gateway_reference} marked as {payload.status}"}