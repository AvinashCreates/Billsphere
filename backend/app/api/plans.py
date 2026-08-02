from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.core.dependencies import require_role

router = APIRouter(prefix="/plans", tags=["Plans"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PlanResponse)
def create_plan(
    plan: PlanCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    new_plan = Plan(**plan.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


@router.get("/", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_update: PlanUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    update_data = plan_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # safety: don't silently orphan active subscriptions
    active_count = (
        db.query(Subscription)
        .filter(
            Subscription.plan_id == plan_id,
            Subscription.status.in_(["trial", "active", "past_due"]),
        )
        .count()
    )

    if active_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete plan: {active_count} customer(s) are still on it",
        )

    db.delete(plan)
    db.commit()
    return {"detail": "Plan deleted"}