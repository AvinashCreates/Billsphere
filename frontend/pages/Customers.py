import requests
import streamlit as st
from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css


load_css()


# ==========================================================
# Authentication
# ==========================================================

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

if user["role"] != "admin":
    st.error("Access Denied: Admin access required.")
    st.stop()


# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(
    page_title="Customers",
    page_icon="👥",
    layout="wide"
)


# ==========================================================
# Custom CSS
# Same hero style as AdminDashboard.py
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
# Same style as AdminDashboard.py
# ==========================================================

with st.sidebar:

    st.markdown("# 💳 Billing Platform")

    st.caption("Customer Management")

    st.divider()

    st.write(f"👤 **{user['username']}**")
    st.write("🛡 Administrator")

    st.divider()

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
        st.rerun()

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
        st.switch_page(
            "pages/Profile.py"
        )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()
        st.switch_page("app.py")


# ==========================================================
# Hero Banner
# Same structure as AdminDashboard.py
# ==========================================================

# ---------------- Hero Banner ----------------

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-content">
            <h1>Customer Management 👥</h1>
            <p>
                View, search, create, and manage
                registered customers from one place.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# Search + Pagination State
# ==========================================================

if "cust_page" not in st.session_state:
    st.session_state["cust_page"] = 1


# ==========================================================
# Search
# ==========================================================

search_col, _ = st.columns([2, 3])

with search_col:

    search = st.text_input(
        "🔍 Search by username or email",
        key="cust_search"
    )


# ==========================================================
# API Parameters
# ==========================================================

params = {
    "page": st.session_state["cust_page"],
    "page_size": 10
}

if search:
    params["search"] = search


# ==========================================================
# Create Customer
# ==========================================================

st.subheader("➕ Add New Customer")

with st.container(border=True):

    with st.form(
        "create_customer_form",
        clear_on_submit=True
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            new_username = st.text_input(
                "Username",
                placeholder="Enter username"
            )

        with c2:

            new_email = st.text_input(
                "Email",
                placeholder="Enter email"
            )

        with c3:

            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password"
            )

        submitted = st.form_submit_button(
            "➕ Create Customer",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if (
                not new_username
                or not new_email
                or not new_password
            ):

                st.error(
                    "All fields are required."
                )

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

                    st.success(
                        f"Customer '{new_username}' created."
                    )

                    st.rerun()

                else:

                    try:
                        st.error(
                            resp.json()["detail"]
                        )

                    except Exception:
                        st.error(
                            "Failed to create customer."
                        )


st.divider()


# ==========================================================
# Call Backend
# ==========================================================

response = requests.get(
    f"{API_URL}/customers/",
    headers=get_headers(),
    params=params,
)


# ==========================================================
# Customer Data
# ==========================================================

if response.status_code == 200:

    data = response.json()

    customers = data["customers"]

    total_customers = data["total_customers"]

    total_pages = data.get(
        "total_pages",
        1
    )


    # ======================================================
    # Customer Overview
    # ======================================================

    st.subheader("📊 Customer Overview")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "👥 Total Customers",
            total_customers
        )

    with c2:

        st.metric(
            "📄 Current Page",
            st.session_state["cust_page"]
        )

    with c3:

        st.metric(
            "👤 Customers Shown",
            len(customers)
        )


    st.divider()


    # ======================================================
    # Customer List
    # ======================================================

    st.subheader("📋 Customer List")


    if customers:

        for customer in customers:

            with st.container(border=True):

                col1, col2, col3 = st.columns(3)


                # ------------------------------------------------
                # Customer Information
                # ------------------------------------------------
                with col1:

                # ------------------------------------------------
                # Customer Profile Picture
                # ------------------------------------------------

                    profile_picture = customer.get(
                         "profile_picture"
                    )

                    if profile_picture:

                       st.markdown(
                          f"""
                          <div style="
                               width:70px;
                               height:70px;
                               border-radius:50%;
                               overflow:hidden;
                               margin-bottom:10px;
                               border:2px solid #2563eb;
                          ">
                               <img
                                  src="{API_URL}{profile_picture}"
                                  style="
                                     width:100%;
                                     height:100%;
                                     object-fit:cover;
                                  "
                                />
                           </div>
                           """,
                           unsafe_allow_html=True,
                    )

                    else:

                        
                          # Show first-letter avatar ONLY when no profile picture exists
                          username = customer.get("username", "U")

                          first_letter = (
                          username[0].upper()
                          if username
                          else "U"
                          )

                          st.markdown(
                                 f"""
                                 <div style="
                                 width:70px;
                                 height:70px;
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
                                 font-size:28px;
                                 font-weight:700;
                                 margin-bottom:10px;
                                 ">
                                     {first_letter}
                                 </div>
                                  """,
                                  unsafe_allow_html=True,
                            )


                    st.subheader(
                                customer["username"]
                    )
                    st.caption(
                             f"Customer ID: #{customer['id']}"
                    )

                    st.write(
                             f"**Email:** "
                             f"{customer['email']}"
                    )

                    st.write(
                             f"**Role:** "
                             f"{customer['role']}"
                    )
                
                


                # ------------------------------------------------
                # Subscription Information
                # ------------------------------------------------

                with col2:

                    plan = (
                        customer.get("current_plan")
                        or "No Plan"
                    )

                    status = (
                        customer.get(
                            "subscription_status"
                        )
                        or "—"
                    )

                    st.write(
                        f"**Plan:** {plan}"
                    )

                    st.write(
                        f"**Subscription:** {status}"
                    )

                    st.write(
                        f"**Created At:** "
                        f"{str(customer['created_at'])[:10]}"
                    )


                # ------------------------------------------------
                # Billing Information
                # ------------------------------------------------

                with col3:

                    st.write(
                        f"**Total Invoices:** "
                        f"{customer.get('total_invoices', 0)}"
                    )

                    st.write(
                        f"**Total Spent:** "
                        f"${customer.get('total_spent', 0.0):.2f}"
                    )


                # =================================================
                # Edit / Delete
                # =================================================

                with st.expander(
                    "✏️ Edit / Delete"
                ):

                    with st.form(
                        f"edit_form_{customer['id']}"
                    ):

                        e1, e2, e3 = st.columns(3)


                        with e1:

                            edit_username = st.text_input(
                                "Username",
                                value=customer["username"],
                                key=f"u_{customer['id']}"
                            )


                        with e2:

                            edit_email = st.text_input(
                                "Email",
                                value=customer["email"],
                                key=f"e_{customer['id']}"
                            )


                        with e3:

                            edit_password = st.text_input(
                                "New Password "
                                "(leave blank to keep current)",
                                type="password",
                                key=f"p_{customer['id']}"
                            )


                        save_col, delete_col = st.columns(2)


                        with save_col:

                            save = st.form_submit_button(
                                "💾 Save Changes",
                                use_container_width=True
                            )


                        with delete_col:

                            delete = st.form_submit_button(
                                "🗑 Delete Customer",
                                use_container_width=True
                            )


                        # -----------------------------------------
                        # Save Customer
                        # -----------------------------------------

                        if save:

                            payload = {
                                "username": (
                                    edit_username
                                    or None
                                ),
                                "email": (
                                    edit_email
                                    or None
                                ),
                                "password": (
                                    edit_password
                                    or None
                                ),
                            }

                            resp = requests.put(
                                f"{API_URL}/customers/"
                                f"{customer['id']}",
                                json=payload,
                                headers=get_headers(),
                            )


                            if resp.status_code == 200:

                                st.success(
                                    "Customer updated."
                                )

                                st.rerun()

                            else:

                                try:

                                    st.error(
                                        resp.json()["detail"]
                                    )

                                except Exception:

                                    st.error(
                                        "Failed to update customer."
                                    )


                        # -----------------------------------------
                        # Delete Customer
                        # -----------------------------------------

                        if delete:

                            resp = requests.delete(
                                f"{API_URL}/customers/"
                                f"{customer['id']}",
                                headers=get_headers(),
                            )


                            if resp.status_code == 204:

                                st.success(
                                    "Customer deleted."
                                )

                                st.rerun()

                            else:

                                try:

                                    st.error(
                                        resp.json()["detail"]
                                    )

                                except Exception:

                                    st.error(
                                        "Failed to delete customer. "
                                        "They may have existing "
                                        "billing history."
                                    )


    else:

        st.info(
            "No customers found."
        )


    # ==========================================================
    # Pagination
    # ==========================================================

    st.divider()

    p1, p2, p3 = st.columns(
        [2, 3, 2]
    )


    with p1:

        if (
            st.session_state["cust_page"] > 1
            and st.button(
                "⬅ Previous",
                use_container_width=True
            )
        ):

            st.session_state["cust_page"] -= 1

            st.rerun()


    with p2:

        st.write(
            f"Page **{st.session_state['cust_page']}** "
            f"of **{max(1, total_pages)}** "
            f"(Total: {total_customers})"
        )


    with p3:

        if (
            st.session_state["cust_page"] < total_pages
            and st.button(
                "Next ➡",
                use_container_width=True
            )
        ):

            st.session_state["cust_page"] += 1

            st.rerun()


else:

    st.error(
        f"Failed to load customers. "
        f"Status code: {response.status_code}"
    )


# ==========================================================
# Back to Dashboard
# ==========================================================

st.divider()

if st.button(
    "⬅️ Back to Dashboard",
    key="customers_back_dashboard"
):

    st.switch_page(
        "pages/AdminDashboard.py"
    )