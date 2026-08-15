"""
BillSphere Payment Service

Payment processing, invoice state changes, subscription lifecycle
integration, failed-payment dunning and refunds.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logging import app_logger
from app.models.audit_log import AuditLog
from app.models.invoice import Invoice
from app.models.invoice_line_item import InvoiceLineItem
from app.models.payment import Payment
from app.models.payment_retry import PaymentRetry
from app.models.subscription import Subscription
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.subscription_state_machine import (
    SubscriptionLifecycleException,
    activate_subscription,
    mark_past_due,
)


# ==========================================================
# Constants
# ==========================================================

# Failed-payment retry schedule.
#
# Example:
# Payment fails on Aug 15
#   Day 1 -> Aug 16
#   Day 3 -> Aug 18
#   Day 7 -> Aug 22
#
RETRY_SCHEDULE_DAYS = (1, 3, 7)


# ==========================================================
# Audit Helper
# ==========================================================


def _audit(
    db: Session,
    action: str,
    description: str,
    entity_id: int,
) -> None:
    """
    Create an audit log entry for payment-related actions.
    """

    db.add(
        AuditLog(
            user_id=None,
            action=action,
            module="payments",
            description=description,
            entity_id=entity_id,
            entity_type="payment",
        )
    )


# ==========================================================
# Payment Retrieval
# ==========================================================


def get_payment_by_id(
    db: Session,
    payment_id: int,
) -> Payment | None:
    """
    Return a payment by ID.
    """

    return (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )


# ==========================================================
# Create Payment
# ==========================================================


def create_payment(
    db: Session,
    payment_data: PaymentCreate,
) -> Payment:
    """
    Create a new payment record.
    """

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == payment_data.invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found.",
        )

    amount = Decimal(str(payment_data.amount))

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than zero.",
        )

    if amount > Decimal(str(invoice.total_amount)):
        raise HTTPException(
            status_code=400,
            detail="Payment amount cannot exceed invoice total.",
        )

    payment = Payment(
        invoice_id=payment_data.invoice_id,
        amount=amount,
        payment_method=payment_data.payment_method,
        transaction_id=payment_data.transaction_id,
        status=payment_data.status,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


# ==========================================================
# List Payments
# ==========================================================


def list_payments(
    db: Session,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """
    Return paginated payments.
    """

    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values.",
        )

    query = db.query(Payment)

    total = query.count()

    items = (
        query.order_by(Payment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ==========================================================
# Update Payment
# ==========================================================


def update_payment(
    db: Session,
    payment_id: int,
    payment_data: PaymentUpdate,
) -> Payment:
    """
    Update payment details.

    NOTE:
    This is a generic update endpoint.

    The dedicated /success and /failed endpoints should be
    used for payment lifecycle transitions because those
    endpoints also update invoices, subscriptions, retries,
    timestamps, etc.
    """

    payment = get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    for key, value in payment_data.model_dump(
        exclude_unset=True
    ).items():
        setattr(payment, key, value)

    db.commit()
    db.refresh(payment)

    return payment


# ==========================================================
# Clear Open Retry Records
# ==========================================================


def _clear_open_retries(
    db: Session,
    payment_id: int,
) -> None:
    """
    Cancel scheduled retries for a payment after successful
    payment completion.

    This prevents unnecessary future retry attempts after
    the invoice has already been paid.
    """

    db.query(PaymentRetry).filter(
        PaymentRetry.payment_id == payment_id,
        PaymentRetry.status == "scheduled",
    ).update(
        {
            "status": "cancelled",
        },
        synchronize_session=False,
    )


# ==========================================================
# Schedule Payment Retries
# ==========================================================


def _schedule_payment_retries(
    db: Session,
    payment_id: int,
    failure_time: datetime,
) -> list[PaymentRetry]:
    """
    Create the BillSphere failed-payment retry schedule.

    Retry schedule:

        Day 1
        Day 3
        Day 7

    Each retry is stored as a PaymentRetry row with:

        payment_id
        retry_count
        retry_date
        status = scheduled

    The function is idempotent. If a retry for a particular
    schedule day already exists for this payment, it will not
    create another duplicate record.
    """

    retries: list[PaymentRetry] = []

    for retry_day in RETRY_SCHEDULE_DAYS:

        # Prevent duplicate retry records if the failed
        # endpoint is called more than once for the same
        # payment.
        existing_retry = (
            db.query(PaymentRetry)
            .filter(
                PaymentRetry.payment_id == payment_id,
                PaymentRetry.retry_count == retry_day,
                PaymentRetry.status.in_(
                    [
                        "scheduled",
                        "pending",
                        "processing",
                    ]
                ),
            )
            .first()
        )

        if existing_retry:
            retries.append(existing_retry)
            continue

        retry = PaymentRetry(
            payment_id=payment_id,
            retry_count=retry_day,
            retry_date=failure_time
            + timedelta(days=retry_day),
            status="scheduled",
            error_message=None,
        )

        db.add(retry)
        retries.append(retry)

    return retries


# ==========================================================
# Mark Payment Successful
# ==========================================================


def mark_payment_success(
    db: Session,
    payment_id: int,
    transaction_id: str,
) -> Payment:
    """
    Mark a payment as successfully completed.

    Successful payment lifecycle:

        Payment
            -> completed
            -> payment_date set

        Invoice
            -> paid
            -> paid_at set

        Scheduled retries
            -> cancelled

        Subscription
            -> activated when appropriate
    """

    payment = get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    now = datetime.now(timezone.utc)

    payment.status = "completed"
    payment.transaction_id = transaction_id
    payment.payment_date = now

    # A successful payment means all future dunning attempts
    # for this payment are no longer necessary.
    _clear_open_retries(
        db,
        payment.id,
    )

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == payment.invoice_id)
        .first()
    )

    if invoice:

        invoice.status = "paid"
        invoice.paid_at = now

        # Activate the related subscription when a successful
        # payment is received for a trial or past_due subscription.
        if invoice.subscription_id:

            subscription = (
                db.query(Subscription)
                .filter(
                    Subscription.id == invoice.subscription_id
                )
                .first()
            )

            if subscription and subscription.status in {
                "trial",
                "past_due",
            }:
                try:
                    activate_subscription(
                        db=db,
                        subscription=subscription,
                        user_id=None,
                    )
                except SubscriptionLifecycleException:
                    # Preserve existing behavior:
                    # payment can still complete even if
                    # subscription activation cannot transition.
                    pass

    _audit(
        db,
        "payment_received",
        f"Payment {payment.id} completed successfully.",
        payment.id,
    )

    db.commit()
    db.refresh(payment)

    return payment


# ==========================================================
# Mark Payment Failed
# ==========================================================


def mark_payment_failed(
    db: Session,
    payment_id: int,
) -> Payment:
    """
    Mark a payment as failed and schedule dunning retries.

    Failure lifecycle:

        Payment
            -> failed

        Invoice
            -> pending

        Subscription
            -> past_due

        PaymentRetry
            -> Day 1 scheduled
            -> Day 3 scheduled
            -> Day 7 scheduled
    """

    payment = get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    failure_time = datetime.now(timezone.utc)

    payment.status = "failed"

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == payment.invoice_id)
        .first()
    )

    if invoice:

        # Keep the invoice unpaid because the payment failed.
        invoice.status = "pending"

        if invoice.subscription_id:

            subscription = (
                db.query(Subscription)
                .filter(
                    Subscription.id == invoice.subscription_id
                )
                .first()
            )

            if subscription and subscription.status == "active":
                try:
                    mark_past_due(
                        db=db,
                        subscription=subscription,
                        user_id=None,
                    )
                except SubscriptionLifecycleException:
                    # Preserve existing behavior.
                    pass

    # ------------------------------------------------------
    # Dunning / Failed Payment Recovery
    # ------------------------------------------------------
    #
    # This was previously missing.
    #
    # Create:
    #   Day 1
    #   Day 3
    #   Day 7
    #
    # retry records for this payment.
    #
    scheduled_retries = _schedule_payment_retries(
        db=db,
        payment_id=payment.id,
        failure_time=failure_time,
    )

    app_logger.info(
        "Payment %s failed. Scheduled %s retry attempts.",
        payment.id,
        len(scheduled_retries),
    )

    _audit(
        db,
        "payment_failed",
        (
            f"Payment {payment.id} failed; "
            f"{len(scheduled_retries)} retry attempts scheduled."
        ),
        payment.id,
    )

    db.commit()
    db.refresh(payment)

    return payment


# ==========================================================
# Refund Payment
# ==========================================================


def refund_payment(
    db: Session,
    payment_id: int,
    amount: Decimal | None = None,
    reason: str | None = None,
) -> Payment:
    """
    Refund a completed payment fully or partially.
    """

    payment = get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    if payment.status not in {
        "completed",
        "refunded",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only completed payments can be refunded. "
                f"Current status: '{payment.status}'."
            ),
        )

    already_refunded = Decimal(
        str(payment.refunded_amount or 0)
    )

    remaining = (
        Decimal(str(payment.amount))
        - already_refunded
    )

    refund_amount = (
        Decimal(str(amount))
        if amount is not None
        else remaining
    )

    if refund_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Refund amount must be greater than zero.",
        )

    if refund_amount > remaining:
        raise HTTPException(
            status_code=400,
            detail=(
                "Refund amount exceeds the remaining "
                "refundable amount."
            ),
        )

    payment.refunded_amount = (
        already_refunded + refund_amount
    )

    payment.refunded_at = datetime.now(timezone.utc)

    payment.refund_reason = reason

    payment.status = (
        "refunded"
        if payment.refunded_amount >= payment.amount
        else "partially_refunded"
    )

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == payment.invoice_id)
        .first()
    )

    if invoice:

        invoice.status = (
            "void"
            if payment.status == "refunded"
            else invoice.status
        )

        db.add(
            InvoiceLineItem(
                invoice_id=invoice.id,
                description=(
                    f"Refund: "
                    f"{reason or 'Payment refund'}"
                ),
                item_type="refund",
                amount=-refund_amount,
            )
        )

    _audit(
        db,
        "refund_issued",
        (
            f"Refund of {refund_amount:.2f} "
            f"issued for payment {payment.id}."
        ),
        payment.id,
    )

    db.commit()
    db.refresh(payment)

    return payment