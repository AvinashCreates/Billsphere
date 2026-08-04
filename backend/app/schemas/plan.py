from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlanCreate(BaseModel):
    name: str
    price: float
    billing_interval: str
    trial_period_days: int = 0

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    billing_interval: Optional[str] = None
    trial_period_days: Optional[int] = None

class PlanStatusUpdate(BaseModel):
    status: str  # "active" or "inactive"

class PlanResponse(BaseModel):
    id: int
    name: str
    price: float
    billing_interval: str
    trial_period_days: int
    status: str
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True