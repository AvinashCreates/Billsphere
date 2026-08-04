from datetime import datetime, timezone
from app.workers.celery_app import celery_app
from app.core.email import send_email
from app.core import email_templates as templates
from app.database.database import SessionLocal
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.audit_log import AuditLog


@celery_app.task(name="app.workers.email_tasks.send_welcome_email", bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_email: str, user_name: str):
    subject, html = templates.welcome_email(user_name)
    if not send_email(user_email, subject, html):
        raise self.retry()
    return {"sent_to": user_email, "type": "welcome"}


@celery_app.task(name="app.workers.email_tasks.send_subscription_confirmation", bind=True, max_retries=3, default_retry_delay=60)
def send_subscription_confirmation(self, customer_email: str, customer_name: str, plan_name: str, billing_interval: str, deadline_iso: str):
    deadline_str = datetime.fromisoformat(deadline_iso).strftime("%d %B %Y")
    subject, html = templates.subscription_confirmation_email(customer_name, plan_name, billing_interval, deadline_str)
    if not send_email(customer_email, subject, html):
        raise self.retry()
    return {"sent_to": customer_email, "type": "subscription_confirmation"}


@celery_app.task(name="app.workers.email_tasks.send_deadline_reminder", bind=True, max_retries=3, default_retry_delay=60)
def send_deadline_reminder(self, customer_email: str, customer_name: str, plan_name: str, deadline_iso: str, days_left: int):
    deadline_str = datetime.fromisoformat(deadline_iso).strftime("%d %B %Y")
    subject, html = templates.deadline_reminder_email(customer_name, plan_name, deadline_str, days_left)
    if not send_email(customer_email, subject, html):
        raise self.retry()
    return {"sent_to": customer_email, "type": "deadline_reminder", "days_left": days_left}


REMINDER_WINDOWS_DAYS = [3, 1]  # send a reminder 3 days out and again 1 day out


@celery_app.task(name="app.workers.email_tasks.check_upcoming_deadlines")
def check_upcoming_deadlines():
    """
    Runs daily via Celery beat. Finds active/trial subscriptions whose
    current_period_end falls within a reminder window and queues a mail —
    once per (subscription, window, period_end), tracked via AuditLog so
    reruns don't double-send.
    """
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    queued = []

    try:
        active_subs = (
            db.query(Subscription)
            .filter(Subscription.status.in_(["active", "trial"]))
            .all()
        )

        for sub in active_subs:
            days_left = (sub.current_period_end - now).days
            if days_left not in REMINDER_WINDOWS_DAYS:
                continue

            reminder_tag = f"reminder.deadline_{days_left}d:{sub.current_period_end.isoformat()}"

            already_sent = (
                db.query(AuditLog)
                .filter(
                    AuditLog.entity_type == "subscription",
                    AuditLog.entity_id == sub.id,
                    AuditLog.event == reminder_tag,
                )
                .first()
            )
            if already_sent:
                continue

            customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()
            plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
            if not customer or not plan:
                continue

            send_deadline_reminder.delay(
                customer.email, customer.name, plan.name,
                sub.current_period_end.isoformat(), days_left,
            )

            db.add(AuditLog(
                entity_type="subscription",
                entity_id=sub.id,
                event=reminder_tag,
                actor="system:celery",
            ))
            db.commit()
            queued.append(sub.id)

        return {"queued_subscription_ids": queued, "checked_at": now.isoformat()}

    finally:
        db.close()