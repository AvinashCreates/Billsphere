import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.database.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    amount = Column(Float, nullable=False)

    # Payment method: manual | card | bank_transfer | etc.
    payment_method = Column(String, default="manual", nullable=False)

    payment_date = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # Status: success | failed
    status = Column(String, default="success", nullable=False)

    # Unique transaction reference
    transaction_id = Column(
        String,
        unique=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    user = relationship("User", backref="payments")
