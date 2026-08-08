from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User



from app.services.customer_service import (
    fetch_all_customers,
    fetch_customer,
)

from app.schemas.customer import (
    CustomerResponse,
    CustomerListResponse,
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get(
    "/",
    response_model=CustomerListResponse
)
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    customers = fetch_all_customers(db)

    return {
        "customers": customers,
        "total_customers": len(customers)
    }

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    customer = fetch_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer