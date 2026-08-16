# app/repositories/customer_repository.py

from sqlalchemy.orm import Session
from app.models.user import User


# NOTE: registered customers are stored with role == "user"
# (see app/services/auth_service.py -> register_user). "customer"
# is not a role value ever assigned anywhere in the app.

def get_all_customers(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
):
    query = db.query(User).filter(User.role == "user")

    if search:
        like = f"%{search}%"
        query = query.filter(
            (User.username.ilike(like)) | (User.email.ilike(like))
        )

    total = query.count()

    items = (
        query
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total


def get_customer_by_id(db: Session, customer_id: int):
    return (
        db.query(User)
        .filter(
            User.id == customer_id,
            User.role == "user"
        )
        .first()
    )


def get_customer_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_customer_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_customer(db: Session, customer: User):
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: User):
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: User):
    db.delete(customer)
    db.commit()
