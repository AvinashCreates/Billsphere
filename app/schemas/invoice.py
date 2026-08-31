from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Embedded sub-schemas
# ---------------------------------------------------------------------------

class CustomerInfo(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class SubscriptionInfo(BaseModel):
    id: int
    plan_id: int
    status: str
    subscribed_at: datetime

    model_config = {"from_attributes": True}


class InvoiceLineItemResponse(BaseModel):
    id: int
    description: str
    line_type: str
    quantity: float
    unit_price: float
    amount: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# List-level (summary) schema — used in GET /invoices
# ---------------------------------------------------------------------------

class InvoiceListItem(BaseModel):
    id: int
    invoice_number: Optional[str]
    user_id: int
    subscription_id: Optional[int]
    billing_period_start: Optional[datetime]
    billing_period_end: Optional[datetime]
    due_date: Optional[datetime]
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime

    # Flat customer info for list view
    customer_username: Optional[str] = None
    customer_email: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Detail schema — used in GET /invoices/{invoice_id}
# ---------------------------------------------------------------------------

class InvoiceDetail(BaseModel):
    id: int
    invoice_number: Optional[str]
    billing_period_start: Optional[datetime]
    billing_period_end: Optional[datetime]
    due_date: Optional[datetime]
    plan_fee: float
    proration_amount: float
    tax_amount: float
    usage_charges: float
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
    updated_at: datetime

    # Nested related objects
    customer: Optional[CustomerInfo]
    subscription: Optional[SubscriptionInfo]
    line_items: List[InvoiceLineItemResponse] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Paginated list wrapper — used in GET /invoices response
# ---------------------------------------------------------------------------

class PaginatedInvoiceResponse(BaseModel):
    items: List[InvoiceListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
