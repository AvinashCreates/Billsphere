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

st.set_page_config(page_title="Notifications", layout="wide")

st.title("Notifications")

TYPE_ICONS = {
    "subscription": "📦",
    "invoice": "🧾",
    "payment_success": "✅",
    "payment_failure": "⚠️",
    "renewal": "🔔",
    "expiry": "⏰",
    "general": "📣",
}


# ==========================================================
# ADMIN: SEND TEST NOTIFICATION (verifies Redis/Celery pipeline)
# ==========================================================

if user["role"] == "admin":
    with st.expander("🧪 Send Test Notification"):
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
    if st.button("🔄 Refresh"):
        st.rerun()

with col_mark_all:
    if not view_all and st.button("✅ Mark all as read"):
        requests.put(
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
    icon = TYPE_ICONS.get(note["type"], "🔔")

    with st.container(border=True):
        col1, col2, col3 = st.columns([5, 2, 1])

        with col1:
            label = f"{icon} **{note['title']}**"
            if not note["is_read"] and not view_all:
                label += "  🔵"
            st.markdown(label)
            st.write(note["message"])

            if view_all:
                st.caption(f"User ID: {note['user_id']}")

        with col2:
            status_color = {
                "sent": "🟢",
                "pending": "🟡",
                "failed": "🔴",
            }.get(note["status"], "⚪")

            st.write(f"{status_color} {note['status'].capitalize()}")
            st.caption(note["created_at"][:19].replace("T", " "))

        with col3:
            if not view_all and not note["is_read"]:
                if st.button("Mark read", key=f"read_{note['id']}"):
                    requests.put(
                        f"{API_URL}/notifications/{note['id']}/read",
                        headers=get_headers(),
                    )
                    st.rerun()

st.divider()

if st.button("Back"):
    if user["role"] == "admin":
        st.switch_page("pages/AdminDashboard.py")
    else:
        st.switch_page("pages/UserDashboard.py")