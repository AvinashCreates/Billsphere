"""
BillSphere Plan Model

SQLAlchemy database model for subscription plans.

Each plan belongs to a specific platform.

Example:

Amazon
    ├── Basic
    ├── Standard
    └── Premium

Netflix
    ├── Basic
    ├── Standard
    └── Premium
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Plan(Base):
    """
    Subscription plan database model.

    A platform can have multiple plans, but the same
    plan name cannot be duplicated within the same platform.

    Example:

        Amazon + Basic       -> allowed
        Amazon + Standard    -> allowed
        Amazon + Premium     -> allowed

        Netflix + Basic      -> allowed

        Amazon + Basic       -> duplicate, not allowed
    """

    __tablename__ = "plans"

    # ==========================================================
    # Table Constraints
    # ==========================================================

    __table_args__ = (
        UniqueConstraint(
            "platform",
            "name",
            name="uq_plans_platform_name",
        ),
    )

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # Platform
    # ==========================================================

    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Plan Information
    # ==========================================================

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==========================================================
    # Pricing
    # ==========================================================

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR",
    )

    # ==========================================================
    # Billing
    # ==========================================================

    billing_cycle: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="monthly",
    )

    trial_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # ==========================================================
    # Features
    # ==========================================================

    feature_entitlements: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )

    # ==========================================================
    # Usage Limits
    # ==========================================================

    max_customers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    max_invoices: Mapped[int | None] = mapped_column(
        Integer,
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
    # Ownership
    # ==========================================================

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ==========================================================
    # Timestamps
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"<Plan "
            f"id={self.id} "
            f"platform={self.platform} "
            f"name={self.name} "
            f"price={self.price} "
            f"currency={self.currency}>"
        )