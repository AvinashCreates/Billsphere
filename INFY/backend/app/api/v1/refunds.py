"""
BillSphere Refunds API

Endpoints:
- GET /refunds - List all refunds
- POST /refunds - Create a refund
- GET /refunds/{refund_id} - Get specific refund details
"""

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.dependencies import (
    database_session,
    get_current_user_token,
)

from app.models.payment import Payment
from app.models.invoice import Invoice
from app.schemas.payment import (
    PaymentRefundRequest,
    PaymentResponse,
)

from app.services.payment_service import (
    refund_payment,
)

# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"],
)


# ==========================================================
# List Refunds
# ==========================================================

@router.get("")
def list_refunds(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number.",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of refunds per page.",
    ),
    status_filter: str | None = Query(
        default=None,
        description="Filter by refund status (refunded, partially_refunded).",
    ),
    db: Session = Depends(database_session),
    current_user: dict = Depends(get_current_user_token),
):
    """
    Get paginated list of refunds with refund reason and status.
    """

    owner_id = int(current_user["sub"])

    # Query payments that have been refunded
    query = db.query(Payment).filter(
        and_(
            Payment.owner_id == owner_id,
            Payment.refunded_amount > 0,
            Payment.refund_reason.isnot(None),
        )
    )

    if status_filter:
        query = query.filter(Payment.status == status_filter)

    total = query.count()

    refunds = (
        query
        .order_by(Payment.refunded_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": refund.id,
                "payment_id": refund.id,
                "invoice_id": refund.invoice_id,
                "amount": refund.amount,
                "refunded_amount": refund.refunded_amount,
                "refund_reason": refund.refund_reason,
                "refund_status": refund.status,
                "refunded_at": refund.refunded_at,
                "created_at": refund.created_at,
            }
            for refund in refunds
        ],
    }


# ==========================================================
# Create Refund
# ==========================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_refund(
    request: PaymentRefundRequest,
    payment_id: int = Query(
        ...,
        description="Payment ID to refund.",
    ),
    db: Session = Depends(database_session),
    current_user: dict = Depends(get_current_user_token),
):
    """
    Create a refund for a payment.
    
    Request body should include:
    - amount (optional, defaults to full payment amount)
    - reason (required)
    """

    owner_id = int(current_user["sub"])

    # Verify payment exists and belongs to user
    payment = db.query(Payment).filter(
        and_(
            Payment.id == payment_id,
            Payment.owner_id == owner_id,
        )
    ).first()

    if not payment:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # Process refund
    refunded_payment = refund_payment(
        db=db,
        payment_id=payment_id,
        amount=request.amount,
        reason=request.reason,
        owner_id=owner_id,
    )

    return {
        "id": refunded_payment.id,
        "payment_id": refunded_payment.id,
        "invoice_id": refunded_payment.invoice_id,
        "amount": refunded_payment.amount,
        "refunded_amount": refunded_payment.refunded_amount,
        "refund_reason": refunded_payment.refund_reason,
        "refund_status": refunded_payment.status,
        "refunded_at": refunded_payment.refunded_at,
        "created_at": refunded_payment.created_at,
        "message": "Refund processed successfully",
    }


# ==========================================================
# Get Refund Details
# ==========================================================

@router.get("/{refund_id}")
def get_refund_details(
    refund_id: int,
    db: Session = Depends(database_session),
    current_user: dict = Depends(get_current_user_token),
):
    """
    Get detailed information about a specific refund.
    """

    owner_id = int(current_user["sub"])

    refund = db.query(Payment).filter(
        and_(
            Payment.id == refund_id,
            Payment.owner_id == owner_id,
            Payment.refunded_amount > 0,
        )
    ).first()

    if not refund:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found",
        )

    # Get associated invoice
    invoice = db.query(Invoice).filter(
        Invoice.id == refund.invoice_id
    ).first()

    return {
        "id": refund.id,
        "payment_id": refund.id,
        "invoice_id": refund.invoice_id,
        "invoice_number": invoice.invoice_number if invoice else None,
        "amount": refund.amount,
        "refunded_amount": refund.refunded_amount,
        "refund_reason": refund.refund_reason,
        "refund_status": refund.status,
        "refunded_at": refund.refunded_at,
        "created_at": refund.created_at,
        "updated_at": refund.updated_at,
    }
