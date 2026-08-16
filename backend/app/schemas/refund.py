from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RefundResponse(BaseModel):
    id: int
    payment_id: int
    invoice_id: int
    subscription_id: Optional[int]
    amount: float
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True