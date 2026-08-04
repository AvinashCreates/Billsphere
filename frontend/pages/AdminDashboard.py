import streamlit as st
from auth import logout

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

    if st.button("🔄 Subscriptions", use_container_width=True):
        st.switch_page("pages/Subscriptions.py")

    if st.button("🧾 Invoices", use_container_width=True):
        st.switch_page("pages/Invoices.py")

    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Hero Banner ----------------

st.markdown(f"""
<div class="banner">

<h2>👋 Welcome back, {user['username']}</h2>

Manage customers, plans, subscriptions and monitor your billing platform from one place.

</div>
""", unsafe_allow_html=True)

# ---------------- Overview ----------------

st.subheader("📊 Platform Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("👤 Users", "1")

with c2:
    st.metric("👥 Customers", "0")

with c3:
    st.metric("📦 Plans", "0")

with c4:
    st.metric("💰 Revenue", "₹0")

st.divider()

# ---------------- Quick Actions ----------------


st.subheader("⚡ Quick Actions")

q1, q2, q3 = st.columns(3)

with q1:

    if st.button(
        "👥 Manage Customers",
        use_container_width=True
    ):
        st.switch_page("pages/Customers.py")

with q2:

    if st.button(
        "📦 Manage Plans",
        use_container_width=True
    ):
        st.switch_page("pages/Plans.py")

with q3:

    if st.button(
        "🧾 Manage Invoices",
        use_container_width=True
    ):
        st.switch_page("pages/Invoices.py")

# ---------------- Bottom Section ----------------

left, right = st.columns([2,1])

# ---------- Recent Activity ----------

with left:

    st.subheader("📈 Recent Activity")

    st.info("🆕 No recent customer registrations")

    st.info("📦 No plans created yet")

    st.info("🧾 Invoice module coming soon")

    st.info("💳 Payment module coming soon")

# ---------- System Status ----------

with right:

    st.subheader("⚙ Platform Status")

    st.success("✅ API Server Running")

    st.success("✅ Authentication Enabled")

    st.success("✅ Database Connected")

    st.warning("⏳ Subscription Module Pending")

    st.warning("⏳ Invoice Module Pending")

st.divider()

# ---------------- Future Modules ----------------

st.subheader("🚀 Upcoming Modules")

m1, m2, m3 = st.columns(3)

with m1:
    st.info("🧾 Invoice Management")

with m2:
    st.info("💳 Payment Processing")

with m3:
    st.info("📊 Reports & Analytics")
