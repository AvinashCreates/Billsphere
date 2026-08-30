from app.core.database import engine
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    with Session(engine) as db:
        result = db.execute(select(User))
        users = result.scalars().all()
        print(f"Total users: {len(users)}")
        for user in users[:5]:
            print(f"  - {user.email} (role: {user.role}, active: {user.is_active})")
except Exception as e:
    print(f"Error: {e}")
