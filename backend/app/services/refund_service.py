from datetime import datetime, timezone
from app.models.subscription import Subscription


def calculate_unused_period_refund(sub: Subscription, amount_paid: float, now: datetime = None) -> dict:
    """
    Calculates how much of a payment should be refunded when a customer
    cancels immediately, based on how much of the billing period is
    still unused.

    Returns a dict with:
      - fraction_unused
      - days_remaining
      - refund_amount
    """
    now = now or datetime.now(timezone.utc)

    period_start = sub.current_period_start
    period_end = sub.current_period_end

    total_period_seconds = (period_end - period_start).total_seconds()
    remaining_seconds = max(0, (period_end - now).total_seconds())

    fraction_unused = remaining_seconds / total_period_seconds if total_period_seconds > 0 else 0
    days_remaining = round(remaining_seconds / 86400, 2)

    refund_amount = round(amount_paid * fraction_unused, 2)

    return {
        "fraction_unused": round(fraction_unused, 4),
        "days_remaining": days_remaining,
        "refund_amount": refund_amount,
    }