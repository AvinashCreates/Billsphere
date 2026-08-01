from datetime import datetime, timezone
from app.workers.celery_app import celery_app
from app.database.database import SessionLocal
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.models.plan import Plan


def log_event(db, entity_id: int, event: str, actor: str = "system:celery"):
    entry = AuditLog(
        entity_type="subscription",
        entity_id=entity_id,
        event=event,
        actor=actor,
    )
    db.add(entry)
    db.commit()


@celery_app.task(name="app.workers.tasks.process_due_subscriptions")
def process_due_subscriptions():
    """
    Runs on a schedule (Celery beat). Finds subscriptions whose current
    billing period has ended and moves them to the next state:
      - if cancel_at_period_end was set -> cancelled
      - otherwise -> past_due (awaiting renewal/payment)

    This is the automated equivalent of manually calling /expire on each
    subscription — it's what actually makes the state machine "live"
    instead of requiring an admin to trigger it by hand.
    """
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
            if sub.cancel_at_period_end:
                sub.status = "cancelled"
                log_event(db, sub.id, "subscription.auto_cancelled_at_period_end")
            else:
                sub.status = "past_due"
                log_event(db, sub.id, "subscription.auto_marked_past_due")

            processed.append(sub.id)

        db.commit()
        return {"processed_subscription_ids": processed, "checked_at": now.isoformat()}

    finally:
        db.close()
