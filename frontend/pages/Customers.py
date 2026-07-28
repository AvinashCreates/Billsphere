import streamlit as st
import requests

from config import API_URL
from utils import get_headers

# ---------- Authentication ----------
if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

# ---------- Page Config ----------
st.set_page_config(
    page_title="Customers",
    layout="wide"
)

st.title("Customers")

# ---------- Call Backend ----------
response = requests.get(
    f"{API_URL}/customers/",
    headers=get_headers()
)

if response.status_code == 200:

    data = response.json()

    st.success(data["message"])

    st.write("Logged in User")
    st.info(data["logged_in_user"])

else:
    st.error("Authentication Failed")

# ---------- Back Button ----------
if st.button("Back to Dashboard"):

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/UserDashboard.py")