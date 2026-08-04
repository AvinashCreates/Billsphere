from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.plan import Plan
from app.models.audit_log import AuditLog
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate, PlanStatusUpdate
from app.core.dependencies import require_role
from app.models.user import User

router = APIRouter(prefix="/plans", tags=["Plans"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_plan_event(db: Session, plan_id: int, event: str, actor: str):
    entry = AuditLog(entity_type="plan", entity_id=plan_id, event=event, actor=actor)
    db.add(entry)
    db.commit()


@router.post("/", response_model=PlanResponse)
def create_plan(
    plan: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    new_plan = Plan(**plan.dict(), status="active")
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    log_plan_event(db, new_plan.id, "plan.created", current_user.email)
    return new_plan


@router.get("/", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    """Customer-facing: only plans currently offered for subscription."""
    return db.query(Plan).filter(Plan.status == "active").all()


@router.get("/admin", response_model=list[PlanResponse])
def list_all_plans(
    status: Optional[str] = Query(None, description="active | inactive | deleted"),
    billing_interval: Optional[str] = Query(None, description="monthly | yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Admin: every plan regardless of status, with optional filters."""
    query = db.query(Plan)
    if status:
        query = query.filter(Plan.status == status)
    if billing_interval:
        query = query.filter(Plan.billing_interval == billing_interval)
    return query.order_by(Plan.id.desc()).all()


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_update: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    update_data = plan_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    log_plan_event(db, plan.id, "plan.updated", current_user.email)
    return plan


@router.patch("/{plan_id}/status", response_model=PlanResponse)
def set_plan_status(
    plan_id: int,
    payload: PlanStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Toggle a plan between active and temporarily-inactive."""
    if payload.status not in ("active", "inactive"):
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'inactive'")

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status == "deleted":
        raise HTTPException(status_code=400, detail="Cannot change status of a deleted plan")

    plan.status = payload.status
    db.commit()
    db.refresh(plan)
    log_plan_event(db, plan.id, f"plan.status_changed:{payload.status}", current_user.email)
    return plan


@router.delete("/{plan_id}", response_model=PlanResponse)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Soft delete — the row stays for history/audit; only the status flips."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status == "deleted":
        raise HTTPException(status_code=400, detail="Plan is already deleted")

    plan.status = "deleted"
    plan.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(plan)
    log_plan_event(db, plan.id, "plan.deleted", current_user.email)
    return plan