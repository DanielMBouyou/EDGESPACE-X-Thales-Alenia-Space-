from __future__ import annotations

import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE - Security", layout="wide")
apply_theme()
init_state()

header("Security", "Packet integrity and client isolation.")

st.markdown("**Principles**")
st.markdown("- Client key is never stored in clear text")
st.markdown("- HMAC signature (V1) for packet integrity")
st.markdown("- Hash input and packet for auditability")

st.markdown("**Fields**")
st.markdown("- input.input_hash = SHA256(image bytes)")
st.markdown("- integrity.packet_hash = SHA256(canonical packet)")
st.markdown("- integrity.signature = HMAC-SHA256(packet_hash)")
