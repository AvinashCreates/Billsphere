from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.database.base import Base


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Human-readable description e.g. "Pro Plan - Monthly Fee"
    description = Column(String, nullable=False)

    # Type: plan_fee | proration | tax | usage
    line_type = Column(String, nullable=False, default="plan_fee")

    quantity = Column(Float, default=1.0, nullable=False)
    unit_price = Column(Float, default=0.0, nullable=False)
    amount = Column(Float, default=0.0, nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationship back to invoice
    invoice = relationship("Invoice", back_populates="line_items")
