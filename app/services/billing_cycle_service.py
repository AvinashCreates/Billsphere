"""
BillSphere Billing Cycle Service

Handles:

- Starting a billing cycle
- Creating billing cycle history records
- Calculating billing period dates
- Updating subscription billing-period metadata
- Generating renewal invoices
- Closing/renewing billing cycles
- Processing subscriptions at period end
- Cancel-at-period-end handling
- Preventing duplicate billing cycles

Billing flow:

    Subscription
        |
        v
    Start Billing Cycle
        |
        +--> BillingCycle
        |
        +--> Subscription period fields
        |
        v
    Period End
        |
        +--> cancel_at_period_end = True
        |        |
        |        v
        |      Cancel
        |
        +--> cancel_at_period_end = False
                 |
                 v
             Renewal Invoice
                 |
                 v
             New Billing Cycle
"""

from __future__ import annotations

from calendar import monthrange
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.billing_cycle import BillingCycle
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.invoice_line_item import InvoiceLineItem
from app.models.usage_record import UsageRecord
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.services.invoice_service import generate_invoice_number
from app.services.tax_service import calculate_tax
from app.services.subscription_state_machine import (
    SubscriptionLifecycleException,
    process_period_end as state_machine_process_period_end,
)


# ==========================================================
# Constants
# ==========================================================

ACTIVE_CYCLE_STATUS = "active"
RENEWED_CYCLE_STATUS = "renewed"
INVOICED_CYCLE_STATUS = "invoiced"
CLOSED_CYCLE_STATUS = "closed"


# ==========================================================
# Internal Helpers
# ==========================================================


def _now() -> datetime:
    """
    Return the current UTC datetime.
    """
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    """
    Normalize a datetime to UTC.

    Handles both timezone-aware and naive datetimes.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _add_months(
    value: datetime,
    months: int,
) -> datetime:
    """
    Add calendar months while preserving the day as much as possible.

    Example:

        January 31 + 1 month
        -> February 28/29

    This is preferable to simply adding 30 days for
    monthly billing cycles.
    """

    if months == 0:
        return value

    year = value.year
    month = value.month + months

    year += (month - 1) // 12
    month = ((month - 1) % 12) + 1

    day = min(
        value.day,
        monthrange(year, month)[1],
    )

    return value.replace(
        year=year,
        month=month,
        day=day,
    )


def _calculate_cycle_end(
    cycle_start: datetime,
    billing_cycle: str,
) -> datetime:
    """
    Calculate the end of a billing period.

    Supported cycles:

        daily
        weekly
        monthly
        quarterly
        yearly
        annual

    Unknown cycles fall back to monthly.
    """

    normalized_cycle = (
        str(billing_cycle or "monthly")
        .strip()
        .lower()
    )

    if normalized_cycle == "daily":
        return cycle_start + timedelta(days=1)

    if normalized_cycle == "weekly":
        return cycle_start + timedelta(days=7)

    if normalized_cycle == "monthly":
        return _add_months(
            cycle_start,
            1,
        )

    if normalized_cycle == "quarterly":
        return _add_months(
            cycle_start,
            3,
        )

    if normalized_cycle in {"yearly", "annual"}:
        return _add_months(
            cycle_start,
            12,
        )

    # Safe fallback.
    return _add_months(
        cycle_start,
        1,
    )


def _get_tax_rate() -> Decimal:
    """
    Read the configured tax percentage safely.
    """

    return Decimal(
        str(
            getattr(
                settings,
                "TAX_PERCENTAGE",
                18.00,
            )
        )
    )


def _get_customer_country(
    db: Session,
    customer_id: int,
) -> str:
    """
    Get the customer's country.

    Defaults to India because BillSphere currently
    uses India GST as its primary tax implementation.
    """

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id
        )
        .first()
    )

    if not customer:
        return "IN"

    country = getattr(
        customer,
        "country",
        None,
    )

    return (
        str(country).upper()
        if country
        else "IN"
    )


# ==========================================================
# Find Existing Cycle
# ==========================================================


def get_active_billing_cycle(
    db: Session,
    subscription_id: int,
) -> BillingCycle | None:
    """
    Return the currently active billing cycle.

    Only one active cycle should normally exist for a
    subscription.
    """

    return (
        db.query(BillingCycle)
        .filter(
            BillingCycle.subscription_id
            == subscription_id,
            BillingCycle.status
            == ACTIVE_CYCLE_STATUS,
        )
        .order_by(
            BillingCycle.id.desc()
        )
        .first()
    )


# ==========================================================
# Get Latest Billing Cycle
# ==========================================================


def get_latest_billing_cycle(
    db: Session,
    subscription_id: int,
) -> BillingCycle | None:
    """
    Return the latest billing-cycle record.
    """

    return (
        db.query(BillingCycle)
        .filter(
            BillingCycle.subscription_id
            == subscription_id
        )
        .order_by(
            BillingCycle.id.desc()
        )
        .first()
    )


# ==========================================================
# Create Billing Cycle
# ==========================================================


def create_billing_cycle(
    db: Session,
    subscription: Subscription,
    cycle_start: datetime | None = None,
    cycle_end: datetime | None = None,
    status_value: str = ACTIVE_CYCLE_STATUS,
) -> BillingCycle:
    """
    Create a billing-cycle history record.

    If dates are not supplied, they are calculated from
    the subscription's billing cycle.
    """

    start = _as_utc(
        cycle_start
        or subscription.current_period_start
        or subscription.start_date
    )

    if cycle_end:
        end = _as_utc(cycle_end)

    elif subscription.current_period_end:
        end = _as_utc(
            subscription.current_period_end
        )

    else:
        end = _calculate_cycle_end(
            start,
            subscription.billing_cycle,
        )

    # ------------------------------------------------------
    # Duplicate protection
    # ------------------------------------------------------

    existing = (
        db.query(BillingCycle)
        .filter(
            BillingCycle.subscription_id
            == subscription.id,
            BillingCycle.cycle_start
            == start,
            BillingCycle.cycle_end
            == end,
        )
        .first()
    )

    if existing:
        return existing

    billing_cycle = BillingCycle(
        subscription_id=subscription.id,
        cycle_start=start,
        cycle_end=end,
        status=status_value,
        invoice_id=None,
        created_at=_now(),
    )

    db.add(billing_cycle)

    db.flush()

    return billing_cycle


# ==========================================================
# Start Subscription Billing Cycle
# ==========================================================


def start_subscription_billing_cycle(
    db: Session,
    subscription: Subscription,
) -> BillingCycle:
    """
    Start the first billing cycle for a subscription.

    This also synchronizes the live billing-period fields
    on Subscription.
    """

    start = (
        subscription.current_period_start
        or subscription.start_date
    )

    start = _as_utc(start)

    end = subscription.current_period_end

    if not end:
        end = _calculate_cycle_end(
            start,
            subscription.billing_cycle,
        )
    else:
        end = _as_utc(end)

    # ------------------------------------------------------
    # Update subscription period metadata
    # ------------------------------------------------------

    subscription.current_period_start = start
    subscription.current_period_end = end
    subscription.next_billing_date = end

    # ------------------------------------------------------
    # Reuse existing active cycle if available
    # ------------------------------------------------------

    existing = get_active_billing_cycle(
        db,
        subscription.id,
    )

    if existing:
        return existing

    cycle = create_billing_cycle(
        db=db,
        subscription=subscription,
        cycle_start=start,
        cycle_end=end,
        status_value=ACTIVE_CYCLE_STATUS,
    )

    db.flush()

    return cycle


# ==========================================================
# Create Renewal Invoice
# ==========================================================


def create_renewal_invoice(
    db: Session,
    subscription: Subscription,
    plan: Plan,
) -> Invoice:
    """
    Generate a complete renewal invoice.

    Components:
    - recurring plan fee
    - unbilled usage
    - tax line items
    - unique invoice number
    """
    plan_amount = Decimal(str(plan.price or 0)).quantize(Decimal("0.01"))
    if plan_amount < 0:
        raise HTTPException(status_code=400, detail="Plan price cannot be negative.")

    usage_records = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.subscription_id == subscription.id,
            UsageRecord.invoiced.is_(False),
        )
        .all()
    )
    usage_amount = sum(
        (Decimal(str(record.amount or 0)) for record in usage_records),
        Decimal("0.00"),
    ).quantize(Decimal("0.01"))

    taxable_amount = (plan_amount + usage_amount).quantize(Decimal("0.01"))
    country_code = _get_customer_country(db, subscription.customer_id)
    customer = (
        db.query(Customer)
        .filter(Customer.id == subscription.customer_id)
        .first()
    )
    same_state = (
        country_code == str(getattr(settings, "COMPANY_COUNTRY", "IN")).upper()
        and (getattr(customer, "state", None) or "").strip().lower()
        == str(getattr(settings, "COMPANY_STATE", "")).strip().lower()
    )
    breakdown = calculate_tax(
        amount=taxable_amount,
        country_code=country_code,
        tax_rate_percent=None,
        same_state=same_state,
    )

    now = _now()
    invoice = Invoice(
        invoice_number=generate_invoice_number(db),
        customer_id=subscription.customer_id,
        subscription_id=subscription.id,
        amount=breakdown.taxable_amount,
        tax_amount=breakdown.total_tax,
        total_amount=breakdown.total_amount,
        status="pending",
        due_date=now,
        paid_at=None,
        created_at=now,
    )
    db.add(invoice)
    db.flush()

    db.add(InvoiceLineItem(
        invoice_id=invoice.id,
        description=f"{plan.name} subscription ({subscription.billing_cycle})",
        item_type="subscription",
        amount=plan_amount,
    ))

    for record in usage_records:
        db.add(InvoiceLineItem(
            invoice_id=invoice.id,
            description=f"{record.description} x{record.quantity}",
            item_type="usage",
            amount=Decimal(str(record.amount or 0)).quantize(Decimal("0.01")),
        ))
        record.invoiced = True
        record.invoice_id = invoice.id

    if breakdown.cgst > 0:
        db.add(InvoiceLineItem(
            invoice_id=invoice.id,
            description=f"CGST ({breakdown.tax_rate_percent / 2}%)",
            item_type="tax_cgst",
            amount=breakdown.cgst,
        ))
    if breakdown.sgst > 0:
        db.add(InvoiceLineItem(
            invoice_id=invoice.id,
            description=f"SGST ({breakdown.tax_rate_percent / 2}%)",
            item_type="tax_sgst",
            amount=breakdown.sgst,
        ))
    if breakdown.igst > 0:
        db.add(InvoiceLineItem(
            invoice_id=invoice.id,
            description=f"IGST ({breakdown.tax_rate_percent}%)",
            item_type="tax_igst",
            amount=breakdown.igst,
        ))

    db.flush()
    return invoice


# ==========================================================
# Close Billing Cycle
# ==========================================================


def close_billing_cycle(
    db: Session,
    billing_cycle: BillingCycle,
    status_value: str = CLOSED_CYCLE_STATUS,
) -> BillingCycle:
    """
    Close an existing billing cycle.
    """

    billing_cycle.status = status_value

    db.flush()

    return billing_cycle


# ==========================================================
# Attach Invoice To Cycle
# ==========================================================


def attach_invoice_to_billing_cycle(
    db: Session,
    billing_cycle: BillingCycle,
    invoice: Invoice,
) -> BillingCycle:
    """
    Attach an invoice to a billing cycle.

    The cycle is marked as invoiced.
    """

    billing_cycle.invoice_id = invoice.id
    billing_cycle.status = INVOICED_CYCLE_STATUS

    db.flush()

    return billing_cycle


# ==========================================================
# Renew Subscription
# ==========================================================


def renew_subscription(
    db: Session,
    subscription: Subscription,
) -> dict:
    """
    Renew a subscription after its current billing period ends.

    Steps:

        1. Validate subscription.
        2. Find current billing cycle.
        3. Check cancellation-at-period-end.
        4. Generate renewal invoice.
        5. Close old cycle.
        6. Calculate next period.
        7. Create next billing cycle.
        8. Update subscription dates.
    """

    now = _now()

    # ------------------------------------------------------
    # Validate billing period
    # ------------------------------------------------------

    current_end = subscription.current_period_end

    if not current_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Subscription does not have a current "
                "billing period."
            ),
        )

    current_end = _as_utc(
        current_end
    )

    # ------------------------------------------------------
    # Do not renew too early
    # ------------------------------------------------------

    if current_end > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Subscription billing period has not "
                "ended yet."
            ),
        )

    # ------------------------------------------------------
    # Find current cycle
    # ------------------------------------------------------

    current_cycle = get_active_billing_cycle(
        db,
        subscription.id,
    )

    # ------------------------------------------------------
    # Cancellation at period end
    # ------------------------------------------------------

    if subscription.cancel_at_period_end:
        try:
            state_machine_process_period_end(
                db=db,
                subscription=subscription,
                user_id=None,
            )

        except SubscriptionLifecycleException:
            # If the state machine does not need processing,
            # continue with explicit cancellation metadata.
            pass

        subscription.cancel_at_period_end = False

        subscription.cancelled_at = now

        if current_cycle:
            close_billing_cycle(
                db,
                current_cycle,
                CLOSED_CYCLE_STATUS,
            )

        db.flush()

        return {
            "renewed": False,
            "cancelled": True,
            "invoice": None,
            "billing_cycle": current_cycle,
            "subscription": subscription,
        }

    # ------------------------------------------------------
    # Get plan
    # ------------------------------------------------------

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found.",
        )

    # ------------------------------------------------------
    # Create renewal invoice
    # ------------------------------------------------------

    invoice = create_renewal_invoice(
        db=db,
        subscription=subscription,
        plan=plan,
    )

    # ------------------------------------------------------
    # Close old billing cycle
    # ------------------------------------------------------

    if current_cycle:
        current_cycle.invoice_id = invoice.id
        current_cycle.status = RENEWED_CYCLE_STATUS
        db.flush()

    # ------------------------------------------------------
    # Calculate next billing period
    # ------------------------------------------------------

    next_start = current_end

    next_end = _calculate_cycle_end(
        next_start,
        subscription.billing_cycle,
    )

    # ------------------------------------------------------
    # Update subscription
    # ------------------------------------------------------

    subscription.current_period_start = next_start
    subscription.current_period_end = next_end
    subscription.next_billing_date = next_end

    # ------------------------------------------------------
    # Create next cycle
    # ------------------------------------------------------

    next_cycle = create_billing_cycle(
        db=db,
        subscription=subscription,
        cycle_start=next_start,
        cycle_end=next_end,
        status_value=ACTIVE_CYCLE_STATUS,
    )

    db.flush()

    return {
        "renewed": True,
        "cancelled": False,
        "invoice": invoice,
        "billing_cycle": next_cycle,
        "subscription": subscription,
    }


# ==========================================================
# Process Subscription At Period End
# ==========================================================


def process_subscription_billing_period(
    db: Session,
    subscription_id: int,
) -> dict:
    """
    Process one subscription whose billing period has ended.

    This is the main function that a scheduler/Celery worker
    should call.
    """

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id
            == subscription_id
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found.",
        )

    try:
        result = renew_subscription(
            db=db,
            subscription=subscription,
        )

        db.commit()

        db.refresh(subscription)

        return result

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


# ==========================================================
# Process Due Subscriptions
# ==========================================================


def process_due_subscriptions(
    db: Session,
    limit: int = 100,
) -> list[dict]:
    """
    Find subscriptions whose billing period has ended
    and process them.

    This function is designed for Celery Beat / scheduler use.
    """

    if limit < 1:
        limit = 1

    if limit > 1000:
        limit = 1000

    now = _now()

    subscriptions = (
        db.query(Subscription)
        .filter(
            Subscription.current_period_end.isnot(None),
            Subscription.current_period_end <= now,
            Subscription.status.in_(
                [
                    "trial",
                    "active",
                    "past_due",
                ]
            ),
        )
        .order_by(
            Subscription.id.asc()
        )
        .limit(limit)
        .all()
    )

    results: list[dict] = []

    for subscription in subscriptions:
        try:
            result = renew_subscription(
                db=db,
                subscription=subscription,
            )

            db.commit()

            db.refresh(subscription)

            results.append(
                {
                    "subscription_id": subscription.id,
                    "success": True,
                    "renewed": result.get(
                        "renewed",
                        False,
                    ),
                    "cancelled": result.get(
                        "cancelled",
                        False,
                    ),
                    "invoice_id": (
                        result["invoice"].id
                        if result.get("invoice")
                        else None
                    ),
                    "billing_cycle_id": (
                        result["billing_cycle"].id
                        if result.get("billing_cycle")
                        else None
                    ),
                }
            )

        except Exception as exc:
            db.rollback()

            results.append(
                {
                    "subscription_id": subscription.id,
                    "success": False,
                    "renewed": False,
                    "cancelled": False,
                    "invoice_id": None,
                    "billing_cycle_id": None,
                    "error": str(exc),
                }
            )

    return results


# ==========================================================
# Initialize Billing Cycle For Existing Subscription
# ==========================================================


def initialize_subscription_billing_cycle(
    db: Session,
    subscription_id: int,
) -> BillingCycle:
    """
    Initialize billing-cycle information for an existing
    subscription.

    Useful for subscriptions created before the Billing Cycle
    Engine was introduced.
    """

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found.",
        )

    try:
        cycle = start_subscription_billing_cycle(
            db=db,
            subscription=subscription,
        )

        db.commit()

        db.refresh(subscription)
        db.refresh(cycle)

        return cycle

    except Exception:
        db.rollback()
        raise


# ==========================================================
# Synchronize Subscription Billing Metadata
# ==========================================================


def synchronize_subscription_billing_period(
    db: Session,
    subscription: Subscription,
) -> Subscription:
    """
    Synchronize Subscription's live billing-period metadata
    with its active BillingCycle.

    This does not create a new cycle if one already exists.
    """

    cycle = get_active_billing_cycle(
        db,
        subscription.id,
    )

    if not cycle:
        cycle = start_subscription_billing_cycle(
            db=db,
            subscription=subscription,
        )
    else:
        subscription.current_period_start = (
            cycle.cycle_start
        )

        subscription.current_period_end = (
            cycle.cycle_end
        )

        subscription.next_billing_date = (
            cycle.cycle_end
        )

    db.flush()

    return subscription


# ==========================================================
# Billing Cycle History
# ==========================================================


def list_billing_cycles(
    db: Session,
    subscription_id: int,
) -> list[BillingCycle]:
    """
    Return billing-cycle history for a subscription.
    """

    subscription_exists = (
        db.query(Subscription.id)
        .filter(
            Subscription.id == subscription_id
        )
        .first()
    )

    if not subscription_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found.",
        )

    return (
        db.query(BillingCycle)
        .filter(
            BillingCycle.subscription_id
            == subscription_id
        )
        .order_by(
            BillingCycle.id.desc()
        )
        .all()
    )

# ==========================================================
# Scheduler Compatibility Wrapper
# ==========================================================


def renew_subscription_billing_period(
    db: Session,
    subscription_id: int,
) -> dict:
    """
    Renew a subscription's billing period.

    This function is the scheduler-facing entry point.

    It loads the subscription and delegates the actual
    renewal logic to renew_subscription().
    """

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found.",
        )

    try:
        result = renew_subscription(
            db=db,
            subscription=subscription,
        )

        db.commit()
        db.refresh(subscription)

        return result

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise