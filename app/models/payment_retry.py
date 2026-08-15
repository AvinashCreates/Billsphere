"""
BillSphere Payment Retry Model

Database table:

payment_retries
----------------
id
payment_id
retry_count
retry_date
status
error_message
created_at

Used for:
- Failed payment recovery
- Dunning workflow
- Retry scheduling
"""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PaymentRetry(Base):
    """
    Payment retry tracking model.
    """

    __tablename__ = "payment_retries"


    # ==================================================
    # Primary Key
    # ==================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )


    # ==================================================
    # Payment Reference
    # ==================================================

    payment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "payments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    # ==================================================
    # Retry Information
    # ==================================================

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    retry_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )


    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    # ==================================================
    # Timestamp
    # ==================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


    def __repr__(self) -> str:
        return (
            f"<PaymentRetry id={self.id} "
            f"status={self.status}>"
        )