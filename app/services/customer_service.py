# app/services/customer_service.py

from sqlalchemy.orm import Session

from app.repositories.customer_repository import (
    get_all_customers,
    get_customer_by_id
)


def fetch_all_customers(db: Session):
    return get_all_customers(db)


def fetch_customer(db: Session, customer_id: int):
    return get_customer_by_id(db, customer_id)