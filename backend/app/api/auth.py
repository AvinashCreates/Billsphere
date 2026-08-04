from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.dependencies import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token, decode_invite_token
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, Token, SetPasswordRequest
from app.workers.email_tasks import send_welcome_email

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Trigger Celery welcome email task
    user_name = user.email.split("@")[0]
    try:
        send_welcome_email.delay(new_user.email, user_name)
    except Exception as e:
        print(f"Failed to queue welcome email task: {e}")

    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/set-password", response_model=Token)
def set_password(payload: SetPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = decode_invite_token(payload.token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired invite link")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid invite link")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()

    # Log them straight in after setting the password
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
