from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    status: str
    gateway_reference: Optional[str]
    attempted_at: datetime

    class Config:
        from_attributes = True