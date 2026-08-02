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

    class Config:
        from_attributes = True