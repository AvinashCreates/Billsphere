from app.database.database import SessionLocal
from app.models.user import User

db = SessionLocal()

email = "gyathrigayathri2007@gmail.com"

user = db.query(User).filter(User.email == email).first()

if user:
    db.delete(user)
    db.commit()
    print("Deleted successfully")
else:
    print("User not found")

db.close()