"""
BillSphere Audit Log Model

Database model for tracking system activities.

Handles:
- User actions
- Security events
- Billing changes
- Administrative activities
"""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base



class AuditLog(Base):
    """
    Audit log database table.
    """

    __tablename__ = "audit_logs"



    # ==================================================
    # Primary Key
    # ==================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )



    # ==================================================
    # User Relationship
    # ==================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )



    # ==================================================
    # Action Information
    # ==================================================

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    module: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )



    # ==================================================
    # Request Tracking
    # ==================================================

    ip_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )



    # ==================================================
    # Entity Reference
    # ==================================================

    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


    entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )



    # ==================================================
    # Timestamp
    # ==================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )



    def __repr__(self) -> str:

        return (
            f"<AuditLog "
            f"id={self.id} "
            f"action={self.action}>"
        )