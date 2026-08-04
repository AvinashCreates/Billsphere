from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.models.invoice import Invoice
from app.models.user import User
from app.models.subscription import Subscription


# ---------------------------------------------------------------------------
# Allowed sort columns — whitelist to prevent SQL injection
# ---------------------------------------------------------------------------
SORT_COLUMN_MAP = {
    "invoice_number": Invoice.invoice_number,
    "created_at": Invoice.created_at,
    "due_date": Invoice.due_date,
    "total_amount": Invoice.total_amount,
}

DEFAULT_SORT_COLUMN = Invoice.created_at
DEFAULT_SORT_ORDER = "desc"


def get_invoices_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    user_id: Optional[int] = None,
    subscription_id: Optional[int] = None,
    billing_date_from=None,
    billing_date_to=None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> Tuple[List[Invoice], int]:
    """
    Return a paginated, filtered, sorted list of invoices.
    Joins User so we can search/filter by customer attributes.

    Returns: (items, total_count)
    """
    query = (
        db.query(Invoice)
        .join(User, Invoice.user_id == User.id)
        .outerjoin(Subscription, Invoice.subscription_id == Subscription.id)
    )

    # --- Filters ---
    if status:
        query = query.filter(Invoice.status == status)

    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)

    if user_id:
        query = query.filter(Invoice.user_id == user_id)

    if subscription_id:
        query = query.filter(Invoice.subscription_id == subscription_id)

    if billing_date_from:
        query = query.filter(Invoice.billing_period_start >= billing_date_from)

    if billing_date_to:
        query = query.filter(Invoice.billing_period_end <= billing_date_to)

    # --- Free-text search (invoice number, customer email, username) ---
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Invoice.invoice_number.ilike(search_term),
                User.email.ilike(search_term),
                User.username.ilike(search_term),
            )
        )

    # --- Sorting ---
    sort_column = SORT_COLUMN_MAP.get(sort_by or "", DEFAULT_SORT_COLUMN)
    order_fn = desc if (sort_order or DEFAULT_SORT_ORDER).lower() == "desc" else asc
    query = query.order_by(order_fn(sort_column))

    # --- Pagination ---
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return items, total


def get_invoice_by_id(db: Session, invoice_id: int) -> Optional[Invoice]:
    """Fetch a single invoice by ID, eagerly loading line_items."""
    return (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )


def create_invoice(db: Session, invoice: Invoice) -> Invoice:
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_invoice(db: Session, invoice: Invoice) -> Invoice:
    db.commit()
    db.refresh(invoice)
    return invoice
