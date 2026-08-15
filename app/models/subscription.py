"""
BillSphere Subscription Model

Database model for customer subscriptions.

Handles:
- Customer and plan relationships
- Subscription dates
- Subscription status
- Billing cycle
- Pause / Resume metadata
- Billing period metadata
- Cancellation metadata
- Lifecycle metadata

Lifecycle:

trial
  |
active
 |   \
paused  past_due
 |        |
active     |
  \        |
   \       |
    cancelled
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class Subscription(Base):
    """
    Subscription database model.

    Existing subscription fields are preserved and extended
    with lifecycle and billing-period metadata.
    """

    __tablename__ = "subscriptions"

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey(
            "plans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Subscription Dates
    # ==========================================================

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==========================================================
    # Status
    # ==========================================================

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="trial",
        index=True,
    )

    # ==========================================================
    # Billing
    # ==========================================================

    billing_cycle: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="monthly",
    )

    # ==========================================================
    # Lifecycle Metadata
    # ==========================================================

    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==========================================================
    # Current Billing Period
    # ==========================================================

    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    next_billing_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # ==========================================================
    # Cancellation
    # ==========================================================

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==========================================================
    # Lifecycle Metadata
    # ==========================================================

    lifecycle_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        """
        Return a readable subscription representation.
        """

        return (
            f"<Subscription "
            f"id={self.id} "
            f"customer_id={self.customer_id} "
            f"plan_id={self.plan_id} "
            f"status={self.status} "
            f"billing_cycle={self.billing_cycle}>"
        )