from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User

from app.services.customer_service import (
    fetch_all_customers,
    fetch_customer,
    create_customer,
    update_customer,
    delete_customer,
)

from app.schemas.customer import (
    CustomerResponse,
    CustomerListResponse,
    CustomerCreate,
    CustomerUpdate,
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
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by username or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    customers, total = fetch_all_customers(db, page=page, page_size=page_size, search=search)

    total_pages = (total + page_size - 1) // page_size if total else 1

    return {
        "customers": customers,
        "total_customers": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
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


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return create_customer(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_existing_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        updated = update_customer(
            db,
            customer_id=customer_id,
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if updated is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return updated


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        deleted = delete_customer(db, customer_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")

    return None
