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

    if st.button("Plans"):
       st.switch_page("pages/Plans.py") 

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

    import requests
import streamlit as st
from auth import logout
from config import API_URL
from utils import get_headers

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

st.set_page_config(
    page_title="User Dashboard",
    layout="wide"
)

try:
    unread_response = requests.get(
        f"{API_URL}/notifications/unread-count", headers=get_headers()
    )
    unread_count = (
        unread_response.json()["unread_count"]
        if unread_response.status_code == 200
        else 0
    )
except Exception:
    unread_count = 0

with st.sidebar:

    st.title("Customer Dashboard")

    st.write(user["username"])

    st.write(user["role"])

    if st.button("My Profile"):
        st.switch_page("pages/Profile.py")

    if st.button("Customers"):
        st.switch_page("pages/Customers.py")

    if st.button("Plans"):
       st.switch_page("pages/Plans.py") 

    notif_label = "🔔 Notifications"
    if unread_count:
        notif_label += f" ({unread_count})"

    if st.button(notif_label):
        st.switch_page("pages/Notifications.py")

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