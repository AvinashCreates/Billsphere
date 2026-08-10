from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    plan_id: int

       
class SubscriptionUpdate(BaseModel):
    plan_id: int

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    subscribed_at: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None

    class Config:
        from_attributes = True