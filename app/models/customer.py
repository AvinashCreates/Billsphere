"""
BillSphere Customer Model

SQLAlchemy model for the customers table.

Database columns:
- id
- owner_id
- company_name
- contact_name
- email
- phone
- address
- city
- state
- country
- postal_code
- tax_id
- is_active
- created_at
- updated_at
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


class Customer(Base):
    """
    Customer database model.
    """

    __tablename__ = "customers"

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # Owner
    # ==========================================================

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Customer Information
    # ==========================================================

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    contact_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    tax_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ==========================================================
    # Status
    # ==========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ==========================================================
    # Timestamps
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"<Customer "
            f"id={self.id} "
            f"company={self.company_name} "
            f"owner_id={self.owner_id}>"
        )