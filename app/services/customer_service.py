# app/services/customer_service.py

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.subscription import Subscription
from app.models.plan import Plan
from app.models.invoice import Invoice

from app.repositories.customer_repository import (
    get_all_customers as repo_get_all_customers,
    get_customer_by_id,
    get_customer_by_email,
    get_customer_by_username,
    create_customer as repo_create_customer,
    update_customer as repo_update_customer,
    delete_customer as repo_delete_customer,
)

from app.utils.security import hash_password


def _enrich_customers(db: Session, customers: list[User]) -> list[dict]:
    """
    Attach current plan / subscription status / invoice totals to a page
    of customers in a small, fixed number of queries (not one query per
    customer), then return plain dicts ready for CustomerResponse.
    """

    if not customers:
        return []

    user_ids = [c.id for c in customers]

    # ---- Latest/active subscription per user ----

    subs = (
        db.query(Subscription)
        .filter(Subscription.user_id.in_(user_ids))
        .order_by(Subscription.id.desc())
        .all()
    )

    # Prefer an active subscription; otherwise the most recent one.
    sub_by_user: dict[int, Subscription] = {}
    for sub in subs:
        existing = sub_by_user.get(sub.user_id)
        if existing is None:
            sub_by_user[sub.user_id] = sub
        elif existing.status != "active" and sub.status == "active":
            sub_by_user[sub.user_id] = sub

    plan_ids = {s.plan_id for s in sub_by_user.values()}
    plans_by_id = {}
    if plan_ids:
        plans_by_id = {
            p.id: p
            for p in db.query(Plan).filter(Plan.id.in_(plan_ids)).all()
        }

    # ---- Invoice totals per user ----

    invoice_stats = (
        db.query(
            Invoice.user_id,
            func.count(Invoice.id).label("total_invoices"),
            func.coalesce(func.sum(Invoice.total_amount), 0.0).label("total_spent"),
        )
        .filter(Invoice.user_id.in_(user_ids))
        .group_by(Invoice.user_id)
        .all()
    )
    stats_by_user = {row.user_id: row for row in invoice_stats}

    enriched = []
    for c in customers:
        sub = sub_by_user.get(c.id)
        plan = plans_by_id.get(sub.plan_id) if sub else None
        stats = stats_by_user.get(c.id)

        enriched.append({
            "id": c.id,
            "username": c.username,
            "email": c.email,
            "role": c.role,
            "created_at": c.created_at,
            "current_plan": plan.name if plan else None,
            "subscription_status": sub.status if sub else None,
            "total_invoices": stats.total_invoices if stats else 0,
            "total_spent": float(stats.total_spent) if stats else 0.0,
        })

    return enriched


def fetch_all_customers(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
):
    customers, total = repo_get_all_customers(db, page, page_size, search)
    return _enrich_customers(db, customers), total


def fetch_customer(db: Session, customer_id: int):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        return None

    enriched = _enrich_customers(db, [customer])
    return enriched[0]


def create_customer(db: Session, username: str, email: str, password: str):
    if get_customer_by_email(db, email):
        raise ValueError("Email already registered")

    if get_customer_by_username(db, username):
        raise ValueError("Username already exists")

    new_customer = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role="user",
    )

    created = repo_create_customer(db, new_customer)
    return _enrich_customers(db, [created])[0]


def update_customer(
    db: Session,
    customer_id: int,
    username: str | None,
    email: str | None,
    password: str | None,
):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        return None

    if email and email != customer.email:
        existing = get_customer_by_email(db, email)
        if existing and existing.id != customer_id:
            raise ValueError("Email already registered")
        customer.email = email

    if username and username != customer.username:
        existing = get_customer_by_username(db, username)
        if existing and existing.id != customer_id:
            raise ValueError("Username already exists")
        customer.username = username

    if password:
        customer.hashed_password = hash_password(password)

    updated = repo_update_customer(db, customer)
    return _enrich_customers(db, [updated])[0]


def delete_customer(db: Session, customer_id: int) -> bool:
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        return False

    invoice_count = (
        db.query(func.count(Invoice.id))
        .filter(Invoice.user_id == customer_id)
        .scalar()
    )

    if invoice_count and invoice_count > 0:
        raise ValueError(
            "Cannot delete a customer with existing invoices. "
            "This customer has billing history that must be preserved."
        )

    subscription_count = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.user_id == customer_id)
        .scalar()
    )

    if subscription_count and subscription_count > 0:
        raise ValueError(
            "Cannot delete a customer with an existing subscription "
            "(active, cancelled, or expired). Cancel and remove their "
            "subscription history first."
        )

    repo_delete_customer(db, customer)
    return True
