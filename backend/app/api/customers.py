import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.customer import Customer
from app.models.user import User
from app.models.subscription import Subscription
from app.models.plan import Plan
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.core.dependencies import require_role
from app.core.security import hash_password, create_invite_token
from app.workers.email_tasks import send_customer_invite_email

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")

    new_customer = Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # If nobody with this email has a login yet, create one and email a
    # set-password link — if they've already registered, leave it alone.
    existing_user = db.query(User).filter(User.email == customer.email).first()
    if not existing_user:
        placeholder_hash = hash_password(secrets.token_urlsafe(24))  # unusable until they set a real one
        new_user = User(email=customer.email, hashed_password=placeholder_hash, role="customer")
        db.add(new_user)
        db.commit()

        invite_token = create_invite_token(customer.email)
        send_customer_invite_email.delay(customer.email, customer.name, invite_token)

    return new_customer


@router.get("/", response_model=list[CustomerResponse])
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return db.query(Customer).all()


@router.get("/admin")
def list_customers_admin(
    payment_status: Optional[str] = Query(None, description="paid | unpaid | trial | cancelled"),
    platform: Optional[str] = Query(None, description="Plan name, e.g. Netflix"),
    plan_type: Optional[str] = Query(None, description="monthly | yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Each customer joined to their most recent subscription + plan, with filters."""
    latest_sub_ids = (
        db.query(Subscription.customer_id, func.max(Subscription.id).label("max_id"))
        .group_by(Subscription.customer_id)
        .subquery()
    )

    rows = (
        db.query(Customer, Subscription, Plan)
        .outerjoin(latest_sub_ids, latest_sub_ids.c.customer_id == Customer.id)
        .outerjoin(Subscription, Subscription.id == latest_sub_ids.c.max_id)
        .outerjoin(Plan, Plan.id == Subscription.plan_id)
        .all()
    )

    status_map = {"paid": "active", "unpaid": "past_due", "trial": "trial", "cancelled": "cancelled"}
    result = []

    for customer, sub, plan in rows:
        if payment_status:
            wanted = status_map.get(payment_status)
            if not sub or sub.status != wanted:
                continue
        if platform and (not plan or plan.name != platform):
            continue
        if plan_type and (not plan or plan.billing_interval != plan_type):
            continue

        result.append({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "billing_country": customer.billing_country,
            "created_at": customer.created_at,
            "platform": plan.name if plan else None,
            "plan_type": plan.billing_interval if plan else None,
            "payment_status": sub.status if sub else "no_subscription",
            "current_period_end": sub.current_period_end if sub else None,
            "trial_ends_at": sub.trial_ends_at if sub else None,
        })

    return result


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Removes the customer roster entry only — their login account (if any) stays intact."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return {"detail": "Customer deleted"}