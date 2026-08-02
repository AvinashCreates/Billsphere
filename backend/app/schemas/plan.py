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

class PlanResponse(BaseModel):
    id: int
    name: str
    price: float
    billing_interval: str
    trial_period_days: int
    created_at: datetime

    class Config:
        from_attributes = True