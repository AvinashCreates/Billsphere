"""
BillSphere User Model

Matches PostgreSQL table:

users
-------
id
username
email
hashed_password
role
"""

from sqlalchemy import (
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)





from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    first_name = Column(
        String,
        nullable=False
    )

    last_name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String,
        nullable=True
    )

    hashed_password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="customer"
    )

    is_active = Column(
        Boolean,
        default=True
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    reset_token = Column(
        String,
        nullable=True
    )

    reset_token_expiry = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )