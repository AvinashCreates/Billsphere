from datetime import datetime, timezone
from app.workers.celery_app import celery_app
from app.database.database import SessionLocal
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.models.plan import Plan
from app.services.subscription_logic import log_event, promote_pending_subscription
from app.workers.email_tasks import send_past_due_email


@celery_app.task(name="app.workers.tasks.process_due_subscriptions")
def process_due_subscriptions():
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    processed = []

    try:
        due_subs = (
            db.query(Subscription)
            .filter(
                Subscription.status.in_(["active", "trial"]),
                Subscription.current_period_end <= now,
            )
            .all()
        )

        for sub in due_subs:
            plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
            customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()

            pending_exists = False
            if plan:
                pending_exists = (
                    db.query(Subscription)
                    .join(Plan, Plan.id == Subscription.plan_id)
                    .filter(
                        Subscription.customer_id == sub.customer_id,
                        Subscription.status == "pending",
                        Plan.name == plan.name,
                    )
                    .first()
                ) is not None

            if pending_exists:
                sub.status = "cancelled"
                log_event(db, sub.id, "subscription.auto_cancelled_pending_takeover", "system:celery")
                promote_pending_subscription(db, sub.customer_id, plan.name, actor="system:celery")
            elif sub.cancel_at_period_end:
                sub.status = "cancelled"
                log_event(db, sub.id, "subscription.auto_cancelled_at_period_end", "system:celery")
            else:
                sub.status = "past_due"
                log_event(db, sub.id, "subscription.auto_marked_past_due", "system:celery")
                if plan and customer:
                    send_past_due_email.delay(customer.email, customer.name, plan.name, sub.current_period_end.isoformat())

            processed.append(sub.id)

        db.commit()
        return {"processed_subscription_ids": processed, "checked_at": now.isoformat()}

    finally:
        db.close()