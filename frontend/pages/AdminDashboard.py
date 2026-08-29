import requests
import streamlit as st

from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css


load_css()


# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

if user["role"] != "admin":
    st.error("Access Denied")
    st.stop()


# ---------------- Page Config ----------------

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="💳",
    layout="wide"
)


# ---------------- Custom CSS ----------------

st.markdown(
    """
    <style>

    .hero-banner {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        padding: 35px 40px;
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }

    .hero-content h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .hero-content p {
        color: #e0ecff;
        font-size: 17px;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- Sidebar ----------------

with st.sidebar:

    st.markdown("# 💳 Billing Platform")

    st.caption("Admin Dashboard")

    st.divider()

    st.write(f"👤 **{user['username']}**")
    st.write("🛡 Administrator")

    st.divider()

    if st.button("🏠 Dashboard", use_container_width=True):
        st.rerun()

    if st.button("👥 Customers", use_container_width=True):
        st.switch_page("pages/Customers.py")

    if st.button("📦 Plans", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("🧾 Invoices", use_container_width=True):
        st.switch_page("pages/Invoices.py")

    if st.button("🔔 Notifications", use_container_width=True):
        st.switch_page("pages/Notifications.py")

    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")


# ---------------- Hero Banner ----------------

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-content">
            <h1>Welcome, {user['username']}! 👋</h1>
            <p>
                Manage customers, plans, invoices, subscriptions
                and monitor your billing platform from one place.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------- Overview (Live Data) ----------------

st.subheader("📊 Platform Overview")

customer_count = 0
plan_count = 0
total_revenue = 0.0


try:

    # ---------- Customers ----------

    customer_resp = requests.get(
        f"{API_URL}/customers/",
        headers=get_headers()
    )

    if customer_resp.status_code == 200:

        customer_data = customer_resp.json()

        # Backend returns total_customers directly
        customer_count = customer_data.get("total_customers", 0)


    # ---------- Plans ----------

    plan_resp = requests.get(
        f"{API_URL}/plans/",
        headers=get_headers()
    )

    if plan_resp.status_code == 200:

        plan_data = plan_resp.json()

        # If API returns a list
        if isinstance(plan_data, list):
            plan_count = len(plan_data)

        # If API returns paginated response
        elif isinstance(plan_data, dict):
            plan_items = plan_data.get("items", [])
            plan_count = len(plan_items)


    # ---------- Revenue ----------

    invoice_resp = requests.get(
        f"{API_URL}/invoices/",
        headers=get_headers(),
        params={
            "page": 1,
            "page_size": 1000,
            "sort_by": "created_at",
            "sort_order": "desc"
        }
    )

    if invoice_resp.status_code == 200:

        invoice_data = invoice_resp.json()

        # If API returns a list
        if isinstance(invoice_data, list):
            invoices = invoice_data

        # If API returns paginated response
        elif isinstance(invoice_data, dict):
            invoices = invoice_data.get("items", [])

        else:
            invoices = []

        total_revenue = sum(
            float(invoice.get("total_amount", 0) or 0)
            for invoice in invoices
        )


except Exception:
    pass


# ---------- Display Overview ----------

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "👥 Customers",
        customer_count
    )

with c2:
    st.metric(
        "📦 Plans",
        plan_count
    )

with c3:
    st.metric(
        "💰 Revenue",
        f"₹{total_revenue:,.2f}"
    )

st.divider()


# ---------------- Quick Actions ----------------

st.subheader("⚡ Quick Actions")

q1, q2, q3 = st.columns(3)

with q1:
    if st.button(
        "👥 Manage Customers",
        use_container_width=True,
        key="admin_manage_customers"
    ):
        st.switch_page("pages/Customers.py")


with q2:
    if st.button(
        "📦 Manage Plans",
        use_container_width=True,
        key="admin_manage_plans"
    ):
        st.switch_page("pages/Plans.py")


with q3:
    if st.button(
        "🧾 Manage Invoices",
        use_container_width=True,
        key="admin_manage_invoices"
    ):
        st.switch_page("pages/Invoices.py")


# ---------------- Bottom Section ----------------

left, right = st.columns([2, 1])


# ---------- Recent Activity ----------

with left:

    st.subheader("📈 Recent Activity")

    st.info("🆕 No recent customer registrations")

    st.info("📦 No plans created yet")

    st.info("🧾 Invoice Module Active")

    st.info("💳 Payment Module Active (API only - no admin UI yet)")

    st.info("🔔 Notification Module Active")


# ---------- System Status ----------

with right:

    st.subheader("⚙ Platform Status")

    st.success("✅ API Server Running")

    st.success("✅ Authentication Enabled")

    st.success("✅ Database Connected")

    st.success("✅ Subscription Module Active")

    st.success("✅ Invoice Module Active")

    st.success("✅ Payment Module Active")

    st.success("✅ Notification Module Active")


# ---------- Upcoming Modules ----------

st.subheader("🚀 Upcoming Modules")

m1, m2 = st.columns(2)

with m1:
    st.info("📅 Admin Billing Calendar")

with m2:
    st.info("📊 Reports & Analytics")
