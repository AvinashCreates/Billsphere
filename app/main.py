import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.customer import router as customer_router
from app.api.plans import router as plan_router
from app.api.subscriptions import router as subscription_router
from app.api.invoices import router as invoice_router
from app.api.payments import router as payment_router

from app.database.database import engine
from app.database.base import Base
from app.database.database import engine
from app.database.base import Base

# Import all models so SQLAlchemy registers them before create_all
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.invoice_line_item import InvoiceLineItem
from app.models.payment import Payment
from app.models.audit_log import AuditLog

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing Platform API")

os.makedirs("uploads/profile_pictures", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(customer_router)
app.include_router(plan_router)
app.include_router(subscription_router)
app.include_router(invoice_router)
app.include_router(payment_router)



@app.get("/")
def root():
    return {"message": "Billing Platform API is running"}
