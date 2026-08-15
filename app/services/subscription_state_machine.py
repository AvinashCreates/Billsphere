"""
BillSphere Subscription State Machine

Production-ready subscription lifecycle management.

Handles:

- Subscription lifecycle transitions
- Transition validation
- Pause / Resume
- Immediate cancellation
- Cancel at period end
- Persistent subscription history
- Audit log creation
- Lifecycle metadata helpers

Lifecycle:

    trial
      |
    active
    /    \
paused   past_due
   |        |
   |        |
   +--------+
      |
  cancelled
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.subscription_history import SubscriptionHistory


# ==========================================================
# Subscription Status
# ==========================================================


class SubscriptionStatus(str, Enum):
    """
    Supported subscription lifecycle statuses.
    """

    TRIAL = "trial"
    ACTIVE = "active"
    PAUSED = "paused"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"


# ==========================================================
# Subscription Actions
# ==========================================================


class SubscriptionAction(str, Enum):
    """
    Business actions that trigger lifecycle transitions.
    """

    CREATE = "create"
    ACTIVATE = "activate"
    PAUSE = "pause"
    RESUME = "resume"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_SUCCESS = "payment_success"
    CANCEL = "cancel"
    CANCEL_AT_PERIOD_END = "cancel_at_period_end"
    EXPIRE = "expire"
    RENEW = "renew"


# ==========================================================
# Exceptions
# ==========================================================


class SubscriptionLifecycleException(Exception):
    """
    Base exception for subscription lifecycle errors.
    """


class InvalidSubscriptionTransition(
    SubscriptionLifecycleException
):
    """
    Raised when an invalid lifecycle transition is requested.
    """


class SubscriptionAlreadyPaused(
    SubscriptionLifecycleException
):
    """
    Raised when an already paused subscription is paused again.
    """


class SubscriptionNotPaused(
    SubscriptionLifecycleException
):
    """
    Raised when resume is requested for a non-paused subscription.
    """


class SubscriptionAlreadyCancelled(
    SubscriptionLifecycleException
):
    """
    Raised when an already cancelled subscription is cancelled.
    """


class SubscriptionAlreadyScheduledForCancellation(
    SubscriptionLifecycleException
):
    """
    Raised when cancellation has already been scheduled.
    """


# ==========================================================
# Transition Result
# ==========================================================


@dataclass(slots=True)
class TransitionResult:
    """
    Result of a successful subscription lifecycle transition.
    """

    previous_status: str
    new_status: str
    action: str
    changed_at: datetime
    message: str


# ==========================================================
# Allowed Transition Map
# ==========================================================


_ALLOWED_TRANSITIONS: dict[
    SubscriptionStatus,
    set[SubscriptionStatus],
] = {
    SubscriptionStatus.TRIAL: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED,
    },

    SubscriptionStatus.ACTIVE: {
        SubscriptionStatus.PAUSED,
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.CANCELLED,
    },

    SubscriptionStatus.PAUSED: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED,
    },

    SubscriptionStatus.PAST_DUE: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED,
    },

    SubscriptionStatus.CANCELLED: set(),
}


# ==========================================================
# Date / Status Helpers
# ==========================================================


def utc_now() -> datetime:
    """
    Return the current timezone-aware UTC timestamp.
    """

    return datetime.now(timezone.utc)


def normalize_status(
    value: str | SubscriptionStatus,
) -> SubscriptionStatus:
    """
    Normalize a subscription status into SubscriptionStatus.

    Raises
    ------
    InvalidSubscriptionTransition
        If the status is unknown.
    """

    if isinstance(value, SubscriptionStatus):
        return value

    if not isinstance(value, str):
        raise InvalidSubscriptionTransition(
            f"Invalid subscription status type: "
            f"{type(value).__name__}."
        )

    normalized_value = value.strip().lower()

    try:
        return SubscriptionStatus(normalized_value)

    except ValueError as error:
        raise InvalidSubscriptionTransition(
            f"Unknown subscription status: "
            f"'{value}'."
        ) from error


# ==========================================================
# Transition Validation
# ==========================================================


def can_transition(
    current: str | SubscriptionStatus,
    target: str | SubscriptionStatus,
) -> bool:
    """
    Return True when the requested transition is valid.
    """

    current_status = normalize_status(current)
    target_status = normalize_status(target)

    return target_status in _ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )


def validate_transition(
    current: str | SubscriptionStatus,
    target: str | SubscriptionStatus,
) -> None:
    """
    Validate a lifecycle transition.

    Raises
    ------
    InvalidSubscriptionTransition
        If the requested transition is not allowed.
    """

    current_status = normalize_status(current)
    target_status = normalize_status(target)

    if not can_transition(
        current_status,
        target_status,
    ):
        raise InvalidSubscriptionTransition(
            f"Cannot transition subscription "
            f"from '{current_status.value}' "
            f"to '{target_status.value}'."
        )


# ==========================================================
# Audit Log
# ==========================================================


def create_audit_log(
    db: Session,
    *,
    user_id: int | None,
    subscription: Subscription,
    action: str,
    description: str,
) -> AuditLog:
    """
    Create an audit log entry for a subscription action.

    The caller is responsible for committing the transaction.
    """

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        module="subscriptions",
        description=description,
        entity_id=subscription.id,
        entity_type="subscription",
    )

    db.add(audit_log)

    return audit_log


# ==========================================================
# Subscription History
# ==========================================================


def create_subscription_history(
    db: Session,
    *,
    subscription: Subscription,
    previous_status: str,
    new_status: str,
    action: str,
    user_id: int | None,
    reason: str | None = None,
) -> SubscriptionHistory:
    """
    Persist a subscription lifecycle transition.

    The caller is responsible for committing the transaction.
    """

    history = SubscriptionHistory(
        subscription_id=subscription.id,
        user_id=user_id,
        previous_status=previous_status,
        new_status=new_status,
        action=action,
        reason=reason,
    )

    db.add(history)

    return history


def build_history_entry(
    *,
    old_status: str,
    new_status: str,
    action: str,
    user_id: int | None,
) -> dict[str, Any]:
    """
    Build an in-memory lifecycle history representation.
    """

    return {
        "previous_status": old_status,
        "new_status": new_status,
        "action": action,
        "performed_by": user_id,
        "performed_at": utc_now().isoformat(),
    }


# ==========================================================
# Main Transition Engine
# ==========================================================


def transition(
    db: Session,
    *,
    subscription: Subscription,
    target_status: str | SubscriptionStatus,
    action: str | SubscriptionAction,
    user_id: int | None = None,
    description: str | None = None,
    reason: str | None = None,
) -> TransitionResult:
    """
    Execute a validated subscription lifecycle transition.

    The function:

    1. Validates the requested transition.
    2. Updates subscription status.
    3. Updates lifecycle timestamps.
    4. Creates subscription history.
    5. Creates audit log.
    6. Leaves transaction commit responsibility to
       the calling service layer.
    """

    old_status = normalize_status(
        subscription.status,
    )

    new_status = normalize_status(
        target_status,
    )

    # ------------------------------------------------------
    # Validate transition
    # ------------------------------------------------------

    validate_transition(
        old_status,
        new_status,
    )

    now = utc_now()

    action_value = (
        action.value
        if isinstance(action, SubscriptionAction)
        else str(action)
    )

    # ------------------------------------------------------
    # Update subscription status
    # ------------------------------------------------------

    subscription.status = new_status.value

    # ------------------------------------------------------
    # Lifecycle metadata
    # ------------------------------------------------------

    if new_status == SubscriptionStatus.ACTIVE:
        subscription.resumed_at = now

    elif new_status == SubscriptionStatus.PAUSED:
        subscription.paused_at = now

    elif new_status == SubscriptionStatus.CANCELLED:
        subscription.cancelled_at = now
        subscription.end_date = now
        subscription.cancel_at_period_end = False

    # ------------------------------------------------------
    # Persistent subscription history
    # ------------------------------------------------------

    create_subscription_history(
        db,
        subscription=subscription,
        previous_status=old_status.value,
        new_status=new_status.value,
        action=action_value,
        user_id=user_id,
        reason=reason,
    )

    # ------------------------------------------------------
    # Audit log
    # ------------------------------------------------------

    audit_description = (
        description
        or (
            f"Subscription transitioned "
            f"from '{old_status.value}' "
            f"to '{new_status.value}'."
        )
    )

    create_audit_log(
        db,
        user_id=user_id,
        subscription=subscription,
        action=action_value,
        description=audit_description,
    )

    # ------------------------------------------------------
    # Return transition result
    # ------------------------------------------------------

    return TransitionResult(
        previous_status=old_status.value,
        new_status=new_status.value,
        action=action_value,
        changed_at=now,
        message=(
            "Subscription transition completed "
            "successfully."
        ),
    )


# ==========================================================
# Lifecycle Operations
# ==========================================================


def pause_subscription(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
    reason: str | None = None,
) -> TransitionResult:
    """
    Pause an active subscription.
    """

    if subscription.status == (
        SubscriptionStatus.PAUSED.value
    ):
        raise SubscriptionAlreadyPaused(
            "Subscription is already paused."
        )

    return transition(
        db=db,
        subscription=subscription,
        target_status=SubscriptionStatus.PAUSED,
        action=SubscriptionAction.PAUSE,
        user_id=user_id,
        reason=reason,
        description="Subscription paused.",
    )


def resume_subscription(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
    reason: str | None = None,
) -> TransitionResult:
    """
    Resume a paused subscription.
    """

    if subscription.status != (
        SubscriptionStatus.PAUSED.value
    ):
        raise SubscriptionNotPaused(
            "Subscription is not paused."
        )

    return transition(
        db=db,
        subscription=subscription,
        target_status=SubscriptionStatus.ACTIVE,
        action=SubscriptionAction.RESUME,
        user_id=user_id,
        reason=reason,
        description="Subscription resumed.",
    )


def activate_subscription(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
) -> TransitionResult:
    """
    Activate a trial or past-due subscription.

    Valid transitions:

        trial -> active
        past_due -> active
    """

    return transition(
        db=db,
        subscription=subscription,
        target_status=SubscriptionStatus.ACTIVE,
        action=SubscriptionAction.ACTIVATE,
        user_id=user_id,
        description="Subscription activated.",
    )


def mark_past_due(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
) -> TransitionResult:
    """
    Mark an active subscription as past_due.
    """

    return transition(
        db=db,
        subscription=subscription,
        target_status=SubscriptionStatus.PAST_DUE,
        action=SubscriptionAction.PAYMENT_FAILED,
        user_id=user_id,
        description=(
            "Payment failed. "
            "Subscription marked as past_due."
        ),
    )


def cancel_subscription(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
    reason: str | None = None,
) -> TransitionResult:
    """
    Immediately cancel a subscription.
    """

    if subscription.status == (
        SubscriptionStatus.CANCELLED.value
    ):
        raise SubscriptionAlreadyCancelled(
            "Subscription has already been cancelled."
        )

    return transition(
        db=db,
        subscription=subscription,
        target_status=SubscriptionStatus.CANCELLED,
        action=SubscriptionAction.CANCEL,
        user_id=user_id,
        reason=reason,
        description="Subscription cancelled immediately.",
    )


def schedule_cancel_at_period_end(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
    reason: str | None = None,
) -> TransitionResult:
    """
    Schedule cancellation at the end of the current
    billing period.

    This does not immediately change the subscription
    lifecycle status.

    The subscription remains in its current lifecycle state
    until the billing period ends.
    """

    if subscription.status == (
        SubscriptionStatus.CANCELLED.value
    ):
        raise SubscriptionAlreadyCancelled(
            "Cancelled subscription cannot be scheduled "
            "for cancellation."
        )

    if subscription.cancel_at_period_end:
        raise SubscriptionAlreadyScheduledForCancellation(
            "Subscription is already scheduled "
            "for cancellation."
        )

    now = utc_now()

    previous_status = normalize_status(
        subscription.status,
    ).value

    # ------------------------------------------------------
    # Schedule cancellation
    # ------------------------------------------------------

    subscription.cancel_at_period_end = True

    # ------------------------------------------------------
    # Persistent history
    #
    # Scheduling does not change lifecycle status.
    #
    # Example:
    #
    # active -> active
    # ------------------------------------------------------

    create_subscription_history(
        db,
        subscription=subscription,
        previous_status=previous_status,
        new_status=previous_status,
        action=(
            SubscriptionAction
            .CANCEL_AT_PERIOD_END
            .value
        ),
        user_id=user_id,
        reason=reason,
    )

    # ------------------------------------------------------
    # Audit log
    # ------------------------------------------------------

    create_audit_log(
        db,
        user_id=user_id,
        subscription=subscription,
        action=(
            SubscriptionAction
            .CANCEL_AT_PERIOD_END
            .value
        ),
        description=(
            "Subscription scheduled for cancellation "
            "at the end of the current billing period."
        ),
    )

    return TransitionResult(
        previous_status=previous_status,
        new_status=previous_status,
        action=(
            SubscriptionAction
            .CANCEL_AT_PERIOD_END
            .value
        ),
        changed_at=now,
        message=(
            "Subscription cancellation scheduled "
            "for the end of the billing period."
        ),
    )


def process_period_end(
    db: Session,
    *,
    subscription: Subscription,
    user_id: int | None = None,
) -> TransitionResult | None:
    """
    Cancel a subscription when its billing period ends.

    Intended for use by the billing scheduler.
    """

    if not subscription.cancel_at_period_end:
        return None

    return cancel_subscription(
        db=db,
        subscription=subscription,
        user_id=user_id,
        reason="Billing period ended.",
    )


# ==========================================================
# Status Helpers
# ==========================================================


def is_trial(
    subscription: Subscription,
) -> bool:
    """
    Return True when subscription is in trial.
    """

    return (
        subscription.status
        == SubscriptionStatus.TRIAL.value
    )


def is_active(
    subscription: Subscription,
) -> bool:
    """
    Return True when subscription is active.
    """

    return (
        subscription.status
        == SubscriptionStatus.ACTIVE.value
    )


def is_paused(
    subscription: Subscription,
) -> bool:
    """
    Return True when subscription is paused.
    """

    return (
        subscription.status
        == SubscriptionStatus.PAUSED.value
    )


def is_past_due(
    subscription: Subscription,
) -> bool:
    """
    Return True when subscription is past_due.
    """

    return (
        subscription.status
        == SubscriptionStatus.PAST_DUE.value
    )


def is_cancelled(
    subscription: Subscription,
) -> bool:
    """
    Return True when subscription is cancelled.
    """

    return (
        subscription.status
        == SubscriptionStatus.CANCELLED.value
    )


def ensure_not_cancelled(
    subscription: Subscription,
) -> None:
    """
    Ensure subscription is not cancelled.
    """

    if is_cancelled(subscription):
        raise SubscriptionAlreadyCancelled(
            "Subscription has already been cancelled."
        )


# ==========================================================
# Transition Map
# ==========================================================


def allowed_transitions() -> dict[
    SubscriptionStatus,
    set[SubscriptionStatus],
]:
    """
    Return a copy of the allowed transition map.
    """

    return {
        subscription_status: transitions.copy()
        for subscription_status, transitions
        in _ALLOWED_TRANSITIONS.items()
    }