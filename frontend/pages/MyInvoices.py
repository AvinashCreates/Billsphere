import requests
import streamlit as st

from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css

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
        background:#0F172A;
    }

    [data-testid="stSidebar"] *{
        color:white;
    }

    .invoice-hero-banner {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        padding: 35px 40px;
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }

    .invoice-hero-banner h1 { color: white; font-size: 32px; font-weight: 700; margin-bottom: 10px; }
    .invoice-hero-banner p { color: #e0ecff; font-size: 17px; margin: 0; }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar ----------------

with st.sidebar:

    st.markdown("# 💳 Billing Platform")
    st.caption("Customer Dashboard")
    st.divider()

    st.write(f"👤 **{user.get('username')}**")
    st.write("👤 Customer")

    st.divider()

    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/CustomerDashboard.py")

    if st.button("📦 Available Plans", use_container_width=True):
        st.switch_page("pages/Plans.py")

    if st.button("🔄 My Subscription", use_container_width=True):
        st.switch_page("pages/Subscriptions.py")

    if st.button("🧾 My Invoices", use_container_width=True):
        st.rerun()

    if st.button("👤 My Profile", use_container_width=True):
        st.switch_page("pages/Profile.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Header ----------------

st.markdown(
    """
    <div class="invoice-hero-banner">
        <h1>My Invoices 🧾</h1>
        <p>Invoices are generated automatically whenever you subscribe or renew a plan.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Filters ----------------

with st.expander("🔍 Filter", expanded=False):

    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Invoice Status",
            ["All", "pending", "paid", "overdue", "draft", "cancelled"],
        )

    with col2:
        payment_status_filter = st.selectbox(
            "Payment Status",
            ["All", "unpaid", "paid", "partially_paid"],
        )

if "myinv_page" not in st.session_state:
    st.session_state["myinv_page"] = 1

current_page = st.session_state["myinv_page"]

params = {"page": current_page, "page_size": 10}

if status_filter != "All":
    params["status"] = status_filter

if payment_status_filter != "All":
    params["payment_status"] = payment_status_filter

# ---------------- Fetch invoices ----------------

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

# ---------------- Summary ----------------

m1, m2, m3 = st.columns(3)
m1.metric("Total Invoices", total_count)
m2.metric("🟢 Paid", sum(1 for i in invoices if i.get("status") == "paid"))
m3.metric("🟡 Pending / Overdue", sum(1 for i in invoices if i.get("status") in ("pending", "overdue")))

st.divider()

# ---------------- List ----------------

if not invoices:

    st.info("No invoices yet. Subscribe to a plan to generate your first invoice.")

    if st.button("📦 Browse Plans", type="primary"):
        st.switch_page("pages/Plans.py")

else:

    status_badges = {
        "paid": "🟢 Paid",
        "pending": "🟡 Pending",
        "overdue": "🔴 Overdue",
        "draft": "⚪ Draft",
        "cancelled": "❌ Cancelled",
    }

    for inv in invoices:

        inv_id = inv["id"]
        inv_num = inv.get("invoice_number") or f"INV-{inv_id:06d}"
        status = inv.get("status", "pending")
        pay_status = inv.get("payment_status", "unpaid")
        total_amt = inv.get("total_amount", 0.0)
        badge = status_badges.get(status, f"⚪ {status}")

        with st.container(border=True):

            c1, c2, c3 = st.columns([2, 3, 2])

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

            with st.expander("📄 View Full Invoice"):

                detail_resp = requests.get(
                    f"{API_URL}/invoices/my/{inv_id}",
                    headers=get_headers(),
                )

                if detail_resp.status_code != 200:
                    st.error("Unable to load invoice details.")
                    continue

                detail = detail_resp.json()

                d1, d2 = st.columns(2)

                with d1:
                    st.markdown("#### 📅 Billing Period")
                    p_start = detail.get("billing_period_start")
                    p_end = detail.get("billing_period_end")
                    st.write(f"- **Start:** {p_start[:10] if p_start else 'N/A'}")
                    st.write(f"- **End:** {p_end[:10] if p_end else 'N/A'}")
                    st.write(f"- **Due Date:** {(detail.get('due_date') or '')[:10] or 'N/A'}")

                with d2:
                    st.markdown("#### 💰 Amount Summary")
                    st.write(f"- **Plan Fee:** ${detail.get('plan_fee', 0.0):.2f}")
                    st.write(f"- **Proration:** ${detail.get('proration_amount', 0.0):.2f}")
                    st.write(f"- **Taxes:** ${detail.get('tax_amount', 0.0):.2f}")
                    st.write(f"- **Usage Charges:** ${detail.get('usage_charges', 0.0):.2f}")
                    st.markdown(f"**Total: `${detail.get('total_amount', 0.0):.2f}`**")

                line_items = detail.get("line_items", [])

                if line_items:
                    st.markdown("#### 📋 Line Items")
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

# ---------------- Pagination ----------------

st.divider()

p1, p2, p3 = st.columns([2, 3, 2])

with p1:
    if current_page > 1 and st.button("⬅ Previous"):
        st.session_state["myinv_page"] -= 1
        st.rerun()

with p2:
    st.write(f"Page **{current_page}** of **{max(1, total_pages)}** (Total: {total_count})")

with p3:
    if current_page < total_pages and st.button("Next ➡"):
        st.session_state["myinv_page"] += 1
        st.rerun()
