from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class InvoiceBase(BaseModel):
    customer_id: int
    amount: float
    status: str

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None
    paid_at: Optional[datetime] = None

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True