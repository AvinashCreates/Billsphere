from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.plan_service import remove_plan

from app.database.session import get_db

from app.dependencies.auth import (
    get_current_user,
    require_admin,
)

from app.models.user import User

from app.schemas.plan import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
)

from app.services.plan_service import (
    fetch_plans,
    fetch_plan,
    add_plan,
    edit_plan,
    remove_plan,
)

router = APIRouter(
    prefix="/plans",
    tags=["Plans"]
)

@router.get("/", response_model=list[PlanResponse])
def get_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return fetch_plans(
        db,
        current_user,
    )

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = fetch_plan(
    db,
    plan_id,
    current_user,
)

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    return plan


@router.post("/", response_model=PlanResponse)
def create_plan(
    plan: PlanCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return add_plan(db, plan)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan: PlanUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):

    updated = edit_plan(
        db,
        plan_id,
        plan
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    return updated

@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):

    deleted = remove_plan(
        db,
        plan_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Plan not found",
        )

    return {
        "message": "Plan deactivated successfully"
    }

