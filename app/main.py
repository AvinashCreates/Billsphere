from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.customer import router as customer_router

app = FastAPI(title="Billing Platform API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(customer_router)

@app.get("/")
def root():
    return {"message": "Billing Platform API is running"}