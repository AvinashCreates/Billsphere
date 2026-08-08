from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who performed the action (nullable for system-generated events)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # The type of entity this log is about e.g. "invoice", "subscription"
    entity_type = Column(String, nullable=False, index=True)

    # The ID of the affected entity
    entity_id = Column(Integer, nullable=False, index=True)

    # Action performed e.g. "invoice_paid", "subscription_reactivated"
    action = Column(String, nullable=False, index=True)

    # JSON-encoded details stored as text for broad compatibility
    details = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True
    )

    # Relationship back to user (optional)
    performed_by = relationship(
        "User",
        backref="audit_logs",
        foreign_keys=[user_id]
    )
