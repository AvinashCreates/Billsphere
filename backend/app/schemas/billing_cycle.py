from pydantic import BaseModel
from datetime import datetime

class BillingCycleResponse(BaseModel):
    id: int
    subscription_id: int
    cycle_start: datetime
    cycle_end: datetime
    status: str  # pending / invoiced

    class Config:
        from_attributes = True