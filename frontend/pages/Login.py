import streamlit as st
from auth import login

from styles import load_css  

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Login",
    page_icon="💳",
    layout="centered"
)

# ---------------- Custom CSS ----------------
load_css()  
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

# ---------------- Welcome Banner ----------------
st.markdown("""
<div class="welcome-box">

<h2>Welcome Back</h2>

<p>Sign in to your Billing Platform account</p>

</div>
""", unsafe_allow_html=True)

# ---------------- Login Form ----------------
with st.container(border=True):

    st.subheader("🔑 Sign In")
    st.caption("Use your registered email and password.")

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    if st.button("Sign In", use_container_width=True):

        if not email or not password:
            st.warning("Please enter your email and password.")

        else:

            if login(email, password):

                user = st.session_state["user"]

                if user["role"] == "admin":
                    st.switch_page("pages/AdminDashboard.py")
                else:
                    st.switch_page("pages/CustomerDashboard.py")

            else:
                st.error("Invalid email or password.")

# ---------------- Register ----------------
st.markdown(
    "<div style='text-align:center; margin-top:12px;'>"
    "Don't have an account?"
    "</div>",
    unsafe_allow_html=True
)

if st.button("📝 Create Account", use_container_width=True):
    st.switch_page("pages/Register.py")

st.caption("© 2026 Billing Platform")