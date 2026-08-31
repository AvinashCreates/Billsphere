import requests
import streamlit as st
from datetime import date
from collections import defaultdict

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

st.set_page_config(page_title="Billing Calendar", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"]{ background:#16231B; }
    [data-testid="stSidebar"] *{ color:white; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("# Billing Platform")
    st.caption("Admin Dashboard")
    st.divider()
    if st.button("Dashboard", icon=":material/dashboard:", use_container_width=True):
        st.switch_page("pages/AdminDashboard.py")
    if st.button("Customers", icon=":material/group:", use_container_width=True):
        st.switch_page("pages/Customers.py")
    if st.button("Plans", icon=":material/inventory_2:", use_container_width=True):
        st.switch_page("pages/Plans.py")
    if st.button("Invoices", icon=":material/receipt_long:", use_container_width=True):
        st.switch_page("pages/Invoices.py")
    if st.button("Notifications", icon=":material/notifications:", use_container_width=True):
        st.switch_page("pages/Notifications.py")
    if st.button("Billing Calendar", icon=":material/calendar_month:", use_container_width=True):
        st.rerun()
    if st.button("Profile", icon=":material/person:", use_container_width=True):
        st.switch_page("pages/Profile.py")
    st.divider()
    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        logout()
        st.switch_page("app.py")

st.title("Billing Calendar")
st.caption("Track upcoming dues, renewals, and expired subscriptions.")

try:
    response = requests.get(
        f"{API_URL}/admin/calendar/events",
        headers=get_headers(),
        params={"days_ahead": 60},
    )
except Exception as e:
    st.error(f"Failed to connect to backend server: {e}")
    st.stop()

if response.status_code != 200:
    st.error("Unable to fetch billing calendar events.")
    st.stop()

events = response.json()
events_by_date = defaultdict(list)
for e in events:
    events_by_date[e["date"]].append(e)

overdue_count = sum(1 for e in events if e["status"] == "overdue")
upcoming_count = sum(1 for e in events if e["status"] == "upcoming")

m1, m2, m3 = st.columns(3)
m1.metric("Total Events (60 days)", len(events))
m2.metric("Upcoming", upcoming_count)
m3.metric("Overdue", overdue_count)

st.divider()
st.subheader("Select a date")
selected_date = st.date_input("Date", value=date.today())
day_events = events_by_date.get(selected_date.isoformat(), [])

type_label = {
    "renewal_due": "Subscription Renewal",
    "renewal_overdue": "Subscription Renewal (Overdue)",
    "invoice_due": "Invoice Due",
    "payment_overdue": "Payment Overdue",
}

if day_events:
    for e in day_events:
        badge = "Overdue" if e["status"] == "overdue" else "Upcoming"
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.write(f"**{e['customer_name']}**")
                st.caption(f"Customer ID: {e['customer_id']}")
            with c2:
                st.write(type_label.get(e["event_type"], e["event_type"]))
                st.caption(e["reference"])
            with c3:
                st.write(f"${e['amount']:.2f}")
                st.write(badge)
else:
    st.info("No billing events on this date.")

st.divider()
st.subheader("Upcoming Billing Events")

if not events:
    st.info("No upcoming billing events in the next 60 days.")
else:
    for e in events[:50]:
        badge = "Overdue" if e["status"] == "overdue" else "Upcoming"
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c1:
                st.write(e["date"])
            with c2:
                st.write(e["customer_name"])
            with c3:
                st.write(f"{type_label.get(e['event_type'], e['event_type'])} — {e['reference']}")
            with c4:
                st.write(badge)