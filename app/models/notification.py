
"""
BillSphere Notification Model

Database table:

notifications
--------------
id
user_id
customer_id
title
message
notification_type
is_sent
sent_at
is_read
read_at
created_at

Used for:

- Email notifications
- Payment reminders
- Invoice alerts
- System notifications
- Dashboard notifications
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notification(Base):
    """
    Notification database model.
    """

    __tablename__ = "notifications"

    # ==================================================
    # Primary Key
    # ==================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==================================================
    # References
    # ==================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "customers.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    # ==================================================
    # Notification Content
    # ==================================================

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    notification_type: Mapped[str] = mapped_column(
        String(50),
        default="system",
        nullable=False,
    )

    # ==================================================
    # Delivery Status
    # ==================================================

    is_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==================================================
    # Read Status
    # ==================================================

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==================================================
    # Timestamp
    # ==================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self) -> str:
        return (
            f"<Notification "
            f"id={self.id} "
            f"type={self.notification_type} "
            f"read={self.is_read}>"
        )
