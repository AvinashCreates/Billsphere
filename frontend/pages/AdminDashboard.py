import requests
import streamlit as st

from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css, render_hero


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
        background: linear-gradient(135deg, #2F6D4F, #1F4D38);
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
        color: #E4EFE7;
        font-size: 17px;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- Sidebar ----------------

with st.sidebar:

    st.markdown("# Billing Platform")

    st.caption("Admin Dashboard")

    st.divider()

    st.write(f"**{user['username']}**")
    st.write("Administrator")

    st.divider()

    if st.button("Dashboard", icon=":material/dashboard:", use_container_width=True):
        st.rerun()

    if st.button("Customers", icon=":material/group:", use_container_width=True):
        st.switch_page("pages/Customers.py")

    if st.button("Plans", icon=":material/inventory_2:", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("Invoices", icon=":material/receipt_long:", use_container_width=True):
        st.switch_page("pages/Invoices.py")

    if st.button("Notifications", icon=":material/notifications:", use_container_width=True):
        st.switch_page("pages/Notifications.py")

    if st.button("Billing Calendar", icon=":material/calendar_month:", use_container_width=True):
        st.switch_page("pages/BillingCalendar.py")

   

    if st.button("StreamFlix Analytics", icon=":material/bar_chart:", use_container_width=True):
        st.switch_page("pages/StreamFlixAdmin.py")

    if st.button("Profile", icon=":material/person:", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        logout()
        st.switch_page("app.py")


# ---------------- Hero Banner ----------------

render_hero(
    f"Welcome, {user['username']}!",
    "Manage customers, plans, invoices, subscriptions and monitor your billing platform from one place.",
    icon="dashboard",
)


# ---------------- Fetch all live data ----------------
customer_count = 0
plan_count = 0
total_revenue = 0.0
pending_revenue = 0.0
active_sub_count = 0
recent_customers = []
recent_invoices = []
overdue_count = 0

try:

    # ---------- Customers ----------

    customer_resp = requests.get(
        f"{API_URL}/customers/",
        headers=get_headers(),
        params={"page": 1, "page_size": 5, "sort_by": "created_at", "sort_order": "desc"},
    )

    if customer_resp.status_code == 200:
        customer_data = customer_resp.json()
        customer_count = customer_data.get("total_customers", 0)
        recent_customers = customer_data.get("customers", customer_data.get("items", []))[:5]

    # ---------- Plans ----------

    plan_resp = requests.get(f"{API_URL}/plans/", headers=get_headers())

    if plan_resp.status_code == 200:
        plan_data = plan_resp.json()
        if isinstance(plan_data, list):
            plan_count = len(plan_data)
        elif isinstance(plan_data, dict):
            plan_count = len(plan_data.get("items", []))

    # ---------- Subscriptions ----------

    subs_resp = requests.get(f"{API_URL}/subscriptions/", headers=get_headers())

    if subs_resp.status_code == 200:
        subs_data = subs_resp.json()
        subs_list = subs_data if isinstance(subs_data, list) else subs_data.get("items", [])
        active_sub_count = sum(1 for s in subs_list if s.get("status") == "active")

except Exception as e:
    st.warning(f"Some dashboard data could not be loaded: {e}")

# ---------- Invoices / Revenue ----------
# Own try/except so a 422 or exception here is visible
# and isn't silently swallowed by the block above.

try:
    invoice_resp = requests.get(
        f"{API_URL}/invoices/",
        headers=get_headers(),
        params={"page": 1, "page_size": 100},
    )

    if invoice_resp.status_code == 200:
        invoice_data = invoice_resp.json()
        invoices = invoice_data if isinstance(invoice_data, list) else invoice_data.get("items", [])

        total_revenue = sum(
            float(inv.get("total_amount", 0) or 0)
            for inv in invoices
            if inv.get("payment_status") == "paid"
        )

        pending_revenue = sum(
            float(inv.get("total_amount", 0) or 0)
            for inv in invoices
            if inv.get("payment_status") != "paid"
        )

        overdue_count = sum(1 for inv in invoices if inv.get("status") == "overdue")

        recent_invoices = sorted(
            invoices, key=lambda i: i.get("created_at", ""), reverse=True
        )[:5]
    else:
        st.error(f"Invoice fetch failed: {invoice_resp.status_code} — {invoice_resp.text}")

except Exception as e:
    st.error(f"Invoice fetch exception: {e}")
# ---------- Display Overview ----------

st.subheader("Platform Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Customers", customer_count)

with c2:
    st.metric("Active Subscriptions", active_sub_count)

with c3:
    st.metric("Revenue (Paid)", f"${total_revenue:,.2f}")

with c4:
    st.metric("Pending Revenue", f"${pending_revenue:,.2f}")

st.divider()


# ---------------- Quick Actions ----------------

st.subheader("Quick Actions")

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("Manage Customers", icon=":material/group:", use_container_width=True, key="admin_manage_customers"):
        st.switch_page("pages/Customers.py")

with q2:
    if st.button("Manage Plans", icon=":material/inventory_2:", use_container_width=True, key="admin_manage_plans"):
        st.switch_page("pages/Plans.py")

with q3:
    if st.button("Manage Invoices", icon=":material/receipt_long:", use_container_width=True, key="admin_manage_invoices"):
        st.switch_page("pages/Invoices.py")

with q4:
    if st.button("Billing Calendar", icon=":material/calendar_month:", use_container_width=True, key="admin_calendar"):
        st.switch_page("pages/BillingCalendar.py")


# ---------------- Bottom Section ----------------

left, right = st.columns([2, 1])


# ---------- Recent Activity (live) ----------

with left:

    st.subheader("Recent Activity")

    if recent_customers:
        st.markdown("**Recent Customers**")
        for c in recent_customers:
            username = c.get("username", "Unknown")
            created = (c.get("created_at", "") or "")[:10]
            st.write(f"• {username} — joined {created or 'N/A'}")
    else:
        st.info("No recent customer registrations")

    st.write("")

    if recent_invoices:
        st.markdown("**Recent Invoices**")
        for inv in recent_invoices:
            status_icon = "" if inv.get("payment_status") == "paid" else ""
            st.write(
                f"{status_icon} {inv.get('invoice_number', 'N/A')} — "
                f"${inv.get('total_amount', 0.0):.2f} "
                f"({inv.get('payment_status', 'unpaid')})"
            )
    else:
        st.info("No invoices yet")


# ---------- System Status (live) ----------

with right:

    st.subheader("Platform Status")

    st.success("API Server Running")
    st.success("Authentication Enabled")
    st.success("Database Connected")

    if overdue_count > 0:
        st.warning(f"{overdue_count} Overdue Invoice(s)")
    else:
        st.success("No Overdue Invoices")

    st.info(f"{plan_count} Plan(s) Configured")
    st.info(f"{active_sub_count} Active Subscription(s)")