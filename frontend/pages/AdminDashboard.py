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

    # Invoice module added from invoices branch
    if st.button("🧾 Invoices", use_container_width=True):
        st.switch_page("pages/Invoices.py")

    if st.button("🔄 Subscriptions", use_container_width=True):
        st.info("Subscriptions module coming soon.")

    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")


# ---------------- Hero Banner ----------------

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

# ---------------- Overview ----------------

st.subheader("📊 Platform Overview")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("👥 Customers", "0")

with c2:
    st.metric("📦 Plans", "0")

with c3:
    st.metric("💰 Revenue", "₹0")

st.divider()


# ---------------- Quick Actions ----------------

st.subheader("⚡ Quick Actions")

q1, q2, q3, q4 = st.columns(4)

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

with q4:
    if st.button(
        "🔄 Manage Subscriptions",
        use_container_width=True
    ):
        st.info("Subscriptions module coming soon.")


st.divider()


