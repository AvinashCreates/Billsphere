from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin

from app.models.user import User

from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
)

from app.services.subscription_service import (
    subscribe,
    my_subscription,
    subscriptions,
    block_subscription,
    unblock_subscription,
    get_subscription,
    edit_subscription,
    cancel_subscription,
    renew_subscription,
    expire_subscription,

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

@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)

def get_subscription_by_id(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = get_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    # Customer can only see their own subscription
    if (
        current_user.role != "admin"
        and subscription.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view this subscription."
        )

    return subscription

# ==========================================================
# UPDATE SUBSCRIPTION
# ==========================================================

@router.put(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)
def update_subscription_api(
    subscription_id: int,
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = get_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    # Customer can update only their own subscription
    if (
        current_user.role != "admin"
        and subscription.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this subscription."
        )

    try:
        updated = edit_subscription(
            db,
            subscription_id,
            subscription_data.plan_id,
        )

        return updated

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
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

# ==========================================================
# ADMIN - BLOCK SUBSCRIPTION
# ==========================================================

@router.patch(
    "/{subscription_id}/block",
    response_model=SubscriptionResponse
)
def block_subscription_api(
    subscription_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    subscription = block_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    return subscription


# ==========================================================
# ADMIN - UNBLOCK SUBSCRIPTION
# ==========================================================

@router.patch(
    "/{subscription_id}/unblock",
    response_model=SubscriptionResponse
)
def unblock_subscription_api(
    subscription_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    subscription = unblock_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    return subscription

# ==========================================================
# CANCEL SUBSCRIPTION
# ==========================================================

@router.post(
    "/{subscription_id}/cancel",
    response_model=SubscriptionResponse
)
def cancel_subscription_api(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = get_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    # Customer can cancel only their own subscription
    if (
        current_user.role != "admin"
        and subscription.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to cancel this subscription."
        )

    try:
        return cancel_subscription(
            db,
            subscription_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# ==========================================================
# RENEW SUBSCRIPTION
# ==========================================================

@router.post(
    "/{subscription_id}/renew",
    response_model=SubscriptionResponse
)
def renew_subscription_api(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = get_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    # Customer can renew only their own subscription
    if (
        current_user.role != "admin"
        and subscription.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to renew this subscription."
        )

    try:
        return renew_subscription(
            db,
            subscription_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# ==========================================================
# EXPIRE SUBSCRIPTION
# ==========================================================

@router.post(
    "/{subscription_id}/expire",
    response_model=SubscriptionResponse
)
def expire_subscription_api(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = get_subscription(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    # Customer can expire only their own subscription
    if (
        current_user.role != "admin"
        and subscription.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to expire this subscription."
        )

    try:
        return expire_subscription(
            db,
            subscription_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) 