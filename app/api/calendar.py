from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User

from app.services.calendar_service import get_billing_calendar_events

router = APIRouter(prefix="/admin/calendar", tags=["Admin Calendar"])


@router.get("/events")
def calendar_events(
    days_ahead: int = Query(default=60, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_billing_calendar_events(db, days_ahead=days_ahead)