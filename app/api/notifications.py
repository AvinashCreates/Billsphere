from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.auth import (
    get_current_user,
    require_admin,
)

from app.models.user import User

from app.schemas.notification import (
    NotificationResponse,
    UnreadCountResponse,
    TestNotificationRequest,
)

from app.services.notification_service import (
    fetch_my_notifications,
    fetch_all_notifications,
    unread_count,
    mark_as_read,
    mark_all_as_read,
    send_test_notification,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/", response_model=list[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return fetch_my_notifications(db, current_user.id)


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"unread_count": unread_count(db, current_user.id)}


@router.get("/all", response_model=list[NotificationResponse])
def get_all_notifications(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return fetch_all_notifications(db)


@router.put("/read-all")
def read_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mark_all_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = mark_as_read(db, notification_id, current_user.id)

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return notification


@router.post("/test", response_model=NotificationResponse)
def send_test(
    payload: TestNotificationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: fires one notification through the full Celery/Redis pipeline, for testing."""
    return send_test_notification(
        db,
        payload.user_id,
        payload.title,
        payload.message,
    )