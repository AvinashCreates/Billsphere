from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationCreate(BaseModel):
    user_id: int
    type: str
    title: str
    message: str
    channel: str = "in_app"
    related_id: Optional[int] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    channel: str
    title: str
    message: str
    status: str
    is_read: bool
    related_id: Optional[int] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    unread_count: int


class TestNotificationRequest(BaseModel):
    user_id: int
    title: str = "Test Notification"
    message: str = "This is a test notification from the Notification System."