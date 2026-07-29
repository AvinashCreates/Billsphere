import requests
import streamlit as st
from config import API_URL
from utils import get_headers

# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]


# ---------------- Page Config ----------------

st.set_page_config(page_title="Plans", layout="wide")

st.title("Plans")


# ==========================================================
# CREATE PLAN (ADMIN)
# ==========================================================

if user["role"] == "admin":
    st.subheader("➕ Add New Plan")

    with st.form("create_plan_form"):
        name = st.text_input("Plan Name")
        description = st.text_area("Description")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        duration = st.number_input("Duration (Days)", min_value=1)

        submitted = st.form_submit_button("Create Plan")

        if submitted:
            # Prevent empty plan creation
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
                    f"{API_URL}/plans", json=payload, headers=get_headers()
                )

                if response.status_code == 200:
                    st.success("Plan created successfully.")
                    st.rerun()
                else:
                    try:
                        st.error(response.json()["detail"])
                    except Exception:
                        st.error("Unable to create plan.")

    st.divider()


# ==========================================================
# FETCH PLANS
# ==========================================================

response = requests.get(f"{API_URL}/plans", headers=get_headers())

if response.status_code != 200:
    st.error("Unable to fetch plans.")
    st.stop()

plans = response.json()

if not plans:
    st.info("No plans available.")
    st.stop()


# ==========================================================
# DISPLAY PLANS
# ==========================================================

for plan in plans:
    # Skip inactive plans for customer view completely
    if user["role"] != "admin" and plan["status"] != "active":
        continue

    with st.container(border=True):
        st.subheader(plan["name"])
        st.write(plan["description"])

        col1, col2, col3 = st.columns(3)

        # Formatted price to 2 decimal places
        col1.metric("Price", f"${float(plan['price']):.2f}")

        col2.metric("Duration", f"{plan['duration']} Days")

        status_text = (
            "🟢 Active" if plan["status"] == "active" else "🔴 Inactive"
        )

        col3.metric("Status", status_text)

        # ======================================================
        # ADMIN FEATURES
        # ======================================================
        if user["role"] == "admin":
            if plan["status"] == "active":
                with st.expander("✏ Edit Plan"):
                    new_name = st.text_input(
                        "Plan Name",
                        value=plan["name"],
                        key=f"name_{plan['id']}",
                    )

                    new_description = st.text_area(
                        "Description",
                        value=plan["description"],
                        key=f"description_{plan['id']}",
                    )

                    new_price = st.number_input(
                        "Price",
                        value=float(plan["price"]),
                        key=f"price_{plan['id']}",
                    )

                    new_duration = st.number_input(
                        "Duration",
                        value=int(plan["duration"]),
                        key=f"duration_{plan['id']}",
                    )

                    new_status = st.selectbox(
                        "Status",
                        ["active", "inactive"],
                        index=0 if plan["status"] == "active" else 1,
                        key=f"status_{plan['id']}",
                    )

                    if st.button("💾 Update Plan", key=f"update_{plan['id']}"):
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
                            headers=get_headers(),
                        )

                        if response.status_code == 200:
                            st.success("✅ Plan updated successfully.")
                            st.rerun()
                        else:
                            try:
                                st.error(response.json()["detail"])
                            except Exception:
                                st.error("Unable to update plan.")

                confirm_key = f"confirm_delete_{plan['id']}"

                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:
                    if st.button(
                        "🗑 Deactivate Plan", key=f"delete_{plan['id']}"
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()

                else:
                    st.warning(
                        "Are you sure you want to deactivate this plan?"
                    )

                    col_yes, col_no = st.columns(2)

                    with col_yes:
                        if st.button("✅ Yes", key=f"yes_{plan['id']}"):
                            response = requests.delete(
                                f"{API_URL}/plans/{plan['id']}",
                                headers=get_headers(),
                            )

                            if response.status_code == 200:
                                st.success("Plan deactivated successfully.")
                            else:
                                st.error("Unable to deactivate plan.")

                            st.session_state[confirm_key] = False
                            st.rerun()

                    with col_no:
                        if st.button("❌ Cancel", key=f"cancel_{plan['id']}"):
                            st.session_state[confirm_key] = False
                            st.rerun()

            else:
                st.warning("This plan is currently inactive.")

        # ======================================================
        # CUSTOMER FEATURES
        # ======================================================
        else:
            if plan["status"] == "active":
                with st.expander("View Details"):
                    detail_response = requests.get(
                        f"{API_URL}/plans/{plan['id']}", headers=get_headers()
                    )

                    if detail_response.status_code == 200:
                        detail = detail_response.json()

                        status = (
                            "🟢 Active"
                            if detail["status"] == "active"
                            else "🔴 Inactive"
                        )

                        st.write(f"**Description:** {detail['description']}")
                        st.write(
                            f"**Price:** ${float(detail['price']):.2f}"
                        )
                        st.write(f"**Duration:** {detail['duration']} Days")
                        st.write(f"**Status:** {status}")
                    else:
                        st.error("Unable to fetch plan details.")