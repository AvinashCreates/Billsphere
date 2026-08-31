import requests
import streamlit as st

from config import API_URL
from utils import get_headers
from auth import logout
from styles import load_css

load_css()

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state.get("user", {})

if user.get("role") != "admin":
    st.error("Access Denied: Admin access required.")
    st.stop()

st.set_page_config(page_title="StreamFlix Analytics", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"]{ background:#0F172A; }
    [data-testid="stSidebar"] *{ color:white; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("# Billing Platform")
    st.caption("Admin Dashboard")
    st.divider()
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/AdminDashboard.py")
    if st.button("Billing Calendar", use_container_width=True):
        st.switch_page("pages/BillingCalendar.py")
    
    if st.button("StreamFlix Analytics", use_container_width=True):
        st.rerun()
    st.divider()
    if st.button("Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

st.title("StreamFlix Analytics")
st.caption(
    "How our Billing Platform gives the StreamFlix team visibility into "
    "their own subscribers — pulled live from the same billing data, "
    "since every StreamFlix Premium user is a real subscriber here."
)

try:
    customers_resp = requests.get(
        f"{API_URL}/customers/",
        headers=get_headers(),
        params={"page": 1, "page_size": 100},
    )
    total_customers = 0
    if customers_resp.status_code == 200:
        cdata = customers_resp.json()
        total_customers = cdata.get("total_customers", len(cdata) if isinstance(cdata, list) else 0)

    subs_resp = requests.get(f"{API_URL}/subscriptions/", headers=get_headers())
    active_subs = []
    if subs_resp.status_code == 200:
        sdata = subs_resp.json()
        subs_list = sdata if isinstance(sdata, list) else sdata.get("items", [])
        active_subs = [s for s in subs_list if s.get("status") == "active"]

    invoices_resp = requests.get(
        f"{API_URL}/invoices/",
        headers=get_headers(),
        params={"page": 1, "page_size": 20, "sort_by": "created_at", "sort_order": "desc"},
    )
    recent_invoices = []
    if invoices_resp.status_code == 200:
        idata = invoices_resp.json()
        recent_invoices = idata.get("items", [])

except Exception as e:
    st.error(f"Failed to load analytics: {e}")
    st.stop()

conversion_rate = (len(active_subs) / total_customers * 100) if total_customers else 0

m1, m2, m3 = st.columns(3)
m1.metric("Total Registered Users", total_customers)
m2.metric("Premium Subscribers", len(active_subs))
m3.metric("Conversion Rate", f"{conversion_rate:.1f}%")

st.divider()
st.subheader("Recent Upgrades")

paid_invoices = [inv for inv in recent_invoices if inv.get("payment_status") == "paid"]

if not paid_invoices:
    st.info("No upgrades yet.")
else:
    for inv in paid_invoices[:10]:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.write(f"**{inv.get('invoice_number', 'N/A')}**")
                st.caption((inv.get("created_at", "") or "")[:10])
            with c2:
                st.write(f"User ID: {inv.get('user_id', 'N/A')}")
            with c3:
                st.write(f"${inv.get('total_amount', 0.0):.2f}")

st.divider()
st.caption(
    "This dashboard demonstrates the Billing Platform → SaaS integration: "
    "StreamFlix's own admin can monitor subscriber growth and revenue "
    "without building any billing logic themselves."
)