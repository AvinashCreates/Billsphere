import requests
import streamlit as st

from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css, render_hero

load_css()

# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state.get("user", {})

if user.get("role") != "user":
    st.error("Access Denied: Customer access required.")
    st.stop()

# ---------------- Page Config ----------------

st.set_page_config(
    page_title="My Invoices",
    page_icon="🧾",
    layout="wide",
)

# ---------------- Styling ----------------

st.markdown(
    """
    <style>
    [data-testid="stSidebar"]{
        background:#16231B;
    }

    [data-testid="stSidebar"] *{
        color:white;
    }

    .invoice-hero-banner {
        background: linear-gradient(135deg, #2F6D4F, #1F4D38);
        padding: 35px 40px;
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }

    .invoice-hero-banner h1 { color: white; font-size: 32px; font-weight: 700; margin-bottom: 10px; }
    .invoice-hero-banner p { color: #E4EFE7; font-size: 17px; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar ----------------

with st.sidebar:
    st.markdown("# Billing Platform")
    st.caption("Customer Dashboard")
    st.divider()

    st.write(f"**{user.get('username')}**")
    st.write("Customer")

    st.divider()

    if st.button("Dashboard", icon=":material/dashboard:", use_container_width=True):
        st.switch_page("pages/CustomerDashboard.py")

    if st.button("Available Plans", icon=":material/inventory_2:", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("My Subscription", icon=":material/autorenew:", use_container_width=True):
        st.switch_page("pages/Subscriptions.py")

    if st.button("My Invoices", icon=":material/receipt_long:", use_container_width=True):
        st.rerun()

    if st.button("My Profile", icon=":material/person:", use_container_width=True):
        st.switch_page("pages/Profile.py")

    if st.button("Notifications", icon=":material/notifications:", use_container_width=True):
            st.switch_page("pages/Notifications.py")
    
    st.divider()

    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Header ----------------

render_hero(
    "My Invoices",
    "Invoices are generated automatically whenever you subscribe or renew a plan.",
    icon="receipt_long",
)

# ---------------- Filters & State ----------------

if "myinv_page" not in st.session_state:
    st.session_state["myinv_page"] = 1

def reset_page():
    st.session_state["myinv_page"] = 1

with st.expander("Filter", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Invoice Status",
            ["All", "pending", "paid", "overdue", "draft", "cancelled"],
            on_change=reset_page,
        )

    with col2:
        payment_status_filter = st.selectbox(
            "Payment Status",
            ["All", "unpaid", "paid", "partially_paid"],
            on_change=reset_page,
        )

current_page = st.session_state["myinv_page"]
params = {"page": current_page, "page_size": 10}

if status_filter != "All":
    params["status"] = status_filter

if payment_status_filter != "All":
    params["payment_status"] = payment_status_filter

# ---------------- Fetch Invoices ----------------

try:
    response = requests.get(
        f"{API_URL}/invoices/my",
        headers=get_headers(),
        params=params,
    )
except Exception as e:
    st.error(f"Failed to connect to backend server: {e}")
    st.stop()

if response.status_code != 200:
    st.error("Unable to fetch your invoices.")
    st.stop()

data = response.json()
invoices = data.get("items", [])
total_count = data.get("total", 0)
total_pages = data.get("total_pages", 1)

# ---------------- Summary Metrics ----------------

m1, m2, m3 = st.columns(3)
m1.metric("Total Invoices", total_count)
m2.metric("Paid", sum(1 for i in invoices if i.get("status") == "paid"))
m3.metric("Pending / Overdue", sum(1 for i in invoices if i.get("status") in ("pending", "overdue")))

st.divider()

# ---------------- Invoice List ----------------

if not invoices:
    st.info("No invoices yet. Subscribe to a plan to generate your first invoice.")
    if st.button("Browse Plans", icon=":material/inventory_2:", type="primary"):
        st.switch_page("pages/Plans.py")

else:
    status_badges = {
        "paid": "Paid",
        "pending": "Pending",
        "overdue": "Overdue",
        "draft": "Draft",
        "cancelled": "Cancelled",
    }

    for inv in invoices:
        inv_id = inv["id"]
        inv_num = inv.get("invoice_number") or f"INV-{inv_id:06d}"
        status = inv.get("status", "pending")
        pay_status = inv.get("payment_status", "unpaid")
        total_amt = inv.get("total_amount", 0.0)
        badge = status_badges.get(status, f"{status}")

        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 3, 2.5])

            with c1:
                st.subheader(inv_num)
                st.caption(f"ID: #{inv_id}")

            with c2:
                created_str = (inv.get("created_at", "") or "")[:10] or "N/A"
                st.write(f"**Created:** {created_str}")
                due_str = (inv.get("due_date", "") or "")[:10] or "N/A"
                st.write(f"**Due:** {due_str}")

            with c3:
                st.metric("Total", f"${total_amt:.2f}")
                st.write(f"**Status:** {badge}")
                st.write(f"**Payment:** `{pay_status}`")

                # --- PDF Download Button next to Payment Status ---
                pdf_url = f"{API_URL}/invoices/{inv_id}/download"
                try:
                    pdf_resp = requests.get(pdf_url, headers=get_headers())
                    if pdf_resp.status_code == 200 and pdf_resp.content:
                        st.download_button(
                            label="Download PDF",
                            data=pdf_resp.content,
                            file_name=f"invoice_{inv_num}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{inv_id}",
                            type="secondary",
                            use_container_width=True,
                        )
                    elif pdf_resp.status_code == 401:
                        st.caption("Session expired")
                    else:
                        st.caption("PDF unavailable")
                except Exception:
                    st.caption("PDF error")

                # Pay Now Button
                if status in ("pending", "overdue") and pay_status == "unpaid":
                    if st.button("Pay Now", key=f"pay_{inv_id}", type="primary", use_container_width=True):
                        st.session_state[f"show_payment_{inv_id}"] = True

            # Payment Form Modal/Container
            if st.session_state.get(f"show_payment_{inv_id}", False):
                st.markdown("### Make Payment")

                payment_method = st.selectbox(
                    "Payment Method",
                    ["upi", "card", "bank_transfer"],
                    key=f"method_{inv_id}",
                )

                placeholder_text = (
                    "Enter UPI ID" if payment_method == "upi"
                    else "Enter mock card number" if payment_method == "card"
                    else "Enter bank reference"
                )

                payment_identifier = st.text_input(
                    "Payment Details",
                    placeholder=placeholder_text,
                    key=f"payment_identifier_{inv_id}",
                )

                col_pay, col_cancel = st.columns(2)

                with col_pay:
                    if st.button(
                        "Pay Now",
                        icon=":material/payments:",
                        key=f"confirm_pay_{inv_id}",
                        type="primary",
                    ):
                        if not payment_identifier.strip():
                            st.warning("Please enter your payment details.")
                        else:
                            try:
                                payment_response = requests.post(
                                    f"{API_URL}/payments/mock",
                                    headers=get_headers(),
                                    json={
                                        "invoice_id": inv_id,
                                        "payment_method": payment_method,
                                        "payment_identifier": payment_identifier,
                                    },
                                )

                                if payment_response.status_code == 200:
                                    result = payment_response.json()
                                    if result.get("success"):
                                        st.success(result.get("message", "Payment successful."))
                                        st.session_state[f"show_payment_{inv_id}"] = False
                                        st.rerun()
                                    else:
                                        st.error(result.get("message", "Payment failed."))
                                else:
                                    try:
                                        error_detail = payment_response.json().get("detail", "Payment failed.")
                                    except Exception:
                                        error_detail = "Payment failed."
                                    st.error(error_detail)

                            except Exception as e:
                                st.error(f"Unable to process payment: {e}")

                with col_cancel:
                    if st.button(
                        "Cancel",
                        icon=":material/cancel:",
                        key=f"cancel_pay_{inv_id}",
                    ):
                        st.session_state[f"show_payment_{inv_id}"] = False
                        st.rerun()

            # Expandable Details
            with st.expander("View Full Invoice"):
                detail_resp = requests.get(
                    f"{API_URL}/invoices/my/{inv_id}",
                    headers=get_headers(),
                )

                if detail_resp.status_code != 200:
                    st.error("Unable to load invoice details.")
                else:
                    detail = detail_resp.json()
                    st.divider()

                    # --- Details Summary ---
                    d1, d2 = st.columns(2)

                    with d1:
                        st.markdown("#### Billing Period")
                        p_start = detail.get("billing_period_start")
                        p_end = detail.get("billing_period_end")
                        st.write(f"- **Start:** {p_start[:10] if p_start else 'N/A'}")
                        st.write(f"- **End:** {p_end[:10] if p_end else 'N/A'}")
                        st.write(f"- **Due Date:** {(detail.get('due_date') or '')[:10] or 'N/A'}")

                    with d2:
                        st.markdown("#### Amount Summary")
                        st.write(f"- **Plan Fee:** ${detail.get('plan_fee', 0.0):.2f}")
                        st.write(f"- **Proration:** ${detail.get('proration_amount', 0.0):.2f}")
                        st.write(f"- **Taxes:** ${detail.get('tax_amount', 0.0):.2f}")
                        st.write(f"- **Usage Charges:** ${detail.get('usage_charges', 0.0):.2f}")
                        st.markdown(f"**Total: `${detail.get('total_amount', 0.0):.2f}`**")

                    line_items = detail.get("line_items", [])
                    if line_items:
                        st.markdown("#### Line Items")
                        st.table([
                            {
                                "Description": item["description"],
                                "Type": item["line_type"],
                                "Qty": item["quantity"],
                                "Unit Price ($)": f"{item['unit_price']:.2f}",
                                "Amount ($)": f"{item['amount']:.2f}",
                            }
                            for item in line_items
                        ])

# ---------------- Pagination Controls ----------------

st.divider()

p1, p2, p3 = st.columns([2, 3, 2])

with p1:
    if current_page > 1 and st.button("Previous", icon=":material/arrow_back:"):
        st.session_state["myinv_page"] -= 1
        st.rerun()

with p2:
    st.write(f"Page **{current_page}** of **{max(1, total_pages)}** (Total: {total_count})")

with p3:
    if current_page < total_pages and st.button("Next", icon=":material/arrow_forward:"):
        st.session_state["myinv_page"] += 1
        st.rerun()