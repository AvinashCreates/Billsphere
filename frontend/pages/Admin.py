import streamlit as st

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

if user["role"] != "admin":
    st.error("Access Denied")
    st.stop()

st.set_page_config(
    page_title="Admin Panel",
    layout="wide"
)

st.title("Admin Dashboard")

st.success("Administrator Access Granted")

col1, col2 = st.columns(2)

with col1:
    st.metric("Users", "1")

with col2:
    st.metric("Customers", "0")

st.divider()

st.write("Administrative Functions")

if st.button("Manage Plans", use_container_width=True):
    st.info("Plans Module Coming Soon")

if st.button("Manage Customers", use_container_width=True):
    st.switch_page("pages/Customers.py")

if st.button("View Subscriptions", use_container_width=True):
    st.info("Subscriptions Module Coming Soon")
    
st.divider()

if st.button("Back"):

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/UserDashboard.py")