"""
BillSphere Subscription Service

Business logic for:

- Creating subscriptions
- Fetching subscriptions
- Listing subscriptions
- Updating subscriptions
- Immediate cancellation with unused-period refund
- Subscription lifecycle management
- Pause / Resume
- Cancel at period end
- Plan change with proration
- Subscription history
- State-machine integration
- Audit logging
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.invoice_line_item import InvoiceLineItem
from app.models.payment import Payment
from app.models.plan import Plan
from app.models.subscription import Subscription

from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
)

from app.services.invoice_service import (
    generate_invoice_number,
)

from app.services.subscription_state_machine import (
    SubscriptionLifecycleException,
    SubscriptionStatus,
    activate_subscription as state_machine_activate,
    cancel_subscription as state_machine_cancel,
    mark_past_due as state_machine_mark_past_due,
    pause_subscription as state_machine_pause,
    process_period_end as state_machine_process_period_end,
    resume_subscription as state_machine_resume,
    schedule_cancel_at_period_end as state_machine_schedule_cancel,
)

from app.services.tax_service import calculate_tax

from app.services.billing_cycle_service import (
    start_subscription_billing_cycle,
)

from app.services.proration_service import (
    calculate_proration,
)


# ==========================================================
# Internal Helpers
# ==========================================================


def _commit_and_refresh(
    db: Session,
    subscription: Subscription,
) -> Subscription:
    db.commit()
    db.refresh(subscription)
    return subscription


def _rollback(db: Session) -> None:
    try:
        db.rollback()
    except Exception:
        pass


def _raise_lifecycle_error(
    error: SubscriptionLifecycleException,
) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    ) from error


# ==========================================================
# Plan Validation Helper
# ==========================================================


def _get_active_plan(
    db: Session,
    plan_id: int,
) -> Plan:
    """
    Fetch the selected plan and make sure it is active.

    This is the central validation used whenever a subscription
    references a plan.
    """

    if not plan_id or plan_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid plan_id is required.",
        )

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == plan_id,
            Plan.is_active.is_(True),
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active plan with ID {plan_id} not found.",
        )

    return plan


# ==========================================================
# Remaining Days Helper
# ==========================================================


def _remaining_days_ratio(
    subscription: Subscription,
) -> tuple[int, int]:
    """
    Returns:

        (remaining_days, total_days)

    for the current billing period.
    """

    now = datetime.now(timezone.utc)

    period_start = subscription.current_period_start
    period_end = subscription.current_period_end

    if not period_start or not period_end:
        return 0, 1

    if period_end <= now:
        return 0, 1

    if period_start.tzinfo is None:
        period_start = period_start.replace(
            tzinfo=timezone.utc
        )

    if period_end.tzinfo is None:
        period_end = period_end.replace(
            tzinfo=timezone.utc
        )

    total_days = max(
        (period_end - period_start).days,
        1,
    )

    remaining_days = max(
        (period_end - now).days,
        0,
    )

    return remaining_days, total_days


# ==========================================================
# Unused Period Refund
# ==========================================================


def _issue_unused_period_refund(
    db: Session,
    subscription: Subscription,
    reason: str,
) -> None:
    """
    Refund the unused portion of the current billing period.
    """

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not plan:
        return

    remaining_days, total_days = (
        _remaining_days_ratio(subscription)
    )

    if remaining_days <= 0:
        return

    unused_amount = (
        Decimal(str(plan.price))
        * Decimal(remaining_days)
        / Decimal(total_days)
    ).quantize(
        Decimal("0.01")
    )

    if unused_amount <= 0:
        return

    latest_paid_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.subscription_id == subscription.id,
            Invoice.status == "paid",
        )
        .order_by(
            Invoice.id.desc()
        )
        .first()
    )

    if not latest_paid_invoice:
        return

    payment = (
        db.query(Payment)
        .filter(
            Payment.invoice_id == latest_paid_invoice.id,
            Payment.status == "completed",
        )
        .order_by(
            Payment.id.desc()
        )
        .first()
    )

    if not payment:
        return

    refund_amount = min(
        unused_amount,
        Decimal(str(payment.amount)),
    )

    from app.services.payment_service import (
        refund_payment,
    )

    refund_payment(
        db,
        payment.id,
        amount=refund_amount,
        reason=reason,
    )


# ==========================================================
# Create Subscription
# ==========================================================


def create_subscription(
    db: Session,
    subscription_data: SubscriptionCreate,
    created_by: int | None = None,
) -> Subscription:
    """
    Create a subscription using the selected plan_id.

    The selected plan determines:

    - Plan validity
    - Billing cycle
    - Trial duration
    - Price
    - Entitlements

    The subscription stores the plan_id rather than copying
    plan pricing into the subscription.
    """

    # ------------------------------------------------------
    # Validate customer
    # ------------------------------------------------------

    customer = (
        db.query(Customer)
        .filter(
            Customer.id
            == subscription_data.customer_id
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    # ------------------------------------------------------
    # Validate selected plan
    # ------------------------------------------------------

    plan = _get_active_plan(
        db,
        subscription_data.plan_id,
    )

    # ------------------------------------------------------
    # Validate status
    # ------------------------------------------------------

    status_value = (
        subscription_data.status
        .strip()
        .lower()
    )

    if status_value not in {
        "trial",
        "active",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New subscriptions must start as "
                "trial or active."
            ),
        )

    # ------------------------------------------------------
    # Start date
    # ------------------------------------------------------

    start = subscription_data.start_date

    if start.tzinfo is None:
        start = start.replace(
            tzinfo=timezone.utc
        )

    # ------------------------------------------------------
    # Billing cycle
    # ------------------------------------------------------
    #
    # IMPORTANT:
    #
    # If the customer selected an annual plan,
    # the subscription automatically becomes annual.
    #
    # We no longer default everything to monthly.
    # ------------------------------------------------------

    selected_billing_cycle = (
        subscription_data.billing_cycle
        or plan.billing_cycle
    )

    selected_billing_cycle = (
        selected_billing_cycle
        .strip()
        .lower()
    )

    plan_billing_cycle = (
        str(plan.billing_cycle)
        .strip()
        .lower()
    )

    # ------------------------------------------------------
    # Prevent accidental mismatch
    # ------------------------------------------------------

    if (
        subscription_data.billing_cycle
        and selected_billing_cycle
        != plan_billing_cycle
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Billing cycle '{subscription_data.billing_cycle}' "
                f"does not match the selected plan's billing cycle "
                f"'{plan.billing_cycle}'."
            ),
        )

    # ------------------------------------------------------
    # Trial end date
    # ------------------------------------------------------

    end = subscription_data.end_date

    if (
        end is None
        and status_value == "trial"
        and getattr(plan, "trial_days", 0)
    ):
        end = start + timedelta(
            days=plan.trial_days
        )

    # ------------------------------------------------------
    # Create subscription
    # ------------------------------------------------------

    subscription = Subscription(
        customer_id=subscription_data.customer_id,
        plan_id=plan.id,
        start_date=start,
        end_date=end,
        status=status_value,
        billing_cycle=selected_billing_cycle,
    )

    db.add(subscription)

    db.flush()

    # ------------------------------------------------------
    # Start billing cycle
    # ------------------------------------------------------

    start_subscription_billing_cycle(
        db,
        subscription,
    )

    db.commit()

    db.refresh(subscription)

    return subscription


# ==========================================================
# Get Subscription By ID
# ==========================================================


def get_subscription_by_id(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
) -> Subscription:

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

    return subscription


# ==========================================================
# List Subscriptions
# ==========================================================


def list_subscriptions(
    db: Session,
    created_by: int | None = None,
    page: int = 1,
    page_size: int = 10,
    status_filter: str | None = None,
):

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Page must be greater than or equal to 1."
            ),
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Page size must be between 1 and 100."
            ),
        )

    query = db.query(Subscription)

    if status_filter:
        query = query.filter(
            Subscription.status
            == status_filter
        )

    total = query.count()

    subscriptions = (
        query
        .order_by(
            Subscription.id.desc()
        )
        .offset(
            (page - 1) * page_size
        )
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": subscriptions,
    }


# ==========================================================
# Update Subscription
# ==========================================================


def update_subscription(
    db: Session,
    subscription_id: int,
    created_by: int | None,
    subscription_data: SubscriptionUpdate,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    update_data = (
        subscription_data.model_dump(
            exclude_unset=True
        )
    )

    requested_status = update_data.pop(
        "status",
        None,
    )

    # ------------------------------------------------------
    # Plan change through update
    # ------------------------------------------------------

    if "plan_id" in update_data:

        new_plan_id = update_data["plan_id"]

        new_plan = _get_active_plan(
            db,
            new_plan_id,
        )

        update_data["billing_cycle"] = (
            new_plan.billing_cycle
        )

    # ------------------------------------------------------
    # Lifecycle status
    # ------------------------------------------------------

    if requested_status is not None:

        requested_status = (
            requested_status
            .strip()
            .lower()
        )

        current_status = (
            subscription.status
        )

        if requested_status != current_status:

            try:

                if (
                    requested_status
                    == SubscriptionStatus.ACTIVE.value
                ):

                    state_machine_activate(
                        db=db,
                        subscription=subscription,
                        user_id=created_by,
                    )

                elif (
                    requested_status
                    == SubscriptionStatus.PAST_DUE.value
                ):

                    state_machine_mark_past_due(
                        db=db,
                        subscription=subscription,
                        user_id=created_by,
                    )

                elif (
                    requested_status
                    == SubscriptionStatus.PAUSED.value
                ):

                    state_machine_pause(
                        db=db,
                        subscription=subscription,
                        user_id=created_by,
                    )

                elif (
                    requested_status
                    == SubscriptionStatus.CANCELLED.value
                ):

                    state_machine_cancel(
                        db=db,
                        subscription=subscription,
                        user_id=created_by,
                    )

                else:

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Unsupported subscription status "
                            f"'{requested_status}'. "
                            "Use the dedicated lifecycle operations "
                            "for state changes."
                        ),
                    )

            except SubscriptionLifecycleException as error:

                _rollback(db)

                _raise_lifecycle_error(
                    error
                )

    # ------------------------------------------------------
    # Apply remaining fields
    # ------------------------------------------------------

    for field, value in update_data.items():

        if hasattr(
            subscription,
            field,
        ):
            setattr(
                subscription,
                field,
                value,
            )

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Immediate Cancellation
# ==========================================================


def cancel_subscription(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
    reason: str | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        state_machine_cancel(
            db=db,
            subscription=subscription,
            user_id=created_by,
            reason=reason,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    result = _commit_and_refresh(
        db,
        subscription,
    )

    try:

        _issue_unused_period_refund(
            db,
            subscription,
            reason
            or "Unused period refund on cancellation.",
        )

    except Exception:

        _rollback(db)

    return result


# ==========================================================
# Activate Subscription
# ==========================================================


def activate_subscription(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        state_machine_activate(
            db=db,
            subscription=subscription,
            user_id=created_by,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Pause Subscription
# ==========================================================


def pause_subscription(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
    reason: str | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        state_machine_pause(
            db=db,
            subscription=subscription,
            user_id=created_by,
            reason=reason,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Resume Subscription
# ==========================================================


def resume_subscription(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
    reason: str | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        state_machine_resume(
            db=db,
            subscription=subscription,
            user_id=created_by,
            reason=reason,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Mark Subscription Past Due
# ==========================================================


def mark_subscription_past_due(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        state_machine_mark_past_due(
            db=db,
            subscription=subscription,
            user_id=created_by,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Cancel At Period End
# ==========================================================


def cancel_at_period_end(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
    reason: str | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        state_machine_schedule_cancel(
            db=db,
            subscription=subscription,
            user_id=created_by,
            reason=reason,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Process Billing Period End
# ==========================================================


def process_subscription_period_end(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
) -> Subscription:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    try:

        result = state_machine_process_period_end(
            db=db,
            subscription=subscription,
            user_id=created_by,
        )

    except SubscriptionLifecycleException as error:

        _rollback(db)

        _raise_lifecycle_error(
            error
        )

    if result is None:
        return subscription

    return _commit_and_refresh(
        db,
        subscription,
    )


# ==========================================================
# Change Plan With Proration
# ==========================================================


def change_plan_with_proration(
    db: Session,
    subscription_id: int,
    new_plan_id: int,
    created_by: int | None = None,
) -> dict:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    # ------------------------------------------------------
    # Existing plan
    # ------------------------------------------------------

    old_plan = (
        db.query(Plan)
        .filter(
            Plan.id
            == subscription.plan_id
        )
        .first()
    )

    if not old_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current subscription plan not found.",
        )

    # ------------------------------------------------------
    # New selected plan
    # ------------------------------------------------------

    new_plan = _get_active_plan(
        db,
        new_plan_id,
    )

    # ------------------------------------------------------
    # Prevent same-plan change
    # ------------------------------------------------------

    if old_plan.id == new_plan.id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The subscription is already using "
                "this plan."
            ),
        )

    old_plan_id = subscription.plan_id

    remaining_days, total_days = (
        _remaining_days_ratio(
            subscription
        )
    )

    proration_invoice = None

    net_amount = Decimal("0.00")
    old_credit = Decimal("0.00")
    new_charge = Decimal("0.00")

    # ------------------------------------------------------
    # Calculate proration
    # ------------------------------------------------------

    if (
        remaining_days > 0
        and old_plan
    ):

        proration = calculate_proration(
            old_plan_price=Decimal(
                str(old_plan.price)
            ),
            new_plan_price=Decimal(
                str(new_plan.price)
            ),
            remaining_days=remaining_days,
            total_days=total_days,
        )

        old_credit = proration[
            "old_credit"
        ]

        new_charge = proration[
            "new_charge"
        ]

        net_amount = proration[
            "net_amount"
        ]

        # --------------------------------------------------
        # Upgrade
        # --------------------------------------------------

        if net_amount > 0:

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id
                    == subscription.customer_id
                )
                .first()
            )

            country_code = (
                customer.country
                if customer
                and customer.country
                else "IN"
            )

            same_state = (
                country_code
                == str(
                    getattr(
                        settings,
                        "COMPANY_COUNTRY",
                        "IN",
                    )
                ).upper()
                and (
                    getattr(
                        customer,
                        "state",
                        None,
                    )
                    or ""
                )
                .strip()
                .lower()
                ==
                str(
                    getattr(
                        settings,
                        "COMPANY_STATE",
                        "",
                    )
                )
                .strip()
                .lower()
            )

            breakdown = calculate_tax(
                amount=net_amount,
                country_code=country_code,
                tax_rate_percent=None,
                same_state=same_state,
            )

            proration_invoice = Invoice(
                invoice_number=generate_invoice_number(
                    db
                ),
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                amount=breakdown.taxable_amount,
                tax_amount=breakdown.total_tax,
                total_amount=breakdown.total_amount,
                status="pending",
                created_at=datetime.now(
                    timezone.utc
                ),
            )

            db.add(
                proration_invoice
            )

            db.flush()

            db.add(
                InvoiceLineItem(
                    invoice_id=proration_invoice.id,
                    description=(
                        f"Prorated charge: "
                        f"{new_plan.name} "
                        f"({remaining_days} days)"
                    ),
                    item_type="proration_debit",
                    amount=new_charge,
                )
            )

            db.add(
                InvoiceLineItem(
                    invoice_id=proration_invoice.id,
                    description=(
                        f"Unused credit: "
                        f"{old_plan.name} "
                        f"({remaining_days} days)"
                    ),
                    item_type="proration_credit",
                    amount=-old_credit,
                )
            )

            if breakdown.cgst > 0:

                db.add(
                    InvoiceLineItem(
                        invoice_id=proration_invoice.id,
                        description=(
                            f"CGST "
                            f"({breakdown.tax_rate_percent / 2}%)"
                        ),
                        item_type="tax_cgst",
                        amount=breakdown.cgst,
                    )
                )

            if breakdown.sgst > 0:

                db.add(
                    InvoiceLineItem(
                        invoice_id=proration_invoice.id,
                        description=(
                            f"SGST "
                            f"({breakdown.tax_rate_percent / 2}%)"
                        ),
                        item_type="tax_sgst",
                        amount=breakdown.sgst,
                    )
                )

            if breakdown.igst > 0:

                db.add(
                    InvoiceLineItem(
                        invoice_id=proration_invoice.id,
                        description=(
                            f"IGST "
                            f"({breakdown.tax_rate_percent}%)"
                        ),
                        item_type="tax_igst",
                        amount=breakdown.igst,
                    )
                )

            db.flush()

        # --------------------------------------------------
        # Downgrade
        # --------------------------------------------------

        elif net_amount < 0:

            latest_invoice = (
                db.query(Invoice)
                .filter(
                    Invoice.subscription_id
                    == subscription.id,
                    Invoice.status
                    == "paid",
                )
                .order_by(
                    Invoice.id.desc()
                )
                .first()
            )

            if latest_invoice:

                latest_payment = (
                    db.query(Payment)
                    .filter(
                        Payment.invoice_id
                        == latest_invoice.id,
                        Payment.status
                        == "completed",
                    )
                    .order_by(
                        Payment.id.desc()
                    )
                    .first()
                )

                if latest_payment:

                    refund_value = min(
                        abs(net_amount),
                        Decimal(
                            str(
                                latest_payment.amount
                            )
                        ),
                    )

                    from app.services.payment_service import (
                        refund_payment,
                    )

                    refund_payment(
                        db,
                        latest_payment.id,
                        amount=refund_value,
                        reason=(
                            "Proration credit for "
                            f"downgrade to "
                            f"{new_plan.name}."
                        ),
                    )

    # ------------------------------------------------------
    # Update subscription to selected plan
    # ------------------------------------------------------

    subscription.plan_id = new_plan.id

    subscription.billing_cycle = (
        new_plan.billing_cycle
    )

    db.commit()

    db.refresh(
        subscription
    )

    # ------------------------------------------------------
    # Response
    # ------------------------------------------------------

    return {
        "subscription": subscription,
        "previous_plan_id": old_plan_id,
        "new_plan_id": new_plan.id,
        "old_plan_credit": old_credit,
        "new_plan_charge": new_charge,
        "net_amount": net_amount,
        "proration_invoice_id": (
            proration_invoice.id
            if proration_invoice
            else None
        ),
    }


# ==========================================================
# Delete Subscription
# ==========================================================


def delete_subscription(
    db: Session,
    subscription_id: int,
    created_by: int | None = None,
) -> bool:

    subscription = get_subscription_by_id(
        db,
        subscription_id,
        created_by,
    )

    db.delete(
        subscription
    )

    db.commit()

    return True