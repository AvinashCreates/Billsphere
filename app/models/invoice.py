"""
BillSphere Invoice Model

Database table:
invoices

Fields:
- id
- invoice_number
- customer_id
- subscription_id
- amount
- tax_amount
- total_amount
- status
- due_date
- paid_at
- created_at
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.invoice_line_item import InvoiceLineItem


class Invoice(Base):
    """
    Invoice database model.
    """

    __tablename__ = "invoices"

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # Invoice Information
    # ==========================================================

    invoice_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "subscriptions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ==========================================================
    # Amount Details
    # ==========================================================

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # ==========================================================
    # Status
    # ==========================================================

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    # ==========================================================
    # Payment Dates
    # ==========================================================

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==========================================================
    # Timestamp
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ==========================================================
    # Invoice Line Items
    # ==========================================================

    line_items: Mapped[list["InvoiceLineItem"]] = relationship(
        "InvoiceLineItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"<Invoice "
            f"id={self.id} "
            f"number={self.invoice_number}>"
        )