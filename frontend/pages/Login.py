import streamlit as st
from auth import login

st.set_page_config(
    page_title="Login",
    page_icon="💳",
    layout="centered"
)

st.title("Sign In")
st.caption("Sign in using your registered account")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Sign In", use_container_width=True):

    if not email or not password:
        st.warning("Please enter your email and password.")

    else:
        if login(email, password):

            user = st.session_state["user"]

            if user["role"] == "admin":
                st.switch_page("pages/AdminDashboard.py")
            else:
                st.switch_page("pages/UserDashboard.py")

        else:
            st.error("Invalid email or password")

st.divider()

st.write("Don't have an account?")

if st.button("Create Account", use_container_width=True):
    st.switch_page("pages/Register.py")