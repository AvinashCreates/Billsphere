import requests
import streamlit as st

from config import API_URL
from utils import get_headers
from styles import load_css
from auth import logout

# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

# ---------------- Page Config ----------------

st.set_page_config(page_title="Notifications", page_icon="🔔", layout="wide")

load_css()
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
        st.switch_page("pages/MyInvoices.py")
        

    if st.button("My Profile", icon=":material/person:", use_container_width=True):
        st.switch_page("pages/Profile.py")

    if st.button("Notifications", icon=":material/notifications:", use_container_width=True):
            st.rerun()
    

    st.divider()

    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ---------------- Styling ----------------



st.markdown("<h1 class='notif-header'>Notifications</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='notif-subtext'>Stay updated about payments, invoices, subscriptions and renewals.</p>",
    unsafe_allow_html=True,
)

STATUS_CLASS = {
    "sent": "notif-status-sent",
    "pending": "notif-status-pending",
    "failed": "notif-status-failed",
}


# ==========================================================
# ADMIN: SEND TEST NOTIFICATION (verifies Redis/Celery pipeline)
# ==========================================================

if user["role"] == "admin":
    with st.expander("Send Test Notification"):
        with st.form("send_test_notification_form"):
            target_user_id = st.number_input(
                "User ID", min_value=1, step=1
            )
            title = st.text_input("Title", value="Test Notification")
            message = st.text_area(
                "Message",
                value="This is a test notification from the Notification System.",
            )

            submitted = st.form_submit_button("Send")

            if submitted:
                response = requests.post(
                    f"{API_URL}/notifications/test",
                    json={
                        "user_id": int(target_user_id),
                        "title": title,
                        "message": message,
                    },
                    headers=get_headers(),
                )

                if response.status_code == 200:
                    st.success(
                        "Notification queued. A running Celery worker "
                        "will pick it up from Redis shortly."
                    )
                else:
                    try:
                        st.error(response.json()["detail"])
                    except Exception:
                        st.error("Unable to send notification.")

    st.divider()


# ==========================================================
# FETCH NOTIFICATIONS
# ==========================================================

view_all = False

if user["role"] == "admin":
    view_all = st.toggle("View all users' notifications (history)", value=False)

col_refresh, col_mark_all = st.columns([1, 1])

with col_refresh:
    if st.button("Refresh", icon=":material/refresh:", use_container_width=True):
        st.rerun()

with col_mark_all:
    if not view_all and st.button("Mark all as read", icon=":material/done_all:", use_container_width=True):
        mark_resp = requests.post(
            f"{API_URL}/notifications/read-all",
            headers=get_headers(),
        )
        if mark_resp.status_code == 200:
            st.rerun()
        else:
            st.error(f"Could not mark all as read: {mark_resp.status_code} — {mark_resp.text}")

endpoint = "/notifications/all" if view_all else "/notifications/"

response = requests.get(f"{API_URL}{endpoint}", headers=get_headers())

if response.status_code != 200:
    st.error(f"Unable to fetch notifications: {response.status_code} — {response.text}")
    st.stop()

notif_data = response.json()
# Defensive: handle either a plain list or a paginated {"items": [...]} shape,
# matching the pattern already used for /invoices/ and /customers/.
notifications = notif_data if isinstance(notif_data, list) else notif_data.get("items", [])

if not notifications:
    st.info("No notifications yet.")
    st.stop()


# ==========================================================
# DISPLAY NOTIFICATIONS
# ==========================================================

for note in notifications:

    with st.container(border=True):
        col1, col2, col3 = st.columns([5, 2, 1])

        note_type = (note.get("type") or "notification").replace("_", " ")
        note_title = note.get("title") or "Notification"
        note_message = note.get("message") or ""
        note_status = note.get("status") or "pending"
        note_is_read = bool(note.get("is_read", False))
        note_created = note.get("created_at") or ""
        note_id = note.get("id")

        with col1:
            unread_dot = (
                "<span class='notif-unread-dot'></span>"
                if not note_is_read and not view_all
                else ""
            )

            st.markdown(
                f"{unread_dot}"
                f"<span class='notif-type-badge'>{note_type}</span>"
                f"&nbsp;&nbsp;<strong>{note_title}</strong>",
                unsafe_allow_html=True,
            )
            st.write(note_message)

            if view_all:
                st.caption(f"User ID: {note.get('user_id', 'N/A')}")

        with col2:
            status_class = STATUS_CLASS.get(note_status, "")
            st.markdown(
                f"<span class='{status_class}'>{note_status.capitalize()}</span>",
                unsafe_allow_html=True,
            )
            st.caption(note_created[:19].replace("T", " ") if note_created else "N/A")

        with col3:
            if not view_all and not note_is_read and note_id is not None:
                if st.button("Mark read", icon=":material/check:", key=f"read_{note_id}"):
                    requests.post(
                        f"{API_URL}/notifications/{note_id}/read",
                        headers=get_headers(),
                    )
                    st.rerun()

st.divider()

if st.button("Back", icon=":material/arrow_back:"):
    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/CustomerDashboard.py")