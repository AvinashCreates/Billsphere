import streamlit as st


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state['token']}"
    }


def is_logged_in():
    return "token" in st.session_state


def get_current_user():
    return st.session_state.get("user", None)