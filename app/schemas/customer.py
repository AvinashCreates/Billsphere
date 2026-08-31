from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    # Enriched fields (populated by the service layer, not the ORM directly)
    current_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    total_invoices: int = 0
    total_spent: float = 0.0
    profile_picture: str | None = None
    model_config = ConfigDict(from_attributes=True)
    


class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total_customers: int
    page: int
    page_size: int
    total_pages: int


class CustomerCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class CustomerUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
