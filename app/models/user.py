from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, UTC

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False, index=True)

    hashed_password = Column(String, nullable=False)

    role = Column(String, default="customer")

    created_at = Column(DateTime,default=lambda: datetime.now(UTC))