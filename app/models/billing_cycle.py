"""
BillSphere Billing Cycle Model

Database table:

billing_cycles
---------------
id
subscription_id
cycle_start
cycle_end
status
invoice_id
created_at

Records a historical entry every time a subscription's
billing period starts, renews, or closes. Complements the
live period fields kept directly on Subscription.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BillingCycle(Base):
    """
    Billing cycle history table.
    """

    __tablename__ = "billing_cycles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cycle_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    cycle_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )
    # active | renewed | invoiced | closed

    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<BillingCycle id={self.id} "
            f"subscription_id={self.subscription_id} "
            f"status={self.status}>"
        )