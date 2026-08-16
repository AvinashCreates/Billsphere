from pydantic import BaseModel, Field


class PlanCreate(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    duration: int = Field(gt=0)


class PlanUpdate(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    duration: int = Field(gt=0)
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