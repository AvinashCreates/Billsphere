from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.invoice import Invoice
from app.models.invoice_line_item import InvoiceLineItem
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import (
    MockPaymentRequest,
    PaymentWebhookRequest,
)
from app.services.payment_gateway_service import payment_gateway


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def _apply_payment_event(
    db: Session,
    invoice: Invoice,
    event: str,
    amount: float,
    payment_method: str,
    transaction_id: str,
) -> dict:
    """
    Apply a payment gateway event to an invoice.

    Supported events:
        paid
        failed
        refunded

    Payment attempts are stored individually, so a failed payment
    followed by a successful retry creates two Payment records.
    """

    event = event.strip().lower()
    payment_method = payment_method.strip().lower()

    # ---------------------------------------------------------
    # Validate event before doing any database work
    # ---------------------------------------------------------
    if event not in {"paid", "failed", "refunded"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported payment event: {event}",
        )

    # ---------------------------------------------------------
    # Prevent duplicate transaction processing
    # ---------------------------------------------------------
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.transaction_id == transaction_id
        )
        .first()
    )

    if existing_payment:
        return {
            "message": "Duplicate payment event ignored.",
            "event": event,
            "invoice_id": invoice.id,
            "invoice_status": invoice.status,
            "payment_status": invoice.payment_status,
            "transaction_id": transaction_id,
        }

    # =========================================================
    # PAID
    # =========================================================
    if event == "paid":

        # Additional protection against paying an already-paid
        # invoice.
        successful_payment = (
            db.query(Payment)
            .filter(
                Payment.invoice_id == invoice.id,
                Payment.status == "success",
            )
            .first()
        )

        if successful_payment or invoice.payment_status == "paid":
            return {
                "message": (
                    "Invoice already paid. "
                    "Duplicate payment ignored."
                ),
                "event": event,
                "invoice_id": invoice.id,
                "invoice_status": invoice.status,
                "payment_status": invoice.payment_status,
                "transaction_id": transaction_id,
            }

        payment = Payment(
            invoice_id=invoice.id,
            user_id=invoice.user_id,
            amount=amount,
            payment_method=payment_method,
            status="success",
            transaction_id=transaction_id,
        )

        db.add(payment)

        invoice.status = "paid"
        invoice.payment_status = "paid"

        # Reactivate subscription after successful payment.
        if invoice.subscription_id and invoice.subscription:
            invoice.subscription.status = "active"

    # =========================================================
    # FAILED
    # =========================================================
    elif event == "failed":

        payment = Payment(
            invoice_id=invoice.id,
            user_id=invoice.user_id,
            amount=amount,
            payment_method=payment_method,
            status="failed",
            transaction_id=transaction_id,
        )

        db.add(payment)

        # Failed payment does NOT cancel the invoice.
        # It remains available for another payment attempt.
        invoice.payment_status = "unpaid"

    # =========================================================
    # REFUNDED
    # =========================================================
    elif event == "refunded":

        refund_line_item = InvoiceLineItem(
            invoice_id=invoice.id,
            description=f"Refund for transaction {transaction_id}",
            line_type="refund",
            quantity=1,
            unit_price=-amount,
            amount=-amount,
        )

        db.add(refund_line_item)

        invoice.payment_status = "unpaid"

    # ---------------------------------------------------------
    # Save changes
    # ---------------------------------------------------------
    db.commit()
    db.refresh(invoice)

    return {
        "message": f"Payment event '{event}' processed.",
        "event": event,
        "invoice_id": invoice.id,
        "invoice_status": invoice.status,
        "payment_status": invoice.payment_status,
        "transaction_id": transaction_id,
    }


# =============================================================
# MOCK CUSTOMER PAYMENT
# =============================================================

@router.post(
    "/mock",
    summary="Process mock customer payment",
)
def process_mock_payment(
    request: MockPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Process a customer payment through the mock gateway.

    The customer does not directly select success/failure.

    The mock gateway determines whether the payment succeeds
    or is declined based on the supplied payment details.
    """

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == request.invoice_id,
            Invoice.user_id == current_user.id,
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    # ---------------------------------------------------------
    # Invoice must be payable
    # ---------------------------------------------------------
    if invoice.status not in {"pending", "overdue"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invoice cannot be paid. "
                f"Current status is '{invoice.status}'."
            ),
        )

    # ---------------------------------------------------------
    # Prevent paying an already-paid invoice
    # ---------------------------------------------------------
    if invoice.payment_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice has already been paid.",
        )

    # ---------------------------------------------------------
    # Process through mock gateway
    # ---------------------------------------------------------
    result = payment_gateway.process_payment(
        amount=invoice.total_amount,
        payment_method=request.payment_method,
        payment_identifier=request.payment_identifier,
    )

    # ---------------------------------------------------------
    # Convert gateway result into internal payment event
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # Simulate gateway → webhook flow
    # ---------------------------------------------------------

    webhook_request = PaymentWebhookRequest(
               invoice_id=invoice.id,
               event="paid" if result.success else "failed",
               amount=result.amount,
               payment_method=result.payment_method,
               transaction_id=result.transaction_id,
    )

    outcome = _apply_payment_event(
             db=db,
             invoice=invoice,
             event=webhook_request.event,
             amount=webhook_request.amount,
             payment_method=webhook_request.payment_method,
             transaction_id=webhook_request.transaction_id,
    )
    return {
        "message": result.message,
        "success": result.success,
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "amount": result.amount,
        "payment_method": result.payment_method,
        "transaction_id": result.transaction_id,
        "invoice_status": outcome["invoice_status"],
        "payment_status": outcome["payment_status"],
    }


# =============================================================
# PAYMENT WEBHOOK
# =============================================================

@router.post(
    "/webhook",
    summary="Handle payment gateway webhook",
)
def payment_webhook(
    request: PaymentWebhookRequest,
    db: Session = Depends(get_db),
):
    """
    Handle payment events sent by a payment gateway.

    Supported:
        paid
        failed
        refunded
    """

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == request.invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    return _apply_payment_event(
        db=db,
        invoice=invoice,
        event=request.event,
        amount=request.amount,
        payment_method=request.payment_method,
        transaction_id=request.transaction_id,
    )