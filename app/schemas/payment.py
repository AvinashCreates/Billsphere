from datetime import datetime
from pydantic import BaseModel


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
