from app.database.database import SessionLocal
from app.models.user import User
from app.models.customer import Customer
from app.models.subscription import Subscription

db = SessionLocal()

email = "gyathrigayathri2007@gmail.com"

# 1. Find customer record
customer = db.query(Customer).filter(Customer.email == email).first()
if customer:
    # Delete associated subscriptions first to maintain FK integrity
    db.query(Subscription).filter(Subscription.customer_id == customer.id).delete()
    db.delete(customer)

# 2. Find user record
user = db.query(User).filter(User.email == email).first()
if user:
    db.delete(user)

db.commit()
print("Cleanup completed for:", email)
db.close()