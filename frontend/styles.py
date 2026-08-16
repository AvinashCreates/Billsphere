import streamlit as st

def load_css():

    st.markdown("""
    <style>

    /* Hide Streamlit default navigation */
    [data-testid="stSidebarNav"]{
        display:none;
    }

    [data-testid="stSidebarHeader"]{
        display:none;
    }

    </style>
    """, unsafe_allow_html=True)