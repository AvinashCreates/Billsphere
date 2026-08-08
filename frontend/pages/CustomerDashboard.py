import streamlit as st
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

# ---------------- Overview ----------------

st.subheader("📊 Subscription Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📦 Active Plan", "No Plan")

with c2:
    st.metric("🔄 Status", "Inactive")

with c3:
    st.metric("📅 Renewal Date", "--")

with c4:
    st.metric("💰 Amount Paid", "₹0")

st.divider()

# ---------------- Quick Actions ----------------

st.subheader("⚡ Quick Actions")

q1, q2, q3 = st.columns(3)

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
        "👤 My Profile",
        use_container_width=True
    ):
        st.switch_page("pages/Profile.py")

st.divider()

