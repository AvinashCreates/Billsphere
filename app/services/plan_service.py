from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.schemas.plan import (
    PlanCreate,
    PlanUpdate,
)

from app.repositories.plan_repository import (
    get_all_plans,
    get_active_plans,
    get_active_plan_by_id,
    get_plan_by_id,
    create_plan,
    update_plan,
    delete_plan,
)

def fetch_plans(
    db: Session,
    user,
):

    if user.role == "admin":
        return get_all_plans(db)

    return get_active_plans(db)

def fetch_plan(
    db: Session,
    plan_id: int,
    user,
):
    if user.role == "admin":
        return get_plan_by_id(
            db,
            plan_id,
        )

    return get_active_plan_by_id(
        db,
        plan_id,
    )

def add_plan(db: Session, plan: PlanCreate):

    new_plan = Plan(
        name=plan.name,
        description=plan.description,
        price=plan.price,
        duration=plan.duration,
        status="active",
    )

    return create_plan(db, new_plan)

def edit_plan(
    db: Session,
    plan_id: int,
    plan: PlanUpdate,
):

    existing = get_plan_by_id(db, plan_id)

    if not existing:
        return None

    existing.name = plan.name
    existing.description = plan.description
    existing.price = plan.price
    existing.duration = plan.duration
    existing.status = plan.status

    return update_plan(db, existing)


def remove_plan(
    db: Session,
    plan_id: int,
):

    existing = get_plan_by_id(
        db,
        plan_id
    )

    if not existing:
        return False

    existing.status = "inactive"

    return update_plan(
        db,
        existing
    )