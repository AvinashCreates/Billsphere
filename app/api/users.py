import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserMeResponse, UsernameUpdateRequest

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

UPLOAD_DIR = os.path.join("uploads", "profile_pictures")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "profile_picture": user.profile_picture,
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return _serialize_user(current_user)


@router.put("/me")
def update_me(
    payload: UsernameUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_username = payload.username.strip()

    if len(new_username) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be at least 3 characters.",
        )

    current_user.username = new_username
    db.commit()
    db.refresh(current_user)

    return _serialize_user(current_user)


@router.post("/me/profile-picture")
def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, ext = os.path.splitext(file.filename or "")
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    contents = file.file.read()

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File too large. Maximum size is 5MB.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"user_{current_user.id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    current_user.profile_picture = f"/uploads/profile_pictures/{filename}"
    db.commit()
    db.refresh(current_user)

    return _serialize_user(current_user)


@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(require_admin)
):
    return {
        "message": "Welcome Admin!",
        "user": current_user.username
    }