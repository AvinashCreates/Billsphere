from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api import plans, customers, auth, subscriptions, schedule, invoices, webhooks, payments, billing_cycles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Everything gets grouped under /api/v1
api_v1 = APIRouter(prefix="/api/v1")

api_v1.include_router(auth.router)
api_v1.include_router(plans.router)
api_v1.include_router(customers.router)
api_v1.include_router(subscriptions.router)
api_v1.include_router(schedule.router)
api_v1.include_router(invoices.router)
api_v1.include_router(webhooks.router)
api_v1.include_router(payments.router)
api_v1.include_router(billing_cycles.router)

app.include_router(api_v1)

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}