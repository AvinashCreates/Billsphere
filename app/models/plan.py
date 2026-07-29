from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, UTC

from app.database.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    description = Column(String, nullable=True)

    price = Column(Float, nullable=False)

    duration = Column(Integer, nullable=False)

    status = Column(String, default="active")

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )