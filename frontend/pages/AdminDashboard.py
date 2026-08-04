import streamlit as st
from auth import logout

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

if user["role"] != "admin":
    st.error("Access Denied")
    st.stop()

st.set_page_config(
    page_title="Admin Dashboard",
    layout="wide"
)

with st.sidebar:

    st.title("Billing Platform")

    st.write(f"User: {user['username']}")
    st.write(f"Role: {user['role']}")

    st.divider()

    if st.button("Dashboard", use_container_width=True):
        st.rerun()

    if st.button("Customers", use_container_width=True):
        st.switch_page("pages/Customers.py")

    if st.button("Plans", use_container_width=True):
       st.switch_page("pages/Plans.py")

    if st.button("Invoices", use_container_width=True):
        st.switch_page("pages/Invoices.py")

    if st.button("Subscriptions", use_container_width=True):
        st.info("Subscriptions module coming soon.")

    if st.button("Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

st.title("Admin Dashboard")

st.success(f"Welcome, {user['username']}!")

st.write(f"Role: {user['role']}")

st.divider()

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Manage Customers", use_container_width=True):
        st.switch_page("pages/Customers.py")

with col2:
    if st.button("Manage Plans", use_container_width=True):
        st.switch_page("pages/Plans.py")

with col3:
    if st.button("Manage Invoices", use_container_width=True):
        st.switch_page("pages/Invoices.py")