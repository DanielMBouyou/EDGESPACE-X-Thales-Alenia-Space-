from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE — Logs", layout="wide")
apply_theme()
init_state()

header("Logs", "Event journal, errors and exportable audit trail.")

st.write("")

# ── Events log ────────────────────────────────────────────────────────────────
st.markdown("### Events sent")

if st.session_state.events_log:
    df_events = pd.DataFrame(st.session_state.events_log)
    st.dataframe(df_events, use_container_width=True)
    st.download_button(
        "Export events (JSON)",
        data=json.dumps(st.session_state.events_log, indent=2),
        file_name="events_log.json",
        mime="application/json",
    )
else:
    st.info("No event sent. Use Try it → Send webhook.")

st.divider()

# ── Errors log ────────────────────────────────────────────────────────────────
st.markdown("### Webhook errors")

if st.session_state.errors_log:
    df_errors = pd.DataFrame(st.session_state.errors_log)
    st.dataframe(df_errors, use_container_width=True)
    st.download_button(
        "Export errors (JSON)",
        data=json.dumps(st.session_state.errors_log, indent=2),
        file_name="errors_log.json",
        mime="application/json",
    )
else:
    st.info("No error recorded.")

st.divider()

# ── Batch results ─────────────────────────────────────────────────────────────
st.markdown("### Latest packets generated")

if st.session_state.batch_packets:
    n = len(st.session_state.batch_packets)
    st.caption(f"{n} packet(s) in memory")
    for i, pkt in enumerate(st.session_state.batch_packets):
        with st.expander(f"Packet {i + 1} — {pkt.get('event_id', '?')[:8]}…"):
            st.code(json.dumps(pkt, indent=2), language="json")
    st.download_button(
        f"Export all packets ({n})",
        data=json.dumps(st.session_state.batch_packets, indent=2),
        file_name="all_packets.json",
        mime="application/json",
    )
else:
    st.info("No packet in memory. Run a detection first.")

st.divider()

# ── Robustesse ────────────────────────────────────────────────────────────────
st.markdown("### Operational robustness")

st.markdown("""
| Check | Status |
|---|---|
| CPU fallback when no GPU | ONNX Runtime CPU |
| Batch handling (N images) | Sequential processing |
| Invalid input rejection | try / except + log |
| Exportable logs | JSON download |
| Degraded mode (model missing) | Explicit error |
""")

# ── Clear logs ────────────────────────────────────────────────────────────────
st.divider()
if st.button("Clear all logs"):
    st.session_state.events_log = []
    st.session_state.errors_log = []
    st.session_state.batch_packets = []
    st.rerun()
