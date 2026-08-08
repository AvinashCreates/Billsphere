import requests
import streamlit as st
from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css

# ---------------- Load Common CSS ----------------

load_css()

# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state.get("user", {})

# ---------------- Page Config ----------------

st.set_page_config(
    page_title="Plans",
    page_icon="📦",
    layout="wide"
)

# ---------------- Blue Banner CSS ----------------

st.markdown(
    """
    <style>

    .invoice-hero-banner {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        padding: 35px 40px;
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }

    .invoice-hero-banner h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .invoice-hero-banner p {
        color: #e0ecff;
        font-size: 17px;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Sidebar ----------------

with st.sidebar:
    st.title("Billing Platform")

    st.write(f"**User:** {user.get('username')}")
    st.write(f"**Role:** {user.get('role')}")

    st.divider()

    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/AdminDashboard.py")

    if st.button("👥 Customers", use_container_width=True):
        st.switch_page("pages/Customers.py")

    if st.button("📦 Plans", use_container_width=True):
        st.rerun()

    if st.button("🧾 Invoices", use_container_width=True):
        st.switch_page("pages/Invoice.py")

    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Hero Banner ----------------

st.markdown(
    """
    <div class="invoice-hero-banner">
        <h1>Plan Management 📦</h1>
        <p>
            Create, manage, and explore subscription plans
            for your customers from one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# CREATE PLAN - ADMIN
# ==========================================================

if user["role"] == "admin":

    st.subheader("➕ Add New Plan")

    with st.container(border=True):
        with st.form("create_plan_form"):

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "Plan Name",
                    placeholder="Enter plan name"
                )

                price = st.number_input(
                    "Price",
                    min_value=0.0,
                    format="%.2f"
                )

            with col2:
                duration = st.number_input(
                    "Duration (Days)",
                    min_value=1
                )

                description = st.text_area(
                    "Description",
                    placeholder="Enter plan description"
                )

            submitted = st.form_submit_button(
                "➕ Create Plan",
                use_container_width=True
            )

            if submitted:

                if not name.strip():
                    st.error("Plan name is required.")

                elif not description.strip():
                    st.error("Description is required.")

                else:

                    payload = {
                        "name": name,
                        "description": description,
                        "price": price,
                        "duration": duration,
                    }

                    response = requests.post(
                        f"{API_URL}/plans",
                        json=payload,
                        headers=get_headers()
                    )

                    if response.status_code == 200:
                        st.success(
                            "✅ Plan created successfully."
                        )
                        st.rerun()

                    else:
                        try:
                            st.error(
                                response.json()["detail"]
                            )
                        except Exception:
                            st.error(
                                "Unable to create plan."
                            )

    st.divider()

# ==========================================================
# FETCH PLANS
# ==========================================================

response = requests.get(
    f"{API_URL}/plans",
    headers=get_headers()
)

if response.status_code != 200:
    st.error("Unable to fetch plans.")
    st.stop()

plans = response.json()

# ==========================================================
# NO PLANS
# ==========================================================

if not plans:
    st.info("No plans available.")
    st.stop()

# ==========================================================
# DISPLAY PLANS
# ==========================================================

for plan in plans:

    # Skip inactive plans for customer view
    if (
        user["role"] != "admin"
        and plan["status"] != "active"
    ):
        continue

    # ---------------- Plan Card ----------------

    with st.container(border=True):

        col1, col2, col3, col4 = st.columns(
            [2, 3, 2, 2]
        )

        # ---------------- Plan Name ----------------

        with col1:
            st.subheader(
                f"📦 {plan['name']}"
            )

            st.caption(
                f"ID: #{plan['id']}"
            )

        # ---------------- Description ----------------

        with col2:
            st.write(
                f"**Description:** {plan['description']}"
            )

        # ---------------- Price ----------------

        with col3:
            st.metric(
                "Price",
                f"${float(plan['price']):.2f}"
            )

        # ---------------- Duration ----------------

        with col4:
            st.metric(
                "Duration",
                f"{plan['duration']} Days"
            )

        # ---------------- Status ----------------

        status_text = (
            "🟢 Active"
            if plan["status"] == "active"
            else "🔴 Inactive"
        )

        st.write(
            f"**Status:** {status_text}"
        )

        # ==================================================
        # ADMIN FEATURES
        # ==================================================

        if user["role"] == "admin":

            if plan["status"] == "active":

                # ---------------- Edit Plan ----------------

                with st.expander("✏️ Edit Plan"):

                    new_name = st.text_input(
                        "Plan Name",
                        value=plan["name"],
                        key=f"name_{plan['id']}"
                    )

                    new_description = st.text_area(
                        "Description",
                        value=plan["description"],
                        key=f"description_{plan['id']}"
                    )

                    new_price = st.number_input(
                        "Price",
                        min_value=0.0,
                        value=float(plan["price"]),
                        format="%.2f",
                        key=f"price_{plan['id']}"
                    )

                    new_duration = st.number_input(
                        "Duration (Days)",
                        min_value=1,
                        value=int(plan["duration"]),
                        key=f"duration_{plan['id']}"
                    )

                    new_status = st.selectbox(
                        "Status",
                        ["active", "inactive"],
                        index=(
                            0
                            if plan["status"] == "active"
                            else 1
                        ),
                        key=f"status_{plan['id']}"
                    )

                    if st.button(
                        "💾 Update Plan",
                        key=f"update_{plan['id']}",
                        use_container_width=True
                    ):

                        payload = {
                            "name": new_name,
                            "description": new_description,
                            "price": new_price,
                            "duration": new_duration,
                            "status": new_status,
                        }

                        response = requests.put(
                            f"{API_URL}/plans/{plan['id']}",
                            json=payload,
                            headers=get_headers()
                        )

                        if response.status_code == 200:
                            st.success(
                                "✅ Plan updated successfully."
                            )
                            st.rerun()

                        else:
                            try:
                                st.error(
                                    response.json()["detail"]
                                )
                            except Exception:
                                st.error(
                                    "Unable to update plan."
                                )

                # ---------------- Deactivate Plan ----------------

                confirm_key = (
                    f"confirm_delete_{plan['id']}"
                )

                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:

                    if st.button(
                        "🗑️ Deactivate Plan",
                        key=f"delete_{plan['id']}",
                        use_container_width=True
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()

                else:

                    st.warning(
                        "Are you sure you want to deactivate this plan?"
                    )

                    col_yes, col_no = st.columns(2)

                    with col_yes:

                        if st.button(
                            "✅ Yes",
                            key=f"yes_{plan['id']}",
                            use_container_width=True
                        ):

                            response = requests.delete(
                                f"{API_URL}/plans/{plan['id']}",
                                headers=get_headers()
                            )

                            if response.status_code == 200:
                                st.success(
                                    "Plan deactivated successfully."
                                )
                            else:
                                st.error(
                                    "Unable to deactivate plan."
                                )

                            st.session_state[confirm_key] = False
                            st.rerun()

                    with col_no:

                        if st.button(
                            "❌ Cancel",
                            key=f"cancel_{plan['id']}",
                            use_container_width=True
                        ):
                            st.session_state[confirm_key] = False
                            st.rerun()

            else:

                st.warning(
                    "This plan is currently inactive."
                )

        # ==================================================
        # CUSTOMER FEATURES
        # ==================================================

        else:

            if plan["status"] == "active":

                with st.expander(
                    "📄 View Plan Details"
                ):

                    detail_response = requests.get(
                        f"{API_URL}/plans/{plan['id']}",
                        headers=get_headers()
                    )

                    if detail_response.status_code == 200:

                        detail = detail_response.json()

                        status = (
                            "🟢 Active"
                            if detail["status"] == "active"
                            else "🔴 Inactive"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.markdown(
                                "#### 📦 Plan Information"
                            )

                            st.write(
                                f"**Description:** "
                                f"{detail['description']}"
                            )

                            st.write(
                                f"**Duration:** "
                                f"{detail['duration']} Days"
                            )

                        with col2:

                            st.markdown(
                                "#### 💰 Pricing"
                            )

                            st.write(
                                f"**Price:** "
                                f"${float(detail['price']):.2f}"
                            )

                            st.write(
                                f"**Status:** {status}"
                            )

                    else:

                        st.error(
                            "Unable to fetch plan details."
                        )