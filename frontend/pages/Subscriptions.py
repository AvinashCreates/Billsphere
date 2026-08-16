import requests
import streamlit as st
from datetime import datetime

from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css

load_css()

# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state.get("user", {})

if user.get("role") != "user":
    st.error("Access Denied: Customer access required.")
    st.stop()

# ---------------- Page Config ----------------

st.set_page_config(
    page_title="My Subscription",
    page_icon="🔄",
    layout="wide",
)

# ---------------- Styling (matches Customer Dashboard) ----------------

st.markdown(
    """
    <style>

    [data-testid="stSidebar"]{
        background:#0F172A;
    }

    [data-testid="stSidebar"] *{
        color:white;
    }

    .banner{
        background:linear-gradient(90deg,#2563EB,#1D4ED8);
        padding:25px;
        border-radius:18px;
        color:white;
        margin-bottom:20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar ----------------

with st.sidebar:

    st.markdown("# 💳 Billing Platform")
    st.caption("Customer Dashboard")
    st.divider()

    st.write(f"👤 **{user.get('username')}**")
    st.write("👤 Customer")

    st.divider()

    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/CustomerDashboard.py")

    if st.button("📦 Available Plans", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("🔄 My Subscription", use_container_width=True):
        st.rerun()

    if st.button("🧾 My Invoices", use_container_width=True):
        st.switch_page("pages/MyInvoices.py")

    if st.button("👤 My Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Header ----------------

st.markdown(
    """
    <div class="banner">
    <h2>🔄 My Subscription</h2>
    Manage your active plan, renew, or cancel.
    </div>
    """,
    unsafe_allow_html=True,
)


def fmt_date(value):
    if not value:
        return "N/A"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y")
    except Exception:
        return value[:10]


# ---------------- Fetch current subscription ----------------

try:
    sub_resp = requests.get(f"{API_URL}/subscriptions/my", headers=get_headers())
except Exception as e:
    st.error(f"Failed to connect to backend server: {e}")
    st.stop()

if sub_resp.status_code == 404:

    st.info("You don't have a subscription yet.")

    if st.button("📦 Browse Available Plans", type="primary"):
        st.switch_page("pages/Plans.py")

    st.stop()

elif sub_resp.status_code != 200:

    st.error("Unable to fetch your subscription.")
    st.stop()

subscription = sub_resp.json()

# ---------------- Fetch plan details ----------------

plan = {}
plan_resp = requests.get(
    f"{API_URL}/plans/{subscription['plan_id']}",
    headers=get_headers(),
)

if plan_resp.status_code == 200:
    plan = plan_resp.json()

# ---------------- Subscription Overview ----------------

status = subscription.get("status", "unknown")

status_badges = {
    "active": "🟢 Active",
    "cancelled": "🔴 Cancelled",
    "expired": "⚪ Expired",
    "blocked": "🚫 Blocked",
}

badge = status_badges.get(status, status)

with st.container(border=True):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📦 Plan", plan.get("name", f"Plan #{subscription['plan_id']}"))

    with c2:
        st.metric("🔄 Status", badge)

    with c3:
        st.metric("📅 Renews / Ends", fmt_date(subscription.get("current_period_end")))

    with c4:
        st.metric("💰 Price", f"${float(plan.get('price', 0)):.2f}" if plan else "N/A")

    st.write(f"**Started:** {fmt_date(subscription.get('current_period_start'))}")

    if plan.get("description"):
        st.write(f"**Description:** {plan['description']}")

st.divider()

# ---------------- Actions ----------------

st.subheader("⚡ Manage Subscription")

a1, a2, a3 = st.columns(3)

with a1:

    if status == "active":

        if st.button("❌ Cancel Subscription", use_container_width=True):

            resp = requests.post(
                f"{API_URL}/subscriptions/{subscription['id']}/cancel",
                headers=get_headers(),
            )

            if resp.status_code == 200:
                st.success("Subscription cancelled.")
                st.rerun()
            else:
                try:
                    st.error(resp.json()["detail"])
                except Exception:
                    st.error("Unable to cancel subscription.")

with a2:

    if status in ("expired", "cancelled"):

        if st.button("🔁 Renew Subscription", use_container_width=True):

            resp = requests.post(
                f"{API_URL}/subscriptions/{subscription['id']}/renew",
                headers=get_headers(),
            )

            if resp.status_code == 200:
                st.success("Subscription renewed. A new invoice has been generated.")
                st.rerun()
            else:
                try:
                    st.error(resp.json()["detail"])
                except Exception:
                    st.error("Unable to renew subscription.")

with a3:

    if st.button("🧾 View My Invoices", use_container_width=True):
        st.switch_page("pages/MyInvoices.py")

if status == "active":
    st.caption(
        "Want a different plan? Cancel your current subscription, "
        "then subscribe to a new one from the Plans page."
    )
