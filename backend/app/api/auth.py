from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.dependencies import get_db, get_current_user
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

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
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchanges a valid, unexpired refresh token for a brand new access token
    (and a fresh refresh token, extending the session) — without requiring
    the user to log in again with their password.
    """
    try:
        decoded = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token is not a refresh token")

    email = decoded.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generates a short-lived reset token for the given email. In production
    this would be emailed to the user (see the Notifications module) —
    for now it's returned directly in the response for local testing.
    """
    user = db.query(User).filter(User.email == payload.email).first()

    # Always return a generic success message, even if the email doesn't
    # exist — this prevents leaking which emails are registered.
    if not user:
        return {"detail": "If that email exists, a reset link has been sent."}

    reset_token = create_reset_token(data={"sub": user.email})

    # TODO: replace this with an actual email send once the Notifications
    # module is wired up (POST /notifications/... per the teammate's API).
    print(f"[MOCK EMAIL] Password reset link for {user.email}: reset_token={reset_token}")

    return {"detail": "If that email exists, a reset link has been sent.", "reset_token_debug": reset_token}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(payload.reset_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired reset token")

    if decoded.get("type") != "reset":
        raise HTTPException(status_code=401, detail="Token is not a password reset token")

    email = decoded.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()

    return {"detail": "Password has been reset successfully"}