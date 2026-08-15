"""
BillSphere Subscription History Model

Stores an immutable record of subscription lifecycle events.

Tracks:
- Subscription
- User who performed the action
- Previous status
- New status
- Lifecycle action
- Reason
- Timestamp
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class SubscriptionHistory(Base):
    """
    Persistent subscription lifecycle history.

    Every important subscription lifecycle operation can
    create one history record.
    """

    __tablename__ = "subscription_history"

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # Subscription Relationship
    # ==========================================================

    subscription_id: Mapped[int] = mapped_column(
        ForeignKey(
            "subscriptions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # User Relationship
    # ==========================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ==========================================================
    # Lifecycle Status
    # ==========================================================

    previous_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # ==========================================================
    # Lifecycle Action
    # ==========================================================

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Reason
    # ==========================================================

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==========================================================
    # Timestamp
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        """
        Return a readable history representation.
        """

        return (
            f"<SubscriptionHistory "
            f"id={self.id} "
            f"subscription_id={self.subscription_id} "
            f"action={self.action} "
            f"{self.previous_status}"
            f"->{self.new_status}>"
        )