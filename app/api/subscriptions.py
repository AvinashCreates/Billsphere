from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin

from app.models.user import User

from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
)

from app.services.subscription_service import (
    subscribe,
    my_subscription,
    subscriptions,
)


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


# ==========================================================
# CUSTOMER - CREATE SUBSCRIPTION
# ==========================================================

@router.post(
    "/",
    response_model=SubscriptionResponse
)
def create_subscription(
    plan: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return subscribe(
            db,
            current_user.id,
            plan
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==========================================================
# CUSTOMER - GET MY SUBSCRIPTION
# ==========================================================

@router.get(
    "/my",
    response_model=SubscriptionResponse
)
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    subscription = my_subscription(
        db,
        current_user.id
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No subscription found."
        )

    return subscription


# ==========================================================
# ADMIN - GET ALL SUBSCRIPTIONS
# ==========================================================

@router.get(
    "/",
    response_model=list[SubscriptionResponse]
)
def get_all_subscriptions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):

    return subscriptions(db)