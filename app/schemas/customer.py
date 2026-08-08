from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    customers: list[CustomerResponse]
    total_customers: int