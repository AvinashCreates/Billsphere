from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, UTC

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # subscription | invoice | payment_success | payment_failure | renewal | expiry | general
    type = Column(String, nullable=False)

    # in_app | email
    channel = Column(String, default="in_app")

    title = Column(String, nullable=False)

    message = Column(Text, nullable=False)

    # pending | sent | failed
    status = Column(String, default="pending")

    is_read = Column(Boolean, default=False)

    # optional pointer to the related record (subscription_id, invoice_id, payment_id, ...)
    related_id = Column(Integer, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    sent_at = Column(DateTime, nullable=True)

    read_at = Column(DateTime, nullable=True)