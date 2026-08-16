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

# Allow only customers
if user["role"] != "user":
    st.error("Access Denied")
    st.stop()

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Customer Dashboard",
    page_icon="💳",
    layout="wide"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>

[data-testid="stSidebar"]{
    background:#0F172A;
}

[data-testid="stSidebar"] *{
    color:white;
}

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

div[data-testid="metric-container"]{
    background:white;
    border:1px solid #E5E7EB;
    border-radius:15px;
    padding:18px;
    box-shadow:0px 3px 10px rgba(0,0,0,.08);
}

.banner{
    background:linear-gradient(90deg,#2563EB,#1D4ED8);
    padding:25px;
    border-radius:18px;
    color:white;
    margin-bottom:20px;
}

.section{
    background:#F8FAFC;
    padding:18px;
    border-radius:15px;
    border:1px solid #E5E7EB;
    height:100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------

with st.sidebar:

    st.markdown("# 💳 Billing Platform")

    st.caption("Customer Dashboard")

    st.divider()

    st.write(f"👤 **{user['username']}**")
    st.write("👤 Customer")

    st.divider()

    if st.button("🏠 Dashboard", use_container_width=True):
        st.rerun()

    if st.button("📦 Available Plans", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("🔄 My Subscription", use_container_width=True):
        st.switch_page("pages/Subscriptions.py")

    if st.button("🧾 My Invoices", use_container_width=True):
        st.switch_page("pages/MyInvoices.py")

    if st.button("👤 My Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Hero Banner ----------------

st.markdown(f"""
<div class="banner">

<h2>👋 Welcome back, {user['username']}</h2>

Manage your subscription, explore available plans and monitor your billing from one place.

</div>
""", unsafe_allow_html=True)

# ---------------- Overview (live data) ----------------

st.subheader("📊 Subscription Overview")

plan_name = "No Plan"
status_label = "None"
renewal_date = "--"
amount_paid = "$0.00"

try:
    sub_resp = requests.get(f"{API_URL}/subscriptions/my", headers=get_headers())

    if sub_resp.status_code == 200:
        subscription = sub_resp.json()
        status_label = subscription.get("status", "unknown").capitalize()

        period_end = subscription.get("current_period_end")
        if period_end:
            renewal_date = period_end[:10]

        plan_resp = requests.get(
            f"{API_URL}/plans/{subscription['plan_id']}",
            headers=get_headers(),
        )
        if plan_resp.status_code == 200:
            plan_name = plan_resp.json().get("name", plan_name)

        inv_resp = requests.get(
            f"{API_URL}/invoices/my",
            headers=get_headers(),
            params={"page": 1, "page_size": 1, "sort_by": "created_at", "sort_order": "desc"},
        )
        if inv_resp.status_code == 200:
            items = inv_resp.json().get("items", [])
            if items:
                amount_paid = f"${items[0].get('total_amount', 0.0):.2f}"

except Exception:
    pass

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📦 Active Plan", plan_name)

with c2:
    st.metric("🔄 Status", status_label)

with c3:
    st.metric("📅 Renewal Date", renewal_date)

with c4:
    st.metric("💰 Latest Invoice", amount_paid)

st.divider()

# ---------------- Quick Actions ----------------

st.subheader("⚡ Quick Actions")

q1, q2, q3, q4 = st.columns(4)

with q1:

    if st.button(
        "📦 Browse Plans",
        use_container_width=True
    ):
        st.switch_page("pages/Plans.py")

with q2:

    if st.button(
        "🔄 My Subscription",
        use_container_width=True
    ):
        st.switch_page("pages/Subscriptions.py")

with q3:

    if st.button(
        "🧾 My Invoices",
        use_container_width=True
    ):
        st.switch_page("pages/MyInvoices.py")

with q4:

    if st.button(
        "👤 My Profile",
        use_container_width=True
    ):
        st.switch_page("pages/Profile.py")

st.divider()

