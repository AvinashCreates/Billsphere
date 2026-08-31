import requests
import streamlit as st

from config import API_URL
from styles import load_css

FREE_PLAY_LIMIT = 2

st.set_page_config(page_title="StreamFlix", layout="wide")

load_css()

if "streamflix_plays" not in st.session_state:
    st.session_state["streamflix_plays"] = 0

is_logged_in = "token" in st.session_state
user = st.session_state.get("user", {})

is_premium = False
plan_name = None

if is_logged_in:
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        resp = requests.get(f"{API_URL}/subscriptions/my", headers=headers)
        if resp.status_code == 200:
            sub = resp.json()
            if sub and sub.get("status") == "active":
                is_premium = True
                plan_resp = requests.get(f"{API_URL}/plans/{sub['plan_id']}", headers=headers)
                if plan_resp.status_code == 200:
                    plan_name = plan_resp.json().get("name")
    except Exception:
        pass

# ---------------- Styling ----------------

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: #16231B; }
    [data-testid="stSidebar"] { background: #1F2A22; }
    [data-testid="stSidebar"] * { color: #DCE5DD; }
    .sf-hero {
        background: linear-gradient(135deg, #3D2C55, #5B3E73);
        padding: 40px;
        border-radius: 16px;
        margin-bottom: 28px;
    }
    .sf-hero h1 { color: white; font-size: 36px; margin-bottom: 6px; }
    .sf-hero p { color: #ede9fe; font-size: 16px; }
    .sf-card {
        background: #16231B;
        border-radius: 12px;
        padding: 18px;
        color: #DCE5DD;
        height: 100%;
    }
    .sf-card h4 { margin-bottom: 6px; }
    .sf-card p { color: #5B6B5F; font-size: 13px; }
    .sf-badge-premium {
        background: #2F6D4F; color: white; padding: 4px 12px;
        border-radius: 999px; font-size: 13px; font-weight: 600;
    }
    .sf-badge-free {
        background: #1F2A22; color: #DCE5DD; padding: 4px 12px;
        border-radius: 999px; font-size: 13px; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### StreamFlix")
    st.caption("Demo SaaS platform — powered by our Billing Platform")
    st.divider()

    if is_logged_in:
        st.write(f"Signed in as **{user.get('username', 'User')}**")
        if is_premium:
            st.markdown('<span class="sf-badge-premium">Premium Member</span>', unsafe_allow_html=True)
            if plan_name:
                st.caption(f"Plan: {plan_name}")
        else:
            st.markdown('<span class="sf-badge-free">Free Plan</span>', unsafe_allow_html=True)
    else:
        st.write("Browsing as guest")
        st.markdown('<span class="sf-badge-free">Free Preview</span>', unsafe_allow_html=True)

    st.divider()

    if is_logged_in:
        if st.button("Back to Billing Platform", icon=":material/arrow_back:", use_container_width=True):
            st.switch_page("pages/CustomerDashboard.py")
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            for key in ["token", "user"]:
                st.session_state.pop(key, None)
            st.switch_page("app.py")
    else:
        if st.button("Log In", icon=":material/login:", use_container_width=True):
            st.switch_page("pages/Login.py")
        if st.button("Create Account", icon=":material/person_add:", use_container_width=True):
            st.switch_page("pages/Register.py")

# ---------------- Hero ----------------

st.markdown(
    """
    <div class="sf-hero">
        <h1>StreamFlix</h1>
        <p>A demo streaming platform showing how an external SaaS product
        integrates with our Billing Platform for subscriptions and
        feature gating. Try it free — no account needed to start.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Catalog ----------------

TITLES = [
    ("The Silent Horizon", "Sci-Fi Drama"),
    ("Kitchen Diaries", "Documentary"),
    ("Nightfall City", "Thriller"),
    ("Coastal Dreams", "Romance"),
    ("The Last Algorithm", "Sci-Fi"),
    ("Mountain Echoes", "Adventure"),
]

st.subheader("Featured Titles")

cols = st.columns(3)

for i, (title, genre) in enumerate(TITLES):
    with cols[i % 3]:
        st.markdown(
            f"""<div class="sf-card"><h4>{title}</h4><p>{genre}</p></div>""",
            unsafe_allow_html=True,
        )

        locked = (not is_premium) and (st.session_state["streamflix_plays"] >= FREE_PLAY_LIMIT)

        if locked:
            st.button("Locked", icon=":material/lock:", key=f"locked_{i}", disabled=True, use_container_width=True)
        else:
            if st.button("Play", icon=":material/play_circle:", key=f"play_{i}", use_container_width=True):
                if not is_premium:
                    st.session_state["streamflix_plays"] += 1
                st.success(f"Now playing: {title}")

        st.write("")

# ---------------- Upgrade wall ----------------

st.divider()

if is_premium:
    st.success("You're on a Premium plan — unlimited plays, full catalog access, and no ads.")

else:
    remaining = max(0, FREE_PLAY_LIMIT - st.session_state["streamflix_plays"])

    if remaining > 0:
        st.info(f"Free preview: {remaining} play(s) remaining.")
    else:
        st.warning(
            "You've reached your free preview limit. Upgrade to Premium "
            "for unlimited plays, the full catalog, and no ads."
        )

    st.subheader("Upgrade to Premium")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="sf-card"><h4>Unlimited Plays</h4><p>No daily limits on what you can watch.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="sf-card"><h4>Full Catalog</h4><p>Access to every title, including new releases.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="sf-card"><h4>No Ads</h4><p>Uninterrupted viewing, every time.</p></div>', unsafe_allow_html=True)

    st.write("")

    if is_logged_in:
        if st.button("Upgrade Now", icon=":material/upgrade:", type="primary", use_container_width=True):
            st.switch_page("pages/Plans.py")
    else:
        st.info("Sign in or create an account to upgrade to Premium.")
        u1, u2 = st.columns(2)
        with u1:
            if st.button("Log In", icon=":material/login:", type="primary", use_container_width=True, key="upgrade_login"):
                st.switch_page("pages/Login.py")
        with u2:
            if st.button("Create Account", icon=":material/person_add:", use_container_width=True, key="upgrade_register"):
                st.switch_page("pages/Register.py")