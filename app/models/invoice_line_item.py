"""
BillSphere Invoice Line Item Model

Database table:
invoice_line_items

Fields:
- id
- invoice_id
- description
- item_type
- amount
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
    from app.models.invoice import Invoice


class InvoiceLineItem(Base):
    """
    Individual line item belonging to an invoice.
    """

    __tablename__ = "invoice_line_items"

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # Invoice Foreign Key
    # ==========================================================

    invoice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "invoices.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Invoice Relationship
    # ==========================================================

    invoice: Mapped["Invoice"] = relationship(
        "Invoice",
        back_populates="line_items",
    )

    # ==========================================================
    # Line Item Details
    # ==========================================================

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    item_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="charge",
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
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
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"<InvoiceLineItem "
            f"id={self.id} "
            f"invoice_id={self.invoice_id} "
            f"type={self.item_type} "
            f"amount={self.amount}>"
        )