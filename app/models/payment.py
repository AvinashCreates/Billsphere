"""
BillSphere Payment Model

Database table:

payments
---------
id
invoice_id
amount
payment_method
transaction_id
status
payment_date
refunded_amount
refunded_at
refund_reason
created_at
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Payment(Base):
    """
    Payment database model.
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    payment_method: Mapped[str] = mapped_column(
        String(50), default="card", nullable=False
    )

    transaction_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )
    # pending | completed | failed | refunded

    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    refunded_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    refunded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    refund_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Payment id={self.id} status={self.status}>"