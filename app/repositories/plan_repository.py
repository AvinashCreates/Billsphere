from sqlalchemy.orm import Session

from app.models.plan import Plan


def get_all_plans(db: Session):
    return db.query(Plan).all()


def get_plan_by_id(db: Session, plan_id: int):
    return db.query(Plan).filter(
        Plan.id == plan_id
    ).first()


def create_plan(db: Session, plan: Plan):
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db: Session, existing_plan: Plan):
    db.commit()
    db.refresh(existing_plan)
    return existing_plan


def delete_plan(db: Session, plan: Plan):
    db.delete(plan)
    db.commit()

def get_active_plans(db: Session):
    return (
        db.query(Plan)
        .filter(Plan.status == "active")
        .all()
    )

def get_active_plan_by_id(
    db: Session,
    plan_id: int,
):
    return (
        db.query(Plan)
        .filter(
            Plan.id == plan_id,
            Plan.status == "active"
        )
        .first()
    )