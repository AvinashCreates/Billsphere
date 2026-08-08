from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User

from app.schemas.invoice import InvoiceDetail, PaginatedInvoiceResponse
from app.schemas.payment import PayInvoiceResponse

from app.services.invoice_service import (
    get_invoices,
    get_invoice_detail,
    pay_invoice,
)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices (Admin)"],
)


# ---------------------------------------------------------------------------
# GET /invoices
# Retrieve all invoices with pagination, filtering, sorting, and search.
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=PaginatedInvoiceResponse,
    summary="List all invoices",
    description=(
        "Admin-only. Retrieve a paginated list of all invoices. "
        "Supports filtering by status, payment status, customer, subscription, "
        "billing date range, and free-text search. "
        "Sortable by invoice_number, created_at, due_date, or total_amount."
    ),
)
def list_invoices(
    # Pagination
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Number of items per page"
    ),
    # Filters
    status: Optional[str] = Query(
        default=None,
        description="Filter by invoice status: draft | pending | paid | overdue | cancelled",
    ),
    payment_status: Optional[str] = Query(
        default=None,
        description="Filter by payment status: unpaid | paid | partially_paid",
    ),
    user_id: Optional[int] = Query(
        default=None, description="Filter by customer user ID"
    ),
    subscription_id: Optional[int] = Query(
        default=None, description="Filter by subscription ID"
    ),
    billing_date_from: Optional[datetime] = Query(
        default=None,
        description="Filter invoices with billing_period_start >= this datetime (ISO 8601)",
    ),
    billing_date_to: Optional[datetime] = Query(
        default=None,
        description="Filter invoices with billing_period_end <= this datetime (ISO 8601)",
    ),
    # Search
    search: Optional[str] = Query(
        default=None,
        description="Free-text search on invoice number, customer email, or username",
    ),
    # Sorting
    sort_by: Optional[str] = Query(
        default="created_at",
        description="Sort field: invoice_number | created_at | due_date | total_amount",
    ),
    sort_order: Optional[str] = Query(
        default="desc",
        description="Sort direction: asc | desc",
    ),
    # Auth
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_invoices(
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


# ---------------------------------------------------------------------------
# GET /invoices/{invoice_id}
# Retrieve full invoice detail.
# ---------------------------------------------------------------------------

@router.get(
    "/{invoice_id}",
    response_model=InvoiceDetail,
    summary="Get invoice detail",
    description=(
        "Admin-only. Retrieve complete details of a single invoice including "
        "customer info, subscription info, billing period, all line items "
        "(plan fee, proration, taxes, usage charges), totals, due date, "
        "payment status, and creation date."
    ),
)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_invoice_detail(db=db, invoice_id=invoice_id)


# ---------------------------------------------------------------------------
# POST /invoices/{invoice_id}/pay
# Process payment for an invoice.
# ---------------------------------------------------------------------------

@router.post(
    "/{invoice_id}/pay",
    response_model=PayInvoiceResponse,
    summary="Pay an invoice",
    description=(
        "Admin-only. Process payment for a pending or overdue invoice. "
        "Validates invoice status, marks the invoice as Paid, creates a "
        "payment record, optionally re-activates the associated subscription, "
        "and records the event in the audit log."
    ),
    status_code=200,
)
def process_invoice_payment(
    invoice_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return pay_invoice(db=db, invoice_id=invoice_id, admin_user=current_user)
