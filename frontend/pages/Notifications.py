import requests
import streamlit as st

from config import API_URL
from utils import get_headers

# ---------------- Authentication ----------------

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

if "user" not in st.session_state:
    st.switch_page("pages/Login.py")

user = st.session_state["user"]

# ---------------- Page Config ----------------

st.set_page_config(page_title="Notifications", page_icon="🔔", layout="wide")

# ---------------- Styling ----------------

st.markdown(
    """
    <style>

    .notif-header {
        margin-bottom: 4px;
    }

    .notif-subtext {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 24px;
    }

    .notif-type-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        background: #eef2ff;
        color: #4338ca;
    }

    .notif-status-sent { color: #059669; font-weight: 600; font-size: 13px; }
    .notif-status-pending { color: #b45309; font-weight: 600; font-size: 13px; }
    .notif-status-failed { color: #dc2626; font-weight: 600; font-size: 13px; }

    .notif-unread-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #2563eb;
        margin-right: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

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
    if st.button("Refresh", use_container_width=True):
        st.rerun()

with col_mark_all:
    if not view_all and st.button("Mark all as read", use_container_width=True):
        requests.post(
            f"{API_URL}/notifications/read-all",
            headers=get_headers(),
        )
        st.rerun()

endpoint = "/notifications/all" if view_all else "/notifications/"

response = requests.get(f"{API_URL}{endpoint}", headers=get_headers())

if response.status_code != 200:
    st.error("Unable to fetch notifications.")
    st.stop()

notifications = response.json()

if not notifications:
    st.info("No notifications yet.")
    st.stop()


# ==========================================================
# DISPLAY NOTIFICATIONS
# ==========================================================

for note in notifications:

    with st.container(border=True):
        col1, col2, col3 = st.columns([5, 2, 1])

        with col1:
            unread_dot = (
                "<span class='notif-unread-dot'></span>"
                if not note["is_read"] and not view_all
                else ""
            )

            st.markdown(
                f"{unread_dot}"
                f"<span class='notif-type-badge'>{note['type'].replace('_', ' ')}</span>"
                f"&nbsp;&nbsp;<strong>{note['title']}</strong>",
                unsafe_allow_html=True,
            )
            st.write(note["message"])

            if view_all:
                st.caption(f"User ID: {note['user_id']}")

        with col2:
            status_class = STATUS_CLASS.get(note["status"], "")
            st.markdown(
                f"<span class='{status_class}'>{note['status'].capitalize()}</span>",
                unsafe_allow_html=True,
            )
            st.caption(note["created_at"][:19].replace("T", " "))

        with col3:
            if not view_all and not note["is_read"]:
                if st.button("Mark read", key=f"read_{note['id']}"):
                    requests.post(
                        f"{API_URL}/notifications/{note['id']}/read",
                        headers=get_headers(),
                    )
                    st.rerun()

st.divider()

if st.button("Back"):
    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/CustomerDashboard.py")
