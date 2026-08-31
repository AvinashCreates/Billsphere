from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User
from app.models.invoice import Invoice
from app.models.plan import Plan

from app.schemas.invoice import InvoiceDetail, PaginatedInvoiceResponse
from app.schemas.payment import PayInvoiceResponse
from app.services.pdf_service import generate_invoice_pdf

from app.services.invoice_service import (
    get_invoices,
    get_invoice_detail,
    pay_invoice,
)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)

# ---------------------------------------------------------------------------
# 1. CUSTOMER ROUTES (Must come before generic /{invoice_id} routes)
# ---------------------------------------------------------------------------

@router.get(
    "/my",
    response_model=PaginatedInvoiceResponse,
    summary="List my invoices",
    description="Customer-only. Retrieve a paginated list of the logged-in user's own invoices.",
)
def list_my_invoices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    payment_status: str | None = Query(default=None),
    sort_by: str | None = Query(default="created_at"),
    sort_order: str | None = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_invoices(
        db=db,
        page=page,
        page_size=page_size,
        status=status_filter,
        payment_status=payment_status,
        user_id=current_user.id,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/my/{invoice_id}",
    response_model=InvoiceDetail,
    summary="Get my invoice detail",
    description="Customer-only. Retrieve full detail of one of the logged-in user's own invoices.",
)
def get_my_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    detail = get_invoice_detail(db=db, invoice_id=invoice_id)

    if not detail.customer or detail.customer.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    return detail


# ---------------------------------------------------------------------------
# 2. ADMIN & GENERAL LIST ROUTES
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=PaginatedInvoiceResponse,
    summary="List all invoices",
    description="Admin-only. Retrieve a paginated list of all invoices.",
)
def list_invoices(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(default=None),
    payment_status: Optional[str] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    subscription_id: Optional[int] = Query(default=None),
    billing_date_from: Optional[datetime] = Query(default=None),
    billing_date_to: Optional[datetime] = Query(default=None),
    search: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default="created_at"),
    sort_order: Optional[str] = Query(default="desc"),
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
# 3. PARAMETRIC ROUTES (/{invoice_id})
# ---------------------------------------------------------------------------

@router.get(
    "/{invoice_id}",
    response_model=InvoiceDetail,
    summary="Get invoice detail",
    description="Admin-only. Retrieve complete details of a single invoice.",
)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_invoice_detail(db=db, invoice_id=invoice_id)


@router.get(
    "/{invoice_id}/download",
    summary="Download PDF Invoice",
    description="Download PDF document for an invoice. Accessible by invoice owner or admin.",
)
def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Invoice not found"
        )

    # Authorization Check
    is_owner = invoice.user_id == current_user.id
    is_admin = getattr(current_user, "role", None) == "admin"

    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this invoice"
        )

    # Fetch associated plan if subscription exists
    plan = None
    if getattr(invoice, "subscription", None):
        plan = db.query(Plan).filter(Plan.id == invoice.subscription.plan_id).first()

    # Generate PDF Bytes
    try:
        pdf_bytes = generate_invoice_pdf(invoice, current_user, plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"PDF generation failed: {str(e)}"
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
        },
    )


@router.post(
    "/{invoice_id}/pay",
    response_model=PayInvoiceResponse,
    summary="Pay an invoice",
    description="Admin-only. Process payment for a pending or overdue invoice.",
    status_code=200,
)
def process_invoice_payment(
    invoice_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return pay_invoice(db=db, invoice_id=invoice_id, admin_user=current_user)