from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)

from datetime import datetime, UTC

from app.database.base import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    plan_id = Column(
        Integer,
        ForeignKey("plans.id"),
        nullable=False
    )

    status = Column(
        String,
        default="active"
    )

    subscribed_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    current_period_start = Column(
        DateTime,
        nullable=False
    )

    current_period_end = Column(
        DateTime,
        nullable=False
    )

    renewal_reminder_sent = Column(
        Boolean,
        default=False,
        nullable=False
    )