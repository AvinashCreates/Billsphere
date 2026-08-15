"""
BillSphere Plan Service

Business logic for subscription plan management.

Handles:
- Creating plans
- Fetching plans
- Filtering plans by platform
- Searching plans
- Updating plans
- Deactivating plans
"""

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy import (
    func,
    or_,
    select,
)

from sqlalchemy.orm import Session

from app.models.plan import Plan

from app.schemas.plan import (
    PlanCreate,
    PlanUpdate,
)


# ==========================================================
# Get Plan By ID
# ==========================================================

def get_plan_by_id(
    db: Session,
    plan_id: int,
) -> Plan | None:
    """
    Fetch a plan using its primary key.
    """

    statement = (
        select(Plan)
        .where(
            Plan.id == plan_id,
        )
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


# ==========================================================
# Get Plan By Name
# ==========================================================

def get_plan_by_name(
    db: Session,
    name: str,
    platform: str | None = None,
) -> Plan | None:
    """
    Fetch a plan by name.

    If platform is supplied, the plan is searched
    within that platform.

    This allows:

        Amazon + Basic
        Netflix + Basic

    to coexist.
    """

    statement = (
        select(Plan)
        .where(
            Plan.name == name,
        )
    )

    if platform:

        statement = statement.where(
            func.lower(Plan.platform)
            == platform.lower()
        )

    result = db.execute(statement)

    return result.scalar_one_or_none()


# ==========================================================
# Create Plan
# ==========================================================

def create_plan(
    db: Session,
    plan_data: PlanCreate,
    created_by: int,
) -> Plan:
    """
    Create a new subscription plan.
    """

    # ------------------------------------------------------
    # Normalize platform and name
    # ------------------------------------------------------

    platform = plan_data.platform.strip()

    name = plan_data.name.strip()

    # ------------------------------------------------------
    # Validate platform
    # ------------------------------------------------------

    if not platform:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform is required.",
        )

    # ------------------------------------------------------
    # Validate plan name
    # ------------------------------------------------------

    if not name:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan name is required.",
        )

    # ------------------------------------------------------
    # Check duplicate plan inside same platform
    # ------------------------------------------------------

    existing_plan = get_plan_by_name(
        db=db,
        name=name,
        platform=platform,
    )

    if existing_plan:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Plan '{name}' already exists "
                f"for platform '{platform}'."
            ),
        )

    # ------------------------------------------------------
    # Create plan
    # ------------------------------------------------------

    plan = Plan(
        platform=platform,
        name=name,
        description=plan_data.description,
        price=plan_data.price,
        currency=plan_data.currency.upper(),
        billing_cycle=plan_data.billing_cycle.lower(),
        trial_days=plan_data.trial_days,
        feature_entitlements=(
            plan_data.feature_entitlements
        ),
        max_customers=plan_data.max_customers,
        max_invoices=plan_data.max_invoices,
        created_by=created_by,
        is_active=True,
    )

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    db.add(plan)

    db.commit()

    db.refresh(plan)

    return plan


# ==========================================================
# List Plans
# ==========================================================

def list_plans(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    platform: str | None = None,
):
    """
    Return paginated active plans.

    Supported filters:

        platform
        search

    Examples:

        All plans:
            GET /api/v1/plans

        Amazon plans:
            GET /api/v1/plans?platform=Amazon

        Amazon Basic:
            GET /api/v1/plans?platform=Amazon&search=Basic
    """

    # ------------------------------------------------------
    # Base query
    # ------------------------------------------------------

    query = (
        select(Plan)
        .where(
            Plan.is_active.is_(True)
        )
    )

    # ------------------------------------------------------
    # Platform filter
    # ------------------------------------------------------

    if platform:

        platform_value = (
            platform.strip().lower()
        )

        query = query.where(
            func.lower(Plan.platform)
            == platform_value
        )

    # ------------------------------------------------------
    # Search filter
    # ------------------------------------------------------

    if search:

        search_value = (
            f"%{search.strip()}%"
        )

        query = query.where(
            or_(
                Plan.name.ilike(
                    search_value
                ),

                Plan.description.ilike(
                    search_value
                ),

                Plan.platform.ilike(
                    search_value
                ),
            )
        )

    # ------------------------------------------------------
    # Order plans
    # ------------------------------------------------------
    #
    # Cheapest plan first.
    #
    # This gives the frontend:
    #
    # Basic
    # Standard
    # Premium
    #
    # when prices are configured accordingly.
    # ------------------------------------------------------

    query = query.order_by(
        Plan.price.asc()
    )

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    offset = (
        page - 1
    ) * page_size

    query = (
        query
        .offset(offset)
        .limit(page_size)
    )

    # ------------------------------------------------------
    # Execute plans query
    # ------------------------------------------------------

    result = db.execute(query)

    plans = result.scalars().all()

    # ------------------------------------------------------
    # Total count
    # ------------------------------------------------------

    count_statement = (
        select(
            func.count(Plan.id)
        )
        .where(
            Plan.is_active.is_(True)
        )
    )

    # ------------------------------------------------------
    # Apply same platform filter to count
    # ------------------------------------------------------

    if platform:

        platform_value = (
            platform.strip().lower()
        )

        count_statement = count_statement.where(
            func.lower(Plan.platform)
            == platform_value
        )

    # ------------------------------------------------------
    # Apply same search filter to count
    # ------------------------------------------------------

    if search:

        search_value = (
            f"%{search.strip()}%"
        )

        count_statement = count_statement.where(
            or_(
                Plan.name.ilike(
                    search_value
                ),

                Plan.description.ilike(
                    search_value
                ),

                Plan.platform.ilike(
                    search_value
                ),
            )
        )

    total = db.execute(
        count_statement
    ).scalar_one()

    # ------------------------------------------------------
    # Return
    # ------------------------------------------------------

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "plans": plans,
    }


# ==========================================================
# Update Plan
# ==========================================================

def update_plan(
    db: Session,
    plan_id: int,
    plan_data: PlanUpdate,
) -> Plan:
    """
    Update an existing subscription plan.
    """

    # ------------------------------------------------------
    # Find plan
    # ------------------------------------------------------

    plan = get_plan_by_id(
        db=db,
        plan_id=plan_id,
    )

    if not plan:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    # ------------------------------------------------------
    # Get only supplied fields
    # ------------------------------------------------------

    update_data = plan_data.model_dump(
        exclude_unset=True,
    )

    # ------------------------------------------------------
    # Normalize platform
    # ------------------------------------------------------

    if (
        "platform" in update_data
        and update_data["platform"] is not None
    ):

        platform = (
            update_data["platform"].strip()
        )

        if not platform:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform cannot be empty.",
            )

        update_data["platform"] = platform

    # ------------------------------------------------------
    # Normalize name
    # ------------------------------------------------------

    if (
        "name" in update_data
        and update_data["name"] is not None
    ):

        name = (
            update_data["name"].strip()
        )

        if not name:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan name cannot be empty.",
            )

        update_data["name"] = name

    # ------------------------------------------------------
    # Normalize currency
    # ------------------------------------------------------

    if (
        "currency" in update_data
        and update_data["currency"] is not None
    ):

        update_data["currency"] = (
            update_data["currency"]
            .strip()
            .upper()
        )

    # ------------------------------------------------------
    # Normalize billing cycle
    # ------------------------------------------------------

    if (
        "billing_cycle" in update_data
        and update_data["billing_cycle"] is not None
    ):

        update_data["billing_cycle"] = (
            update_data["billing_cycle"]
            .strip()
            .lower()
        )

    # ------------------------------------------------------
    # Determine final platform and name
    # ------------------------------------------------------

    final_platform = update_data.get(
        "platform",
        plan.platform,
    )

    final_name = update_data.get(
        "name",
        plan.name,
    )

    # ------------------------------------------------------
    # Check duplicate platform + plan name
    # ------------------------------------------------------

    duplicate_plan = get_plan_by_name(
        db=db,
        name=final_name,
        platform=final_platform,
    )

    if (
        duplicate_plan
        and duplicate_plan.id != plan.id
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Plan '{final_name}' already exists "
                f"for platform '{final_platform}'."
            ),
        )

    # ------------------------------------------------------
    # Apply changes
    # ------------------------------------------------------

    for key, value in update_data.items():

        setattr(
            plan,
            key,
            value,
        )

    # ------------------------------------------------------
    # Save changes
    # ------------------------------------------------------

    db.commit()

    db.refresh(plan)

    return plan


# ==========================================================
# Delete Plan
# ==========================================================

def delete_plan(
    db: Session,
    plan_id: int,
) -> None:
    """
    Soft delete a plan.

    The plan remains in the database but will no longer
    appear in active plan listings.
    """

    # ------------------------------------------------------
    # Find plan
    # ------------------------------------------------------

    plan = get_plan_by_id(
        db=db,
        plan_id=plan_id,
    )

    if not plan:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    # ------------------------------------------------------
    # Soft delete
    # ------------------------------------------------------

    plan.is_active = False

    db.commit()