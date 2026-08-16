from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.database import Base

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String, nullable=False)  # e.g. "cancellation_unused_period", "admin_manual"

    created_at = Column(DateTime(timezone=True), server_default=func.now())