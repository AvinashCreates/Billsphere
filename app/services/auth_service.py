from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserRegister
from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_username,
    create_user,
)
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token


def register_user(db: Session, user: UserRegister):
    if get_user_by_email(db, user.email):
        raise ValueError("Email already registered")

    if get_user_by_username(db, user.username):
        raise ValueError("Username already exists")

    hashed = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed,
        role="user"
    )

    return create_user(db, new_user)


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }