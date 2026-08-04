from sqlalchemy import (
    Column, Integer, String, Float,
    DateTime, ForeignKey, event
)
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.database.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(
        String,
        unique=True,
        nullable=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Billing period
    billing_period_start = Column(DateTime, nullable=True)
    billing_period_end = Column(DateTime, nullable=True)

    # Due date
    due_date = Column(DateTime, nullable=True)

    # Line item totals (denormalized for fast reads)
    plan_fee = Column(Float, default=0.0, nullable=False)
    proration_amount = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    usage_charges = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)

    # Status: draft | pending | paid | overdue | cancelled
    status = Column(String, default="pending", nullable=False, index=True)

    # Payment status: unpaid | paid | partially_paid
    payment_status = Column(
        String,
        default="unpaid",
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    user = relationship("User", backref="invoices", lazy="joined")
    subscription = relationship(
        "Subscription",
        backref="invoices",
        lazy="joined"
    )
    line_items = relationship(
        "InvoiceLineItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="select"
    )
    payments = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="select"
    )


@event.listens_for(Invoice, "after_insert")
def generate_invoice_number(mapper, connection, target):
    """Auto-generate invoice number after insert using the DB-assigned ID."""
    connection.execute(
        Invoice.__table__.update()
        .where(Invoice.__table__.c.id == target.id)
        .values(invoice_number=f"INV-{target.id:06d}")
    )
