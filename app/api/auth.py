from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import UserRegister, UserLogin, UserResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        return login_user(
            db,
            form_data.username,   # username field will contain the email
            form_data.password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )