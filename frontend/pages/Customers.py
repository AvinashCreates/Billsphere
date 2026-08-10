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

st.title("👥 Customer Management")
st.caption("View registered customers and their account information.")


# ---------- Call Backend ----------

response = requests.get(
    f"{API_URL}/customers/",
    headers=get_headers()
)


if response.status_code == 200:

    data = response.json()

    customers = data["customers"]
    total_customers = data["total_customers"]

    # ---------- Summary ----------

    st.metric(
        label="Total Customers",
        value=total_customers
    )

    st.divider()

    # ---------- Customer List ----------

    st.subheader("📋 Customer List")

    if customers:

        for customer in customers:

            with st.container(border=True):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Username:** {customer['username']}")
                    st.write(f"**Email:** {customer['email']}")

                with col2:
                    st.write(f"**Role:** {customer['role']}")
                    st.write(f"**Customer ID:** {customer['id']}")

                with col3:
                    st.write(
                        f"**Created At:** {customer['created_at']}"
                    )

    else:
        st.info("No customers found.")

else:

    st.error(
        f"Failed to load customers. "
        f"Status code: {response.status_code}"
    )


# ---------- Back Button ----------

st.divider()

if st.button(
    "⬅️ Back to Dashboard",
    key="customers_back_dashboard"
):

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/CustomerDashboard.py")