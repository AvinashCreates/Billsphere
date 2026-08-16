from datetime import datetime, timezone
from app.models.subscription import Subscription
from app.models.plan import Plan


def period_length_days(plan: Plan) -> int:
    return 365 if plan.billing_interval == "yearly" else 30


def calculate_proration(sub: Subscription, old_plan: Plan, new_plan: Plan, now: datetime = None) -> dict:
    """
    Calculates the immediate charge (or credit) when a subscription changes
    plans mid-cycle. The subscription's current_period_end is not touched
    here — only the money owed for the remainder of the current period.

    Returns a dict with:
      - days_remaining
      - days_in_period
      - unused_credit   (value of unused time on the OLD plan)
      - new_plan_charge (cost of the NEW plan for the remaining days)
      - net_amount      (positive = customer owes this now,
                          negative = credit toward their next invoice)
    """
    now = now or datetime.now(timezone.utc)

    period_start = sub.current_period_start
    period_end = sub.current_period_end

    total_period_seconds = (period_end - period_start).total_seconds()
    remaining_seconds = max(0, (period_end - now).total_seconds())

    days_in_period = max(1, round(total_period_seconds / 86400))
    days_remaining = round(remaining_seconds / 86400, 2)

    fraction_remaining = remaining_seconds / total_period_seconds if total_period_seconds > 0 else 0

    unused_credit = round(float(old_plan.price) * fraction_remaining, 2)
    new_plan_charge = round(float(new_plan.price) * fraction_remaining, 2)
    net_amount = round(new_plan_charge - unused_credit, 2)

    return {
        "days_remaining": days_remaining,
        "days_in_period": days_in_period,
        "unused_credit": unused_credit,
        "new_plan_charge": new_plan_charge,
        "net_amount": net_amount,
    }