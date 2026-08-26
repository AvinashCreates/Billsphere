from typing import Optional
from pydantic import BaseModel


class UserMeResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    profile_picture: Optional[str] = None


class UsernameUpdateRequest(BaseModel):
    username: str