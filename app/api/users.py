from fastapi import APIRouter, Depends

from app.dependencies.auth import (get_current_user,require_admin,)
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
    }

@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(require_admin)
):
    return {
        "message": "Welcome Admin!",
        "user": current_user.username
    }