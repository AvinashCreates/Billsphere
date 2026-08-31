import streamlit as st

from styles import load_css, render_hero

# ---------------- Redirect if already logged in ----------------
if "token" in st.session_state:

    user = st.session_state["user"]

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/CustomerDashboard.py")

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Billing Platform",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

load_css()

# Hide Streamlit's default sidebar only on this page (landing page has no
# app sidebar at all -- load_css() only hides the auto-generated page nav,
# this hides the sidebar shell entirely, which is specific to this page).
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ---------------- Hero Section ----------------
render_hero(
    "Billing Platform",
    "Simple. Secure. Smart billing for recurring subscriptions.",
    icon="account_balance",
)

# ---------------- Action Buttons ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Sign In", icon=":material/login:", use_container_width=True):
        st.switch_page("pages/Login.py")

with col2:
    if st.button("Create Account", icon=":material/person_add:", use_container_width=True):
        st.switch_page("pages/Register.py")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- Features ----------------
st.subheader(":material/star: Features")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### :material/lock: Secure Authentication")
        st.caption("JWT-based secure login and role-based access.")

    with st.container(border=True):
        st.markdown("#### :material/group: Customer Management")
        st.caption("Manage customer accounts efficiently.")

with col2:
    with st.container(border=True):
        st.markdown("#### :material/inventory_2: Subscription Management")
        st.caption("Create and manage subscription plans.")

    with st.container(border=True):
        st.markdown("#### :material/receipt_long: Invoice Management")
        st.caption("Generate and track customer invoices.")

st.caption("© 2026 Billing Platform · Secure Subscription & Invoice Management")
