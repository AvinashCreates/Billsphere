import os
from datetime import datetime, timedelta, timezone
from app.database.database import SessionLocal
from app.models.user import User
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.core.security import hash_password
from app.workers.email_tasks import (
    send_welcome_email,
    send_customer_invite_email,
    send_trial_activated_email,
    send_subscription_confirmation,
    send_cancellation_email,
    send_reactivation_email,
    send_past_due_email,
    send_deadline_reminder,
)

TARGET_EMAIL = "gyathrigayathri2007@gmail.com"
TARGET_NAME = "Gayathri"

def seed_demo_data():
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    print(f"[SEED] Seeding demo subscriptions for: {TARGET_EMAIL} ...")

    # 1. Ensure User exists
    user = db.query(User).filter(User.email == TARGET_EMAIL).first()
    if not user:
        user = User(
            email=TARGET_EMAIL,
            hashed_password=hash_password("password123"),
            role="customer",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Ensure Customer exists
    customer = db.query(Customer).filter(Customer.email == TARGET_EMAIL).first()
    if not customer:
        customer = Customer(
            name=TARGET_NAME,
            email=TARGET_EMAIL,
            billing_country="IN",
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # 3. Ensure Plans exist
    plans_data = [
        {"name": "Netflix Premium", "price": 19.99, "billing_interval": "monthly", "trial_period_days": 0},
        {"name": "Spotify Duo", "price": 12.99, "billing_interval": "monthly", "trial_period_days": 7},
        {"name": "Prime Video", "price": 8.99, "billing_interval": "monthly", "trial_period_days": 0},
        {"name": "Disney+", "price": 13.99, "billing_interval": "monthly", "trial_period_days": 0},
        {"name": "HBO Max", "price": 15.99, "billing_interval": "monthly", "trial_period_days": 0},
    ]

    db_plans = {}
    for p in plans_data:
        plan = db.query(Plan).filter(Plan.name == p["name"]).first()
        if not plan:
            plan = Plan(**p, status="active")
            db.add(plan)
            db.commit()
            db.refresh(plan)
        db_plans[p["name"]] = plan

    # 4. Clear old test subscriptions for this customer
    db.query(Subscription).filter(Subscription.customer_id == customer.id).delete()
    db.commit()

    # 5. Create specific scenario subscriptions
    test_subs = [
        # Scenario 1: Near Deadline (3 days left) — triggers Celery Beat 3-day reminder
        Subscription(
            customer_id=customer.id,
            plan_id=db_plans["Netflix Premium"].id,
            status="active",
            trial_ends_at=None,
            current_period_start=now - timedelta(days=27),
            current_period_end=now + timedelta(days=3),
            cancel_at_period_end=False,
        ),
        # Scenario 2: Near Deadline (1 day left) — triggers Celery Beat 1-day reminder
        Subscription(
            customer_id=customer.id,
            plan_id=db_plans["Spotify Duo"].id,
            status="trial",
            trial_ends_at=now + timedelta(days=1),
            current_period_start=now - timedelta(days=6),
            current_period_end=now + timedelta(days=1),
            cancel_at_period_end=False,
        ),
        # Scenario 3: Expired Deadline (ended 2 days ago) — triggers Celery Beat process_due_subscriptions
        Subscription(
            customer_id=customer.id,
            plan_id=db_plans["Prime Video"].id,
            status="active",
            trial_ends_at=None,
            current_period_start=now - timedelta(days=32),
            current_period_end=now - timedelta(days=2),
            cancel_at_period_end=False,
        ),
        # Scenario 4: Already Past Due — for testing "Renew Now" button on Dashboard
        Subscription(
            customer_id=customer.id,
            plan_id=db_plans["Disney+"].id,
            status="past_due",
            trial_ends_at=None,
            current_period_start=now - timedelta(days=35),
            current_period_end=now - timedelta(days=5),
            cancel_at_period_end=False,
        ),
        # Scenario 5: Pending / Queued Plan — for testing Pending Section on Dashboard
        Subscription(
            customer_id=customer.id,
            plan_id=db_plans["HBO Max"].id,
            status="pending",
            trial_ends_at=None,
            current_period_start=now + timedelta(days=3),
            current_period_end=now + timedelta(days=33),
            cancel_at_period_end=False,
        ),
    ]

    for sub in test_subs:
        db.add(sub)
    db.commit()

    print("[SUCCESS] Successfully created 5 demo subscriptions in Database:")
    print("   1. Netflix Premium  -> ACTIVE (Ends in 3 days) [Near Deadline]")
    print("   2. Spotify Duo      -> TRIAL  (Ends in 1 day)  [Near Deadline]")
    print("   3. Prime Video      -> ACTIVE (Ended 2 days ago) [Ready for Celery Beat process_due]")
    print("   4. Disney+          -> PAST_DUE (Ready for 'Renew Now' on Dashboard)")
    print("   5. HBO Max          -> PENDING (Queued on Dashboard)")

    db.close()

def dispatch_all_test_emails():
    print(f"\n[MAIL] Dispatching ALL 8 Celery Email Templates to {TARGET_EMAIL} ...")
    now_iso = datetime.now(timezone.utc).isoformat()
    three_days_iso = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()

    send_welcome_email.delay(TARGET_EMAIL, TARGET_NAME)
    send_customer_invite_email.delay(TARGET_EMAIL, TARGET_NAME, "demo_invite_token_123")
    send_trial_activated_email.delay(TARGET_EMAIL, TARGET_NAME, "Spotify Duo", 7, three_days_iso)
    send_subscription_confirmation.delay(TARGET_EMAIL, TARGET_NAME, "Netflix Premium", "monthly", three_days_iso)
    send_cancellation_email.delay(TARGET_EMAIL, TARGET_NAME, "Prime Video", True, now_iso)
    send_reactivation_email.delay(TARGET_EMAIL, TARGET_NAME, "Disney+", three_days_iso)
    send_past_due_email.delay(TARGET_EMAIL, TARGET_NAME, "Prime Video", now_iso)
    send_deadline_reminder.delay(TARGET_EMAIL, TARGET_NAME, "Netflix Premium", three_days_iso, 3)

    print("[MAIL SUCCESS] All 8 Celery email tasks dispatched! Check your Gmail inbox.")

if __name__ == "__main__":
    seed_demo_data()
    # Uncomment the line below if you want to dispatch all 8 test emails instantly to your inbox:
    dispatch_all_test_emails()
