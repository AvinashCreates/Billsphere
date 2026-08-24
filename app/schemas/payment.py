from datetime import datetime
from typing import Literal
from pydantic import BaseModel , Field


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    user_id: int
    amount: float
    payment_method: str
    payment_date: datetime
    status: str
    transaction_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PayInvoiceResponse(BaseModel):
    message: str
    invoice_id: int
    invoice_number: str
    invoice_status: str
    payment_status: str
    payment: PaymentResponse

class MockPaymentRequest(BaseModel):
    invoice_id: int
    payment_method: str = Field(
        default="card",
        description="Payment method: card, upi, or bank_transfer",
    )
    payment_identifier: str | None = Field(
        default=None,
        description=(
            "Mock payment identifier. "
            "For UPI use a UPI ID; for card use a mock card number; "
            "for bank transfer use a bank reference."
        ),
    )

class PaymentWebhookRequest(BaseModel):
    event: Literal["paid", "failed", "refunded"]
    transaction_id: str
    invoice_id: int
    amount: float
    payment_method: str
