from __future__ import annotations

import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE - Architecture", layout="wide")
apply_theme()
init_state()

header("Architecture", "From SAR chip to event packet.")

st.markdown("**Pipeline**")
st.code(
    """
[SAR Chip] -> [Preprocess 640] -> [YOLOv8] -> [NMS] -> [Event Packet]
                     |                               |
                     v                               v
                [Orbit Runtime]                 [Webhook POST]
""",
    language="text",
)

st.markdown("**Downlink assumptions (simulated)**")
st.markdown("- No raw images downlinked")
st.markdown("- Event packets are small JSON payloads")
st.markdown("- Downlink delay and queue delay are configurable")

st.markdown("**Total latency**")
st.markdown("- Onboard processing + downlink + webhook")
