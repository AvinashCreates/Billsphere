import streamlit as st
import requests
from config import API_URL

st.set_page_config(
    page_title="Register",
    page_icon="💳",
    layout="centered"
)

st.title("Create Account")
st.caption("Create your Billing Platform account")

username = st.text_input("Username")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)
if not username or not email or not password:
    st.warning("Please fill in all fields.")
else:
    
  if st.button("Register", use_container_width=True):

    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    if response.status_code == 200:

        st.success("Registration successful.")

        if st.button("Go to Sign In"):
            st.switch_page("pages/Login.py")

    else:
        st.error(response.json()["detail"])

st.divider()

st.write("Already have an account?")

if st.button("Sign In", use_container_width=True):
    st.switch_page("pages/Login.py")