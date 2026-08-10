import streamlit as st

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")
    
if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

st.set_page_config(
    page_title="Profile",
    layout="wide"
)

st.title("My Profile")

col1, col2 = st.columns([1,2])

with col1:
    st.image(
        "https://placehold.co/200x200",
        width=180
    )

with col2:
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**Role:** {user['role']}")

st.divider()

if st.button("Back"):

    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/CustomerDashboard.py")