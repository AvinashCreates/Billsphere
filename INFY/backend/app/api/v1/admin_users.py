"""Administrative user management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import database_session, get_current_user_token
from app.models.user import User
from app.schemas.users import UserListResponse, UserResponse, UserUpdate


router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


def require_admin(
    token: dict = Depends(get_current_user_token),
    db: Session = Depends(database_session),
) -> User:
    try:
        user_id = int(token.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active user account required")
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = 1,
    page_size: int = 50,
    _: User = Depends(require_admin),
    db: Session = Depends(database_session),
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    query = db.query(User).order_by(User.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(database_session),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    changes = user_data.model_dump(exclude_unset=True)
    if "role" in changes:
        role = (changes["role"] or "").lower().strip()
        if role not in {"admin", "customer"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be admin or customer")
        if user.id == admin.id and role != "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own admin role")
        changes["role"] = role

    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(database_session),
):
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()