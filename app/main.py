from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import plans, customers, auth, subscriptions, schedule

app = FastAPI(title="Billing Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(customers.router)
app.include_router(subscriptions.router)
app.include_router(schedule.router)

@app.get("/")
def root():
    return {"message": "Billing Platform is running"}

@app.get("/health")
def health():
    return {"status": "ok"}