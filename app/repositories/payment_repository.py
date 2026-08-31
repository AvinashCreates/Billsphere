from sqlalchemy.orm import Session

from app.models.payment import Payment


def create_payment(db: Session, payment: Payment) -> Payment:
    """Persist a new payment record and return it with DB-assigned fields."""
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
