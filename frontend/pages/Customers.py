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

if user["role"] != "admin":
    st.error("Access Denied: Admin access required.")
    st.stop()


# ---------- Page Config ----------

st.set_page_config(
    page_title="Customers",
    layout="wide"
)

st.title("👥 Customer Management")
st.caption("View, search, and manage registered customers.")


# ---------- Search + Pagination state ----------

if "cust_page" not in st.session_state:
    st.session_state["cust_page"] = 1

search_col, _ = st.columns([2, 3])

with search_col:
    search = st.text_input("🔍 Search by username or email", key="cust_search")

params = {"page": st.session_state["cust_page"], "page_size": 10}
if search:
    params["search"] = search


# ---------- Create Customer ----------

with st.expander("➕ Add New Customer"):

    with st.form("create_customer_form", clear_on_submit=True):

        c1, c2, c3 = st.columns(3)

        with c1:
            new_username = st.text_input("Username")
        with c2:
            new_email = st.text_input("Email")
        with c3:
            new_password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Create Customer", type="primary")

        if submitted:

            if not new_username or not new_email or not new_password:
                st.error("All fields are required.")
            else:
                resp = requests.post(
                    f"{API_URL}/customers/",
                    json={
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                    },
                    headers=get_headers(),
                )

                if resp.status_code == 201:
                    st.success(f"Customer '{new_username}' created.")
                    st.rerun()
                else:
                    try:
                        st.error(resp.json()["detail"])
                    except Exception:
                        st.error("Failed to create customer.")

st.divider()


# ---------- Call Backend ----------

response = requests.get(
    f"{API_URL}/customers/",
    headers=get_headers(),
    params=params,
)


if response.status_code == 200:

    data = response.json()

    customers = data["customers"]
    total_customers = data["total_customers"]
    total_pages = data.get("total_pages", 1)

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
                    st.write(f"**Customer ID:** {customer['id']}")

                with col2:
                    st.write(f"**Role:** {customer['role']}")
                    plan = customer.get("current_plan") or "No Plan"
                    status = customer.get("subscription_status") or "—"
                    st.write(f"**Plan:** {plan}")
                    st.write(f"**Subscription:** {status}")

                with col3:
                    st.write(
                        f"**Created At:** {str(customer['created_at'])[:10]}"
                    )
                    st.write(f"**Total Invoices:** {customer.get('total_invoices', 0)}")
                    st.write(f"**Total Spent:** ${customer.get('total_spent', 0.0):.2f}")

                with st.expander("✏️ Edit / Delete"):

                    with st.form(f"edit_form_{customer['id']}"):

                        e1, e2, e3 = st.columns(3)

                        with e1:
                            edit_username = st.text_input(
                                "Username", value=customer["username"],
                                key=f"u_{customer['id']}"
                            )
                        with e2:
                            edit_email = st.text_input(
                                "Email", value=customer["email"],
                                key=f"e_{customer['id']}"
                            )
                        with e3:
                            edit_password = st.text_input(
                                "New Password (leave blank to keep current)",
                                type="password",
                                key=f"p_{customer['id']}"
                            )

                        save_col, delete_col = st.columns(2)

                        with save_col:
                            save = st.form_submit_button("💾 Save Changes", use_container_width=True)

                        with delete_col:
                            delete = st.form_submit_button("🗑 Delete Customer", use_container_width=True)

                        if save:

                            payload = {
                                "username": edit_username or None,
                                "email": edit_email or None,
                                "password": edit_password or None,
                            }

                            resp = requests.put(
                                f"{API_URL}/customers/{customer['id']}",
                                json=payload,
                                headers=get_headers(),
                            )

                            if resp.status_code == 200:
                                st.success("Customer updated.")
                                st.rerun()
                            else:
                                try:
                                    st.error(resp.json()["detail"])
                                except Exception:
                                    st.error("Failed to update customer.")

                        if delete:

                            resp = requests.delete(
                                f"{API_URL}/customers/{customer['id']}",
                                headers=get_headers(),
                            )

                            if resp.status_code == 204:
                                st.success("Customer deleted.")
                                st.rerun()
                            else:
                                try:
                                    st.error(resp.json()["detail"])
                                except Exception:
                                    st.error(
                                        "Failed to delete customer. "
                                        "They may have existing billing history."
                                    )

    else:
        st.info("No customers found.")

    # ---------- Pagination ----------

    st.divider()

    p1, p2, p3 = st.columns([2, 3, 2])

    with p1:
        if st.session_state["cust_page"] > 1 and st.button("⬅ Previous"):
            st.session_state["cust_page"] -= 1
            st.rerun()

    with p2:
        st.write(
            f"Page **{st.session_state['cust_page']}** of **{max(1, total_pages)}** "
            f"(Total: {total_customers})"
        )

    with p3:
        if st.session_state["cust_page"] < total_pages and st.button("Next ➡"):
            st.session_state["cust_page"] += 1
            st.rerun()

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
