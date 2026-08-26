import streamlit as st

import io
from PIL import Image
from streamlit_cropper import st_cropper

from auth import logout
from styles import load_css

import requests
from config import API_URL
from utils import get_headers

# ==========================================================
# Load Common CSS
# ==========================================================

load_css()


# ==========================================================
# Authentication
# ==========================================================

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]


# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(
    page_title="Profile",
    page_icon="👤",
    layout="wide"
)


# ==========================================================
# Custom CSS
# ==========================================================

st.markdown(
    """
    <style>

    .hero-banner {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        padding: 35px 40px;
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }

    .hero-content h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .hero-content p {
        color: #e0ecff;
        font-size: 17px;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.markdown("# 💳 Billing Platform")

    if user["role"] == "admin":
        st.caption("Admin Profile")
    else:
        st.caption("Customer Profile")

    st.divider()

    st.write(f"👤 **{user['username']}**")

    if user["role"] == "admin":
        st.write("🛡 Administrator")
    else:
        st.write("👥 Customer")

    st.divider()


    # ------------------------------------------------------
    # Admin Navigation
    # ------------------------------------------------------

    if user["role"] == "admin":

        if st.button(
            "🏠 Dashboard",
            use_container_width=True
        ):
            st.switch_page(
                "pages/AdminDashboard.py"
            )

        if st.button(
            "👥 Customers",
            use_container_width=True
        ):
            st.switch_page(
                "pages/Customers.py"
            )

        if st.button(
            "📦 Plans",
            use_container_width=True
        ):
            st.switch_page(
                "pages/Plans.py"
            )

        if st.button(
            "🧾 Invoices",
            use_container_width=True
        ):
            st.switch_page(
                "pages/Invoices.py"
            )

        if st.button(
            "👤 Profile",
            use_container_width=True
        ):
            st.rerun()


    # ------------------------------------------------------
    # Customer Navigation
    # ------------------------------------------------------

    else:

        if st.button(
            "🏠 Dashboard",
            use_container_width=True
        ):
            st.switch_page(
                "pages/CustomerDashboard.py"
            )

        if st.button(
            "📦 Plans",
            use_container_width=True
        ):
            st.switch_page(
                "pages/Plans.py"
            )

        if st.button(
            "🔄 My Subscription",
            use_container_width=True
        ):
            st.switch_page(
                "pages/Subscriptions.py"
            )

        if st.button(
            "🧾 My Invoices",
            use_container_width=True
        ):
            st.switch_page(
                "pages/MyInvoices.py"
            )

        if st.button(
            "👤 Profile",
            use_container_width=True
        ):
            st.rerun()


    st.divider()


    # ------------------------------------------------------
    # Logout
    # ------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()
        st.switch_page("app.py")


# ==========================================================
# Hero Banner
# EXACT SAME PATTERN AS WORKING CUSTOMERS PAGE
# ==========================================================

if user["role"] == "admin":

    description = (
        "View your administrator account information "
        "and manage your billing platform."
    )

else:

    description = (
        "View your account information "
        "and manage your billing profile."
    )


st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-content">
            <h1>My Profile 👤</h1>
            <p>{description}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# Account Information
# ==========================================================

st.subheader("👤 Account Information")


with st.container(border=True):

    col1, col2 = st.columns(
        [1, 2]
    )


    # ------------------------------------------------------
    # Profile Avatar
    # ------------------------------------------------------

    with col1:

        username = user.get(
            "username",
            "User"
        )

        first_letter = username[0].upper()

        profile_picture = user.get("profile_picture")

        if profile_picture:
            st.markdown(
                f"""
                <div style="
                    width:120px;
                    height:120px;
                    border-radius:50%;
                    overflow:hidden;
                    margin:auto;
                ">
                    <img src="{API_URL}{profile_picture}"
                         style="width:100%; height:100%; object-fit:cover;" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="
                    width:120px;
                    height:120px;
                    border-radius:50%;
                    background:linear-gradient(
                        135deg,
                        #2563eb,
                        #1d4ed8
                    );
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:white;
                    font-size:48px;
                    font-weight:700;
                    margin:auto;
                ">
                    {first_letter}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f"### {username}"
        )

        if user["role"] == "admin":
            st.info("🛡 Administrator")
        else:
            st.info("👤 Customer")

with st.expander("📷 Change Profile Picture"):

    # ------------------------------------------------------
    # Show success message after upload
    # ------------------------------------------------------
    if st.session_state.get("profile_picture_updated"):
        st.success("✅ Profile picture uploaded successfully.")

        # Clear the flag after displaying the message
        st.session_state["profile_picture_updated"] = False

    else:

        uploaded_file = st.file_uploader(
            "Upload a new picture",
            type=["png", "jpg", "jpeg", "webp", "jfif"],
            key="profile_pic_uploader",
        )

        if uploaded_file is not None:

            try:
                image = Image.open(uploaded_file).convert("RGB")

                st.caption(
                    "Drag the box to choose what shows in your profile circle:"
                )

                cropped_image = st_cropper(
                    image,
                    aspect_ratio=(1, 1),
                    box_color="#2563eb",
                    realtime_update=True,
                    key="profile_pic_cropper",
                )

                preview_col, _ = st.columns([1, 3])

                with preview_col:
                    st.caption("Preview")

                    st.image(
                        cropped_image.resize((120, 120)),
                        width=120,
                    )

                if st.button(
                    "Upload",
                    key="upload_pic_btn",
                    use_container_width=True,
                ):

                    buffer = io.BytesIO()

                    cropped_image.save(
                        buffer,
                        format="PNG",
                    )

                    buffer.seek(0)

                    files = {
                        "file": (
                            "profile.png",
                            buffer.getvalue(),
                            "image/png",
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/users/me/profile-picture",
                        files=files,
                        headers=get_headers(),
                    )

                    if response.status_code == 200:

                        # Update current user information
                        st.session_state["user"] = response.json()

                        # Tell next Streamlit run to show success only
                        st.session_state["profile_picture_updated"] = True

                        # Clear uploader/cropper state
                        for key in [
                            "profile_pic_uploader",
                            "profile_pic_cropper",
                        ]:
                            st.session_state.pop(key, None)

                        st.rerun()

                    else:

                        try:
                            detail = response.json().get(
                                "detail",
                                "Failed to upload profile picture.",
                            )
                        except Exception:
                            detail = "Failed to upload profile picture."

                        st.error(detail)

            except Exception as exc:

                st.error(
                    f"Unable to process the selected image: {exc}"
                )

    # ------------------------------------------------------
    # Personal Information
    # ------------------------------------------------------

  
with col2:

    st.markdown("### 📋 Personal Information")

    with st.container(border=True):

        r1, r2 = st.columns([1, 3])

        with r1:
            st.write("👤 **Username**")

        with r2:
            st.write(
                user.get("username", "Not available")
            )

        st.divider()

        r1, r2 = st.columns([1, 3])

        with r1:
            st.write("✉️ **Email**")

        with r2:
            st.write(
                user.get("email", "Not available")
            )

        st.divider()

        with st.expander("✏️ Edit Username"):

            with st.form("edit_username_form"):

                new_username = st.text_input(
                    "New Username",
                    value=user.get("username", ""),
                )

                submitted = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if submitted:

                    response = requests.put(
                        f"{API_URL}/users/me",
                        json={"username": new_username},
                        headers=get_headers(),
                    )

                    if response.status_code == 200:
                        st.session_state["user"] = response.json()
                        st.success("Username updated!")
                        st.rerun()
                    else:
                        try:
                            st.error(response.json()["detail"])
                        except Exception:
                            st.error("Failed to update username.")

        


    # Account Role
    with st.container(border=True):
        info_col1, info_col2 = st.columns([1, 3])

        with info_col1:
            st.write("🛡️")

        with info_col2:
            st.caption("ACCOUNT ROLE")

            if user["role"] == "admin":
                st.write("Administrator")
            else:
                st.write("Customer")

# ==========================================================
# Account Status
# ==========================================================

st.divider()

st.subheader("🔐 Account Status")


status1, status2, status3 = st.columns(3)


with status1:

    st.success(
        "✅ Account Active"
    )


with status2:

    st.success(
        "🔒 Authentication Enabled"
    )


with status3:

    if user["role"] == "admin":

        st.info(
            "🛡 Admin Access"
        )

    else:

        st.info(
            "👥 Customer Access"
        )


# ==========================================================
# Quick Actions
# ==========================================================

st.divider()

st.subheader("⚡ Quick Actions")


action1, action2, action3 = st.columns(3)


# ----------------------------------------------------------
# Dashboard
# ----------------------------------------------------------

with action1:

    if st.button(
        "🏠 Back to Dashboard",
        use_container_width=True,
        type="primary"
    ):

        if user["role"] == "admin":

            st.switch_page(
                "pages/AdminDashboard.py"
            )

        else:

            st.switch_page(
                "pages/CustomerDashboard.py"
            )


# ----------------------------------------------------------
# Module
# ----------------------------------------------------------

with action2:

    if user["role"] == "admin":

        if st.button(
            "👥 Manage Customers",
            use_container_width=True
        ):

            st.switch_page(
                "pages/Customers.py"
            )

    else:

        if st.button(
            "📦 Explore Plans",
            use_container_width=True
        ):

            st.switch_page(
                "pages/Plans.py"
            )


# ----------------------------------------------------------
# Logout
# ----------------------------------------------------------

with action3:

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()

        st.switch_page("app.py")