"""
BillSphere Customer Service

Business logic layer for customer management.

Handles:
- Creating customers
- Fetching customers
- Searching customers
- Updating customers
- Deactivating customers
"""

from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.models.customer import Customer
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
)


# ==========================================================
# Get Customer By ID
# ==========================================================

def get_customer_by_id(
    db: Session,
    customer_id: int,
    owner_id: int,
) -> Customer | None:
    """
    Fetch customer by ID belonging to owner.
    """

    statement = select(Customer).where(
        Customer.id == customer_id,
        Customer.owner_id == owner_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


# ==========================================================
# Get Customer By Email
# ==========================================================

def get_customer_by_email(
    db: Session,
    email: str,
    owner_id: int,
) -> Customer | None:
    """
    Fetch customer using email.
    """

    statement = select(Customer).where(
        Customer.email == email,
        Customer.owner_id == owner_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


# ==========================================================
# Create Customer
# ==========================================================

def create_customer(
    db: Session,
    customer_data: CustomerCreate,
    owner_id: int,
) -> Customer:
    """
    Create a new customer.
    """

    existing_customer = get_customer_by_email(
        db,
        customer_data.email,
        owner_id,
    )


    if existing_customer:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer email already exists",
        )


    customer = Customer(
        **customer_data.model_dump(),
        owner_id=owner_id,
    )


    db.add(customer)

    db.commit()

    db.refresh(customer)


    return customer


# ==========================================================
# List Customers
# ==========================================================

def list_customers(
    db: Session,
    owner_id: int,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
):
    """
    Return paginated customer list.
    """

    query = select(Customer).where(
        Customer.owner_id == owner_id,
        Customer.is_active.is_(True),
    )


    if search:

        search_filter = f"%{search}%"

        query = query.where(
            or_(
                Customer.company_name.ilike(
                    search_filter
                ),

                Customer.contact_name.ilike(
                    search_filter
                ),

                Customer.email.ilike(
                    search_filter
                ),
            )
        )


    offset = (
        page - 1
    ) * page_size


    query = query.offset(
        offset
    ).limit(
        page_size
    )


    result = db.execute(query)


    customers = result.scalars().all()


    count_query = select(
        Customer
    ).where(
        Customer.owner_id == owner_id,
        Customer.is_active.is_(True),
    )


    total = len(
        db.execute(count_query)
        .scalars()
        .all()
    )


    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "customers": customers,
    }


def list_admin_customers(
    db: Session,
    payment_status: str | None = None,
    platform: str | None = None,
    plan_type: str | None = None,
) -> list[dict]:
    """Return registered customer accounts with their current billing data."""

    users = (
        db.query(User)
        .filter(User.role.ilike("customer"))
        .order_by(User.created_at.desc())
        .all()
    )

    rows: list[dict] = []
    for user in users:
        customer = (
            db.query(Customer)
            .filter(Customer.owner_id == user.id, Customer.is_active.is_(True))
            .order_by(Customer.created_at.desc())
            .first()
        )
        subscription = None
        if customer:
            subscription = (
                db.query(Subscription)
                .filter(Subscription.customer_id == customer.id)
                .order_by(Subscription.start_date.desc())
                .first()
            )

        plan = db.get(Plan, subscription.plan_id) if subscription else None
        status_value = (
            "paid" if subscription and subscription.status == "active"
            else subscription.status if subscription else "none"
        )

        row = {
            "id": user.id,
            "customer_id": customer.id if customer else None,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "billing_country": customer.country if customer and customer.country else "-",
            "created_at": user.created_at,
            "platform": plan.platform if plan else None,
            "plan_type": subscription.billing_cycle if subscription else None,
            "payment_status": status_value,
            "current_period_end": subscription.current_period_end if subscription else None,
            "trial_ends_at": subscription.end_date if subscription and subscription.status == "trial" else None,
        }

        if payment_status and status_value != payment_status:
            continue
        if platform and row["platform"] != platform:
            continue
        if plan_type and row["plan_type"] != plan_type:
            continue
        rows.append(row)

    return rows


# ==========================================================
# Update Customer
# ==========================================================

def update_customer(
    db: Session,
    customer_id: int,
    owner_id: int,
    customer_data: CustomerUpdate,
) -> Customer:
    """
    Update existing customer.
    """

    customer = get_customer_by_id(
        db,
        customer_id,
        owner_id,
    )


    if not customer:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )


    update_data = customer_data.model_dump(
        exclude_unset=True
    )


    for key, value in update_data.items():

        setattr(
            customer,
            key,
            value,
        )


    db.commit()

    db.refresh(customer)


    return customer


# ==========================================================
# Delete Customer
# ==========================================================

def delete_customer(
    db: Session,
    customer_id: int,
    owner_id: int,
) -> None:
    """
    Soft delete customer.

    Customer data remains in database.
    """

    customer = get_customer_by_id(
        db,
        customer_id,
        owner_id,
    )


    if not customer:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )


    customer.is_active = False


    db.commit()