import random
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database.database import SessionLocal
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse, InvoiceUpdate
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.schemas.invoice import InvoiceResponse
from app.schemas.payment import PaymentResponse
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])

# Simulated payment failure rate — mimics real-world declined cards, etc.
PAYMENT_FAILURE_RATE = 0.2  # 20% of attempts fail


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


def generate_invoice_for_subscription(db: Session, subscription_id: int) -> Invoice:
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    subtotal = float(plan.price)
    tax_amount = round(subtotal * 0.18, 2)
    total = round(subtotal + tax_amount, 2)

    new_invoice = Invoice(
        invoice_number="TEMP",
        customer_id=sub.customer_id,
        subscription_id=sub.id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        status="pending",
        due_date=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    new_invoice.invoice_number = f"INV-{new_invoice.id:06d}"
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


@router.post("/generate/{subscription_id}", response_model=InvoiceResponse)
def generate_invoice(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return generate_invoice_for_subscription(db, subscription_id)


@router.get("/", response_model=list[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        return db.query(Invoice).all()

    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        return []
    return db.query(Invoice).filter(Invoice.customer_id == customer.id).all()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if current_user.role != "admin":
        customer = db.query(Customer).filter(Customer.email == current_user.email).first()
        if not customer or invoice.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this invoice")

    return invoice


@router.post("/{invoice_id}/pay", response_model=PaymentResponse)
def pay_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulates a payment attempt against a mock payment gateway.
    Randomly succeeds or fails (PAYMENT_FAILURE_RATE controls the odds),
    mimicking real-world card declines / network issues.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Ownership check for non-admins
    if current_user.role != "admin":
        customer = db.query(Customer).filter(Customer.email == current_user.email).first()
        if not customer or invoice.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized to pay this invoice")

    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice is already paid")

    # ---- Mock gateway call ----
    succeeded = random.random() > PAYMENT_FAILURE_RATE
    fake_gateway_reference = f"mock_txn_{uuid.uuid4().hex[:12]}"

    payment = Payment(
        invoice_id=invoice.id,
        amount=invoice.total,
        status="succeeded" if succeeded else "failed",
        gateway_reference=fake_gateway_reference,
    )
    db.add(payment)

    if succeeded:
        invoice.status = "paid"
        invoice.paid_at = datetime.now(timezone.utc)

        # If the related subscription was past_due, a successful payment brings it back
        sub = db.query(Subscription).filter(Subscription.id == invoice.subscription_id).first()
        if sub and sub.status == "past_due":
            sub.status = "active"
            log_event(db, "subscription", sub.id, "subscription.reactivated_after_payment", current_user.email)

        log_event(db, "invoice", invoice.id, "invoice.paid", current_user.email)
    else:
        log_event(db, "invoice", invoice.id, "invoice.payment_failed", current_user.email)

    db.commit()
    db.refresh(payment)
    return payment
# ---- Add these imports near the top of invoices.py if not already present ----
# from app.schemas.invoice import InvoiceUpdate   (create this schema, see below)

@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    update: "InvoiceUpdate",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(invoice, key, value)

    db.commit()
    db.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Cannot delete a paid invoice")

    db.delete(invoice)
    db.commit()
    return {"detail": "Invoice deleted"}


@router.get("/{invoice_id}/line-items")
def get_invoice_line_items(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    No separate line_items table exists yet, so this derives a simple
    breakdown from the invoice's own subtotal/tax fields. Can be replaced
    with a real InvoiceLineItem table later if per-item detail is needed.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if current_user.role != "admin":
        customer = db.query(Customer).filter(Customer.email == current_user.email).first()
        if not customer or invoice.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return {
        "invoice_number": invoice.invoice_number,
        "line_items": [
            {"description": "Subscription charge", "amount": float(invoice.subtotal)},
            {"description": "Tax", "amount": float(invoice.tax_amount)},
        ],
        "total": float(invoice.total),
    }


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generates a simple invoice PDF on the fly using reportlab."""
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from fastapi.responses import StreamingResponse

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if current_user.role != "admin":
        customer = db.query(Customer).filter(Customer.email == current_user.email).first()
        if not customer or invoice.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "BillSphere Invoice")

    c.setFont("Helvetica", 11)
    y = height - 110
    lines = [
        f"Invoice Number: {invoice.invoice_number}",
        f"Status: {invoice.status}",
        f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}",
        "",
        f"Subtotal: ${invoice.subtotal}",
        f"Tax: ${invoice.tax_amount}",
        f"Total: ${invoice.total}",
    ]
    for line in lines:
        c.drawString(72, y, line)
        y -= 20

    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"},
    )