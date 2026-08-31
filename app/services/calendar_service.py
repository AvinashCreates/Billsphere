from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.plan import Plan
from app.models.user import User


def get_billing_calendar_events(db: Session, days_ahead: int = 60):
    now = datetime.now(UTC)
    window_end = now + timedelta(days=days_ahead)

    events = []

    subs = (
        db.query(Subscription, User, Plan)
        .join(User, Subscription.user_id == User.id)
        .join(Plan, Subscription.plan_id == Plan.id)
        .filter(
            Subscription.status == "active",
            Subscription.current_period_end <= window_end,
        )
        .all()
    )

    for sub, user, plan in subs:
        period_end = sub.current_period_end
        if period_end.tzinfo is None:
            period_end = period_end.replace(tzinfo=UTC)

        events.append({
            "date": period_end.date().isoformat(),
            "event_type": "renewal_due" if period_end >= now else "renewal_overdue",
            "customer_id": user.id,
            "customer_name": user.username,
            "reference": plan.name,
            "amount": plan.price,
            "status": "upcoming" if period_end >= now else "overdue",
        })

    invoices = (
        db.query(Invoice, User)
        .join(User, Invoice.user_id == User.id)
        .filter(
            Invoice.payment_status != "paid",
            Invoice.due_date <= window_end,
        )
        .all()
    )

    for invoice, user in invoices:
        due = invoice.due_date
        if not due:
            continue
        if due.tzinfo is None:
            due = due.replace(tzinfo=UTC)

        is_overdue = due < now or invoice.status == "overdue"

        events.append({
            "date": due.date().isoformat(),
            "event_type": "payment_overdue" if is_overdue else "invoice_due",
            "customer_id": user.id,
            "customer_name": user.username,
            "reference": invoice.invoice_number,
            "amount": invoice.total_amount,
            "status": "overdue" if is_overdue else "upcoming",
        })

    events.sort(key=lambda e: e["date"])
    return events