import requests
import streamlit as st
from config import API_URL


def login(email, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "grant_type": "password",
                "username": email,
                "password": password
            }
        )

        if response.status_code != 200:
            return False

        token = response.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        user_response = requests.get(
            f"{API_URL}/users/me",
            headers=headers
        )

        if user_response.status_code != 200:
            return False

        st.session_state["token"] = token
        st.session_state["user"] = user_response.json()

        return True

    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False


def logout():
    st.session_state.clear()