# app/repositories/customer_repository.py

from sqlalchemy.orm import Session
from app.models.user import User


def get_all_customers(db: Session):
    return (
        db.query(User)
        .filter(User.role == "customer")
        .order_by(User.created_at.desc())
        .all()
    )


def get_customer_by_id(db: Session, customer_id: int):
    return (
        db.query(User)
        .filter(
            User.id == customer_id,
            User.role == "customer"
        )
        .first()
    )