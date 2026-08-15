"""
BillSphere Usage Record Model

Stores metered usage charges associated with subscriptions.

Database table:
    usage_records

Columns:
    id
    subscription_id
    description
    quantity
    unit_price
    amount
    invoiced
    invoice_id
    recorded_at
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UsageRecord(Base):
    """
    Metered usage charge for a subscription.

    Usage records can remain unbilled until the billing engine
    includes them in an invoice.
    """

    __tablename__ = "usage_records"

    # ======================================================
    # Primary Key
    # ======================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ======================================================
    # Subscription
    # ======================================================

    subscription_id: Mapped[int] = mapped_column(
        ForeignKey(
            "subscriptions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # Usage Details
    # ======================================================

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # ======================================================
    # Invoice Information
    # ======================================================

    invoiced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "invoices.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ======================================================
    # Timestamp
    # ======================================================

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<UsageRecord "
            f"id={self.id} "
            f"subscription_id={self.subscription_id}>"
        )