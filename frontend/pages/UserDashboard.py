import streamlit as st
from auth import logout

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

st.set_page_config(
    page_title="User Dashboard",
    layout="wide"
)

with st.sidebar:

    st.title("Customer Dashboard")

    st.write(user["username"])

    st.write(user["role"])

    if st.button("My Profile"):
        st.switch_page("pages/Profile.py")

    if st.button("Customers"):
        st.switch_page("pages/Customers.py")

    if st.button("Logout"):
        logout()
        st.switch_page("app.py")

st.title("User Dashboard")

st.success(f"Welcome, {user['username']}!")

st.write(f"Role: {user['role']}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.metric("My Orders", "0")

with col2:
    st.metric("Pending Bills", "$0")

st.divider()

st.subheader("Customer Features")

if st.button("View My Bills", use_container_width=True):
    st.info("Billing module will be implemented next.")

if st.button("Download Invoice", use_container_width=True):
    st.info("Invoice download feature coming soon.")