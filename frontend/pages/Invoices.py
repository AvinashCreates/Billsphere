import streamlit as st
import requests
from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css, render_hero

load_css()

# ---------------- Authentication & Authorization ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state.get("user", {})

if user.get("role") != "admin":
    st.error("Access Denied: Admin access required.")
    st.stop()


# ---------------- Page Config ----------------

st.set_page_config(
    page_title="Invoice Management",
    page_icon="🧾",
    layout="wide"
)


# ---------------- Blue Banner CSS ----------------

st.markdown(
    """
    <style>

    .invoice-hero-banner {
        background: linear-gradient(135deg, #2F6D4F, #1F4D38);
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
        color: #E4EFE7;
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

    if st.button("Dashboard", icon=":material/dashboard:", use_container_width=True):
        st.switch_page("pages/AdminDashboard.py")

    if st.button("Customers", icon=":material/group:", use_container_width=True):
        st.switch_page("pages/Customers.py")

    if st.button("Plans", icon=":material/inventory_2:", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("Invoices", icon=":material/receipt_long:", use_container_width=True):
        st.rerun()

    if st.button("Profile", icon=":material/person:", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        logout()
        st.switch_page("app.py")


# ---------------- Blue Hero Banner ----------------

render_hero(
    "Invoice Management",
    "Manage customer invoices, track billing statuses, and process payments from one place.",
    icon="receipt_long",
)


# ---------------- Filters & Search Section ----------------

with st.expander("Search & Filter Options", expanded=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        search_query = st.text_input(
            "Search",
            placeholder="Invoice #, customer email or username",
            key="inv_search"
        )

        status_filter = st.selectbox(
            "Invoice Status",
            ["All", "pending", "paid", "overdue", "draft", "cancelled"],
            key="inv_status"
        )

    with col2:

        payment_status_filter = st.selectbox(
            "Payment Status",
            ["All", "unpaid", "paid", "partially_paid"],
            key="inv_pay_status"
        )

        sort_by = st.selectbox(
            "Sort By",
            [
                "created_at",
                "due_date",
                "total_amount",
                "invoice_number"
            ],
            key="inv_sort_by"
        )

    with col3:

        sort_order = st.radio(
            "Sort Direction",
            ["desc", "asc"],
            horizontal=True,
            key="inv_sort_order"
        )

        page_size = st.selectbox(
            "Page Size",
            [10, 20, 50],
            index=1,
            key="inv_page_size"
        )


# ---------------- Initialize Page State ----------------

if "inv_page" not in st.session_state:
    st.session_state["inv_page"] = 1

current_page = st.session_state["inv_page"]


# ---------------- Build Query Params ----------------

params = {
    "page": current_page,
    "page_size": page_size,
    "sort_by": sort_by,
    "sort_order": sort_order,
}

if search_query.strip():
    params["search"] = search_query.strip()

if status_filter != "All":
    params["status"] = status_filter

if payment_status_filter != "All":
    params["payment_status"] = payment_status_filter


# ---------------- Fetch Invoices ----------------

try:

    response = requests.get(
        f"{API_URL}/invoices/",
        headers=get_headers(),
        params=params
    )

except Exception as e:

    st.error(f"Failed to connect to backend server: {e}")
    st.stop()


if response.status_code != 200:

    st.error("Failed to fetch invoices from backend.")
    st.stop()


data = response.json()

invoices = data.get("items", [])
total_count = data.get("total", 0)
total_pages = data.get("total_pages", 1)


# ---------------- Summary Metrics ----------------

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Total Invoices",
    total_count
)

paid_count = sum(
    1 for i in invoices
    if i.get("status") == "paid"
)

pending_count = sum(
    1 for i in invoices
    if i.get("status") == "pending"
)

overdue_count = sum(
    1 for i in invoices
    if i.get("status") == "overdue"
)

m2.metric(
    "Paid",
    paid_count
)

m3.metric(
    "Pending",
    pending_count
)

m4.metric(
    "Overdue",
    overdue_count
)

st.divider()


# ---------------- Invoice List ----------------

if not invoices:

    st.info("No invoices found matching your criteria.")

else:

    for inv in invoices:

        inv_id = inv["id"]

        inv_num = (
            inv.get("invoice_number")
            or f"INV-{inv_id:06d}"
        )

        status = inv.get(
            "status",
            "pending"
        )

        pay_status = inv.get(
            "payment_status",
            "unpaid"
        )

        total_amt = inv.get(
            "total_amount",
            0.0
        )

        customer_email = (
            inv.get("customer_email")
            or f"User #{inv['user_id']}"
        )

        customer_uname = (
            inv.get("customer_username")
            or ""
        )


        # ---------------- Status Badge Mapping ----------------

        status_badges = {

            "paid": "Paid",

            "pending": "Pending",

            "overdue": "Overdue",

            "draft": "Draft",

            "cancelled": "Cancelled"

        }

        badge = status_badges.get(
            status,
            f"{status}"
        )


        # ---------------- Invoice Card ----------------

        with st.container(border=True):

            head_col1, head_col2, head_col3, head_col4 = st.columns(
                [2, 3, 2, 2]
            )

            with head_col1:

                st.subheader(inv_num)

                st.caption(
                    f"ID: #{inv_id}"
                )


            with head_col2:

                st.write(
                    f"**Customer:** "
                    f"{customer_uname} "
                    f"(`{customer_email}`)"
                )

                created_str = (
                    inv.get("created_at", "")[:10]
                    if inv.get("created_at")
                    else "N/A"
                )

                st.caption(
                    f"Created: {created_str}"
                )


            with head_col3:

                st.metric(
                    "Total Amount",
                    f"${total_amt:.2f}"
                )


            with head_col4:

                st.write(
                    f"**Status:** {badge}"
                )

                st.write(
                    f"**Payment:** `{pay_status}`"
                )


            # ---------------- Invoice Details ----------------

            with st.expander(
                "View Full Invoice Details & Actions"
            ):

                detail_resp = requests.get(
                    f"{API_URL}/invoices/{inv_id}",
                    headers=get_headers()
                )


                if detail_resp.status_code == 200:

                    detail = detail_resp.json()

                    d_col1, d_col2 = st.columns(2)


                    # ---------------- Customer Information ----------------

                    with d_col1:

                        st.markdown(
                            "#### Customer Information"
                        )

                        cust = detail.get(
                            "customer"
                        ) or {}

                        st.write(
                            f"- **User ID:** "
                            f"{cust.get('id', 'N/A')}"
                        )

                        st.write(
                            f"- **Username:** "
                            f"{cust.get('username', 'N/A')}"
                        )

                        st.write(
                            f"- **Email:** "
                            f"{cust.get('email', 'N/A')}"
                        )


                        # ---------------- Billing Dates ----------------

                        st.markdown(
                            "#### Billing Period & Dates"
                        )

                        p_start = detail.get(
                            "billing_period_start"
                        )

                        p_end = detail.get(
                            "billing_period_end"
                        )

                        due = detail.get(
                            "due_date"
                        )

                        st.write(
                            f"- **Period Start:** "
                            f"{p_start[:10] if p_start else 'N/A'}"
                        )

                        st.write(
                            f"- **Period End:** "
                            f"{p_end[:10] if p_end else 'N/A'}"
                        )

                        st.write(
                            f"- **Due Date:** "
                            f"{due[:10] if due else 'N/A'}"
                        )


                    # ---------------- Subscription & Amount ----------------

                    with d_col2:

                        st.markdown(
                            "#### Subscription Information"
                        )

                        sub = detail.get(
                            "subscription"
                        )

                        if sub:

                            st.write(
                                f"- **Subscription ID:** "
                                f"#{sub.get('id')}"
                            )

                            st.write(
                                f"- **Plan ID:** "
                                f"#{sub.get('plan_id')}"
                            )

                            st.write(
                                f"- **Status:** "
                                f"`{sub.get('status')}`"
                            )

                        else:

                            st.write(
                                "_No active subscription linked._"
                            )


                        st.markdown(
                            "#### Amount Summary"
                        )

                        st.write(
                            f"- **Plan Fee:** "
                            f"${detail.get('plan_fee', 0.0):.2f}"
                        )

                        st.write(
                            f"- **Proration:** "
                            f"${detail.get('proration_amount', 0.0):.2f}"
                        )

                        st.write(
                            f"- **Taxes:** "
                            f"${detail.get('tax_amount', 0.0):.2f}"
                        )

                        st.write(
                            f"- **Usage Charges:** "
                            f"${detail.get('usage_charges', 0.0):.2f}"
                        )

                        st.markdown(
                            f"**Total:** "
                            f"`${detail.get('total_amount', 0.0):.2f}`"
                        )


                    # ---------------- Line Items ----------------

                    line_items = detail.get(
                        "line_items",
                        []
                    )

                    if line_items:

                        st.markdown(
                            "#### Line Items"
                        )

                        table_data = [

                            {
                                "Description": item["description"],
                                "Type": item["line_type"],
                                "Qty": item["quantity"],
                                "Unit Price ($)": f"{item['unit_price']:.2f}",
                                "Amount ($)": f"{item['amount']:.2f}"
                            }

                            for item in line_items

                        ]

                        st.table(table_data)


                    # ---------------- Payment Actions ----------------

                    st.divider()

                    act_col1, act_col2 = st.columns(
                        [2, 5]
                    )

                    with act_col1:

                        if (
                            status in ["pending", "overdue"]
                            and pay_status != "paid"
                        ):

                            if st.button(
                                "Process Payment", icon=":material/payments:",
                                key=f"pay_btn_{inv_id}",
                                use_container_width=True
                            ):

                                pay_resp = requests.post(
                                    f"{API_URL}/invoices/{inv_id}/pay",
                                    headers=get_headers()
                                )


                                if pay_resp.status_code == 200:

                                    res = pay_resp.json()

                                    st.success(
                                        f"{res.get('message', 'Payment processed successfully!')}"
                                    )

                                    st.rerun()

                                else:

                                    try:

                                        err_detail = (
                                            pay_resp.json()
                                            .get(
                                                "detail",
                                                "Payment failed."
                                            )
                                        )

                                    except Exception:

                                        err_detail = (
                                            "Payment processing error."
                                        )

                                    st.error(
                                        f"{err_detail}"
                                    )


                        elif status == "paid":

                            st.success(
                                "Invoice is fully paid."
                            )

                        else:

                            st.info(
                                f"Status: {status}"
                            )

                else:

                    st.error(
                        "Failed to load detailed invoice information."
                    )


# ---------------- Pagination Controls ----------------

st.divider()

p_col1, p_col2, p_col3 = st.columns(
    [2, 3, 2]
)


with p_col1:

    if current_page > 1:

        if st.button("Previous Page", icon=":material/arrow_back:"):

            st.session_state["inv_page"] -= 1

            st.rerun()


with p_col2:

    st.write(
        f"Page **{current_page}** "
        f"of **{max(1, total_pages)}** "
        f"(Total: {total_count} invoices)"
    )


with p_col3:

    if current_page < total_pages:

        if st.button("Next Page", icon=":material/arrow_forward:"):

            st.session_state["inv_page"] += 1

            st.rerun()