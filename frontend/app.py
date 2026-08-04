import streamlit as st

# ---------------- Redirect if already logged in ----------------
if "token" in st.session_state:

    user = st.session_state["user"]

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/UserDashboard.py")

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Billing Platform",
    page_icon="💳",
    layout="centered"
)

st.set_page_config(
    page_title="Billing Platform",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit's default sidebar only on this page
st.markdown("""
<style>

/* Hide the entire sidebar */
[data-testid="stSidebar"] {
    display: none;
}

/* Hide the sidebar toggle button */
[data-testid="collapsedControl"] {
    display: none;
}

/* Hide the default page navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Hide Default Streamlit Navigation ----------------
st.markdown("""
<style>

/* Hide Streamlit multipage menu */
[data-testid="stSidebarNav"]{
    display:none;
}

[data-testid="stSidebarHeader"]{
    display:none;
}

/* Hero Banner */
.hero{
    background: linear-gradient(135deg,#2563EB,#1E40AF);
    padding:45px;
    border-radius:18px;
    text-align:center;
    color:white;
    margin-bottom:25px;
}

/* Feature Cards */
.feature{
    background:#F8FAFC;
    border:1px solid #E5E7EB;
    border-radius:12px;
    padding:18px;
    text-align:center;
    font-size:16px;
    font-weight:600;
}

/* Buttons */
.stButton>button{
    border-radius:10px;
    height:50px;
    font-size:16px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Hero Section ----------------
st.markdown("""
<div class="hero">

<h1>💳 Billing Platform</h1>

<h4>Simple. Secure. Smart Billing.</h4>

<p>
Manage customers, subscriptions, plans and invoices
from one powerful dashboard.
</p>

</div>
""", unsafe_allow_html=True)

# ---------------- Action Buttons ----------------

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("🔑 Sign In", use_container_width=True):
        st.switch_page("pages/Login.py")

with col2:
    if st.button("📝 Create Account", use_container_width=True):
        st.switch_page("pages/Register.py")

st.markdown("<br>", unsafe_allow_html=True)

# ----------festures------------


st.subheader("✨ Features")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 🔐 Secure Authentication")
        st.caption("JWT-based secure login and role-based access.")

    with st.container(border=True):
        st.markdown("### 👥 Customer Management")
        st.caption("Manage customer accounts efficiently.")

with col2:
    with st.container(border=True):
        st.markdown("### 📦 Subscription Management")
        st.caption("Create and manage subscription plans.")

    with st.container(border=True):
        st.markdown("### 🧾 Invoice Management")
        st.caption("Generate and track customer invoices.")



st.caption("© 2026 Billing Platform • Secure Subscription & Invoice Management")