from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/")
def get_customers(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Customer API working",
        "logged_in_user": current_user.username
    }