from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    description: str
    price: float
    duration: int


class PlanUpdate(BaseModel):
    name: str
    description: str
    price: float
    duration: int
    status: str


class PlanResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    duration: int
    status: str

    class Config:
        from_attributes = True