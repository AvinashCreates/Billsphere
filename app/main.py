from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.customer import router as customer_router
from app.api.plans import router as plan_router
from app.database.database import engine
from app.database.base import Base

# Import models
from app.models.user import User
from app.models.plan import Plan

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing Platform API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(customer_router)
app.include_router(plan_router)

@app.get("/")
def root():
    return {"message": "Billing Platform API is runninng"}