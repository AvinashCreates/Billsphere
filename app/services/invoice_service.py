import json
from math import ceil
from typing import Optional
from datetime import datetime, UTC

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.user import User

from app.schemas.invoice import (
    InvoiceListItem,
    InvoiceDetail,
    InvoiceLineItemResponse,
    CustomerInfo,
    SubscriptionInfo,
    PaginatedInvoiceResponse,
)
from app.schemas.payment import PaymentResponse, PayInvoiceResponse

from app.repositories.invoice_repository import (
    get_invoices_paginated,
    get_invoice_by_id,
    update_invoice,
)
from app.repositories.payment_repository import create_payment
from app.repositories.audit_log_repository import create_audit_log


# ---------------------------------------------------------------------------
# Invoice statuses that are valid for payment
# ---------------------------------------------------------------------------
PAYABLE_STATUSES = {"pending", "overdue"}


# ---------------------------------------------------------------------------
# Subscription statuses that should be re-activated after payment
# ---------------------------------------------------------------------------
REACTIVATABLE_SUB_STATUSES = {"suspended", "past_due", "pending_payment", "blocked"}


# ---------------------------------------------------------------------------
# Service: Get paginated invoice list
# ---------------------------------------------------------------------------

def get_invoices(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    user_id: Optional[int] = None,
    subscription_id: Optional[int] = None,
    billing_date_from: Optional[datetime] = None,
    billing_date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> PaginatedInvoiceResponse:
    """
    Retrieve a paginated, filtered, and sorted list of invoices.
    Embeds flat customer info for efficient list rendering.
    """
    items, total = get_invoices_paginated(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        payment_status=payment_status,
        user_id=user_id,
        subscription_id=subscription_id,
        billing_date_from=billing_date_from,
        billing_date_to=billing_date_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    invoice_items = []
    for inv in items:
        item = InvoiceListItem(
            id=inv.id,
            invoice_number=inv.invoice_number,
            user_id=inv.user_id,
            subscription_id=inv.subscription_id,
            billing_period_start=inv.billing_period_start,
            billing_period_end=inv.billing_period_end,
            due_date=inv.due_date,
            total_amount=inv.total_amount,
            status=inv.status,
            payment_status=inv.payment_status,
            created_at=inv.created_at,
            customer_username=inv.user.username if inv.user else None,
            customer_email=inv.user.email if inv.user else None,
        )
        invoice_items.append(item)

    total_pages = ceil(total / page_size) if page_size > 0 else 0

    return PaginatedInvoiceResponse(
        items=invoice_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ---------------------------------------------------------------------------
# Service: Get full invoice detail
# ---------------------------------------------------------------------------

def get_invoice_detail(db: Session, invoice_id: int) -> InvoiceDetail:
    """
    Retrieve complete invoice details including customer info,
    subscription info, and all line items.
    Raises HTTP 404 if the invoice does not exist.
    """
    invoice = get_invoice_by_id(db, invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found.",
        )

    # Build embedded customer info
    customer_info = None
    if invoice.user:
        customer_info = CustomerInfo(
            id=invoice.user.id,
            username=invoice.user.username,
            email=invoice.user.email,
        )

    # Build embedded subscription info
    subscription_info = None
    if invoice.subscription:
        subscription_info = SubscriptionInfo(
            id=invoice.subscription.id,
            plan_id=invoice.subscription.plan_id,
            status=invoice.subscription.status,
            subscribed_at=invoice.subscription.subscribed_at,
        )

    # Build line item responses
    line_items = [
        InvoiceLineItemResponse(
            id=li.id,
            description=li.description,
            line_type=li.line_type,
            quantity=li.quantity,
            unit_price=li.unit_price,
            amount=li.amount,
        )
        for li in invoice.line_items
    ]

    return InvoiceDetail(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        billing_period_start=invoice.billing_period_start,
        billing_period_end=invoice.billing_period_end,
        due_date=invoice.due_date,
        plan_fee=invoice.plan_fee,
        proration_amount=invoice.proration_amount,
        tax_amount=invoice.tax_amount,
        usage_charges=invoice.usage_charges,
        total_amount=invoice.total_amount,
        status=invoice.status,
        payment_status=invoice.payment_status,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        customer=customer_info,
        subscription=subscription_info,
        line_items=line_items,
    )


# ---------------------------------------------------------------------------
# Service: Pay an invoice
# ---------------------------------------------------------------------------

def pay_invoice(
    db: Session,
    invoice_id: int,
    admin_user: User,
) -> PayInvoiceResponse:
    """
    Process payment for a given invoice.

    Steps:
      1. Fetch and validate the invoice (must be pending or overdue).
      2. Create a Payment record.
      3. Update invoice status → paid, payment_status → paid.
      4. If the related subscription is suspended/blocked, re-activate it.
      5. Write an AuditLog entry.

    All DB writes are wrapped in a single transaction; any failure triggers
    a full rollback.
    """
    invoice = get_invoice_by_id(db, invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found.",
        )

    # --- Validate payable status ---
    if invoice.status not in PAYABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invoice cannot be paid. Current status is '{invoice.status}'. "
                f"Only invoices with status {sorted(PAYABLE_STATUSES)} can be paid."
            ),
        )

    if invoice.payment_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice has already been paid.",
        )

    try:
        # --- 1. Create Payment record ---
        payment = Payment(
            invoice_id=invoice.id,
            user_id=invoice.user_id,
            amount=invoice.total_amount,
            payment_method="manual",
            status="success",
        )
        db.add(payment)
        db.flush()  # Assign payment.id without committing yet

        # --- 2. Update Invoice ---
        invoice.status = "paid"
        invoice.payment_status = "paid"
        invoice.updated_at = datetime.now(UTC)

        # --- 3. Optionally re-activate subscription ---
        if (
            invoice.subscription_id
            and invoice.subscription
            and invoice.subscription.status in REACTIVATABLE_SUB_STATUSES
        ):
            invoice.subscription.status = "active"

        # --- 4. Write Audit Log ---
        audit_details = json.dumps({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "amount": invoice.total_amount,
            "paid_by_admin_id": admin_user.id,
            "paid_by_admin_email": admin_user.email,
            "payment_transaction_id": payment.transaction_id,
        })

        audit_log = AuditLog(
            user_id=admin_user.id,
            entity_type="invoice",
            entity_id=invoice.id,
            action="invoice_paid",
            details=audit_details,
        )
        db.add(audit_log)

        # --- 5. Commit everything atomically ---
        db.commit()
        db.refresh(invoice)
        db.refresh(payment)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(exc)}",
        ) from exc

    payment_response = PaymentResponse(
        id=payment.id,
        invoice_id=payment.invoice_id,
        user_id=payment.user_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_date=payment.payment_date,
        status=payment.status,
        transaction_id=payment.transaction_id,
        created_at=payment.created_at,
    )

    return PayInvoiceResponse(
        message="Invoice paid successfully.",
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number or f"INV-{invoice.id:06d}",
        invoice_status=invoice.status,
        payment_status=invoice.payment_status,
        payment=payment_response,
    )
