from __future__ import annotations

import streamlit as st


def init_state() -> None:
    if "events_log" not in st.session_state:
        st.session_state.events_log = []
    if "errors_log" not in st.session_state:
        st.session_state.errors_log = []
    if "last_packet" not in st.session_state:
        st.session_state.last_packet = None
    if "last_detections" not in st.session_state:
        st.session_state.last_detections = []
    if "last_latency" not in st.session_state:
        st.session_state.last_latency = {}
    if "last_image" not in st.session_state:
        st.session_state.last_image = None
    if "last_annotated" not in st.session_state:
        st.session_state.last_annotated = None
    if "last_webhook_status" not in st.session_state:
        st.session_state.last_webhook_status = None
    if "last_webhook_latency" not in st.session_state:
        st.session_state.last_webhook_latency = None
