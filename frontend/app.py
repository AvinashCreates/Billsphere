import streamlit as st
if "token" in st.session_state:

    user = st.session_state["user"]

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/UserDashboard.py")

st.set_page_config(
    page_title="Billing Platform",
    page_icon="💳",
    layout="centered"
)

st.title("Billing Platform")

st.caption("Secure billing management with JWT Authentication and Role-Based Access Control")

st.subheader("Welcome")

st.write(
    "Manage customers, invoices and billing securely with JWT Authentication."
)

col1, col2 = st.columns(2)

with col1:
    if st.button("Sign In", use_container_width=True):
        st.switch_page("pages/Login.py")

with col2:
    if st.button("Create Account", use_container_width=True):
        st.switch_page("pages/Register.py")