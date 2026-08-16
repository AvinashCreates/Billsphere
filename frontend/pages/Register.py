import streamlit as st
import requests
from config import API_URL

# ---------------- Page Config ----------------

st.set_page_config(
    page_title="Register",
    page_icon="💳",
    layout="centered"
)

# ---------------- Custom CSS ----------------

st.markdown("""
<style>

.welcome-box{
    background: linear-gradient(135deg,#2563EB,#1E40AF);
    color: white;
    padding: 32px 28px;
    border-radius: 18px;
    width:100%;
    margin-bottom:20px;
    text-align:center;
    box-shadow:0 10px 25px rgba(37,99,235,.18);
}

.welcome-box .logo{
    font-size:52px;
    margin-bottom:8px;
}

.welcome-box h2{
    margin:0;
    font-size:34px;
    font-weight:700;
}

.welcome-box p{
    margin-top:8px;
    margin-bottom:0;
    font-size:17px;
    opacity:.95;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Hero Banner ----------------

st.markdown("""
<div class="welcome-box">
<h2>Create Account</h2>

<p>
        Securely manage your customers, subscription plans,
        recurring billing and invoices
</p>

</div>
""", unsafe_allow_html=True)

# ---------------- Register Form ----------------

with st.container(border=True):

    st.subheader("📝 Create Account")
    st.caption("Fill in your details to get started.")

    username = st.text_input(
        "Username",
        placeholder="Enter your username"
    )

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password"
    )

    if st.button("Create Account", use_container_width=True):

        if not username or not email or not password:
            st.warning("Please fill in all fields.")

        else:

            response = requests.post(
                f"{API_URL}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            if response.status_code == 200:
                st.success("🎉 Registration successful! Please sign in.")
                st.switch_page("pages/Login.py")

            else:
                try:
                    st.error(response.json()["detail"])
                except:
                    st.error("Registration failed.")

# ---------------- Login ----------------

st.markdown(
    "<div class='footer-text'>Already have an account?</div>",
    unsafe_allow_html=True
)

if st.button("🔑 Sign In", use_container_width=True):
    st.switch_page("pages/Login.py")

st.caption("© 2026 Billing Platform")