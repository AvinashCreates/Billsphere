import streamlit as st
from auth import logout

# Protect Dashboard
if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

st.set_page_config(
    page_title="Dashboard",
    page_icon="💳",
    layout="wide"
)

with st.sidebar:

    st.title("Billing Platform")

    st.divider()

    st.write(f"User : {user['username']}")
    st.write(f"Role : {user['role']}")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Profile",
            "Customers",
            "Admin Panel",
            "Logout"
        ]
    )

if page == "Profile":
    st.switch_page("pages/Profile.py")

elif page == "Customers":
    st.switch_page("pages/Customers.py")

elif page == "Admin Panel":

    if user["role"] == "admin":
        st.switch_page("pages/Admin.py")
    else:
        st.error("Access Denied")

elif page == "Logout":

    logout()

    st.switch_page("pages/Login.py")

st.title("Dashboard")

st.write(
    "Welcome to the Billing Platform"
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label="Customers",
        value="0"
    )

with col2:

    st.metric(
        label="Invoices",
        value="0"
    )

with col3:

    st.metric(
        label="Revenue",
        value="$0"
    )

st.divider()

st.subheader("Quick Actions")

c1, c2 = st.columns(2)

with c1:

    if st.button(
        "Manage Customers",
        use_container_width=True
    ):
        st.switch_page("pages/Customers.py")

with c2:

    st.button(
        "Create Invoice",
        use_container_width=True
    )