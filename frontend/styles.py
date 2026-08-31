import streamlit as st


def load_css():

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

    /* ================================================
       DESIGN TOKENS
       ================================================ */
    :root {
        --bg-page:        #F6F8F4;
        --surface:        #FFFFFF;
        --text-primary:   #1F2A22;
        --text-secondary: #5B6B5F;
        --border:         #DCE5DD;

        --accent:         #2F6D4F;
        --accent-dark:    #1F4D38;
        --accent-tint:    #E4EFE7;

        --sidebar-bg:     #16231B;
        --sidebar-text:   #E7EFE9;

        --status-success: #2F6D4F;
        --status-warning: #B45309;
        --status-danger:  #B3453B;
        --status-tint-success: #E4EFE7;
        --status-tint-warning: #FBF0DF;
        --status-tint-danger:  #F6E4E2;

        --transition-fast: 0.15s ease;
        --transition-med:  0.25s ease;
    }

    /* Hide Streamlit default navigation */
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebarHeader"] { display: none; }

    /* ================================================
       ONE DELIBERATE PAGE-LOAD MOMENT
       A single quiet fade-up on the main content area when
       a page first renders. Not applied to individual
       widgets/cards -- one orchestrated entrance, not
       scattered animation.
       ================================================ */
    @keyframes appFadeUp {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    section[data-testid="stMain"] .block-container,
    .main .block-container {
        animation: appFadeUp 0.35s ease-out;
    }

    @media (prefers-reduced-motion: reduce) {
        section[data-testid="stMain"] .block-container,
        .main .block-container {
            animation: none;
        }
    }

    /* ================================================
       MATERIAL SYMBOLS (used inside raw HTML blocks --
       hero banners -- where Streamlit's native :material/
       shortcode does not apply)
       ================================================ */
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 28px;
        line-height: 1;
        vertical-align: middle;
        display: inline-block;
    }

    /* ================================================
       PAGE TITLES
       ================================================ */
    .app-heading {
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }

    /* ================================================
       HERO / PAGE HEADER
       ================================================ */
    .app-hero {
        background: var(--accent);
        padding: 28px 36px;
        border-radius: 14px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 18px;
    }

    .app-hero .app-hero-icon {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .app-hero .app-hero-icon .material-symbols-outlined {
        color: #FFFFFF;
        font-size: 26px;
    }

    .app-hero h1 {
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 600;
        color: #FFFFFF;
        font-size: 28px;
        margin: 0 0 4px 0;
    }

    .app-hero p {
        color: var(--accent-tint);
        font-size: 15px;
        margin: 0;
    }

    /* ================================================
       SIDEBAR
       ================================================ */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
    }

    [data-testid="stSidebar"] * {
        color: var(--sidebar-text) !important;
    }

    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] [data-testid^="stBaseButton"] {
        background: transparent !important;
        border: 1px solid rgba(231, 239, 233, 0.15) !important;
        text-align: left !important;
        transition: background var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] [data-testid^="stBaseButton"]:hover {
        background: rgba(231, 239, 233, 0.08) !important;
        border-color: rgba(231, 239, 233, 0.35) !important;
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] .stButton > button:active,
    [data-testid="stSidebar"] [data-testid^="stBaseButton"]:active {
        transform: translateX(0);
    }

    /* ================================================
       BUTTONS (main content area)
       Two selector families targeted together (.stButton
       class + stBaseButton testid) so this applies whether
       your Streamlit build exposes one or the other.
       ================================================ */
    .stButton > button,
    [data-testid^="stBaseButton"] {
        border-radius: 8px;
        transition: background var(--transition-fast), border-color var(--transition-fast),
                    box-shadow var(--transition-fast), transform var(--transition-fast);
    }

    .stButton > button:hover,
    [data-testid^="stBaseButton"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(47, 109, 79, 0.18);
    }

    .stButton > button:active,
    [data-testid^="stBaseButton"]:active {
        transform: translateY(0);
        box-shadow: none;
    }

    div[data-testid="stMainBlockContainer"] button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background: var(--accent);
        border: 1px solid var(--accent);
    }

    div[data-testid="stMainBlockContainer"] button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
        background: var(--accent-dark);
        border-color: var(--accent-dark);
    }

    /* ================================================
       INPUTS -- focus states (accessibility + polish)
       ================================================ */
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus,
    .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
        transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
    }

    /* ================================================
       METRICS
       ================================================ */
    [data-testid="stMetricValue"] {
        color: var(--text-primary);
        font-family: 'Fraunces', Georgia, serif;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
    }

    /* ================================================
       EXPANDERS -- smoother open/close affordance
       ================================================ */
    [data-testid="stExpander"] summary {
        transition: background var(--transition-fast);
        border-radius: 8px;
    }

    [data-testid="stExpander"] summary:hover {
        background: var(--accent-tint);
    }

    /* ================================================
       STATUS PILLS
       ================================================ */
    .status-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 12.5px;
        font-weight: 600;
    }

    .status-pill.success { background: var(--status-tint-success); color: var(--status-success); }
    .status-pill.warning  { background: var(--status-tint-warning); color: var(--status-warning); }
    .status-pill.danger   { background: var(--status-tint-danger);  color: var(--status-danger); }
    .status-pill.neutral  { background: var(--border); color: var(--text-secondary); }

    </style>
    """, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str = "", icon: str = "dashboard"):
    """Shared page-header block with an icon chip.

    Usage:
        from styles import load_css, render_hero
        load_css()
        render_hero("Plan Management", "Create and manage subscription plans.", icon="inventory_2")

    `icon` is any Material Symbols name (see fonts.google.com/icons),
    e.g. "dashboard", "group", "receipt_long", "notifications",
    "calendar_month", "person", "inventory_2", "bar_chart".
    """
    st.markdown(
        f"""
        <div class="app-hero">
            <div class="app-hero-icon">
                <span class="material-symbols-outlined">{icon}</span>
            </div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(label: str, kind: str = "neutral") -> str:
    """Returns an HTML span for a colored status pill.
    kind: 'success' | 'warning' | 'danger' | 'neutral'

    Usage:
        st.markdown(status_pill("Paid", "success"), unsafe_allow_html=True)
    """
    return f'<span class="status-pill {kind}">{label}</span>'
