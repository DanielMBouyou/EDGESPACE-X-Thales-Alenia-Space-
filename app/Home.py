from __future__ import annotations

import json

import streamlit as st

from app.ui import apply_theme, header, info_card
from app.state import init_state

st.set_page_config(page_title="EDGE SPACE - Home", layout="wide")
apply_theme()
init_state()

header(
    "Prototype A-Z",
    "On ne downlink pas des images : on downlink des alertes verifiables (event packets) integrables instantanement.",
)

st.write("")

col1, col2, col3 = st.columns(3)
with col1:
    info_card("Detect", "Detection IA navires en SAR - bbox + confidence.")
with col2:
    info_card("Packet", "Event packet JSON signe, sans image.")
with col3:
    info_card("Webhook", "POST webhook client + idempotency key.")

st.write("")

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.page_link("app/pages/1_Try_it.py", label="Lancer la demo")
with c2:
    st.page_link("app/pages/3_Satellite_Proof.py", label="Satellite Proof")
with c3:
    st.page_link("app/pages/2_KPIs.py", label="KPIs")

st.write("")

example_packet = {
    "event_id": "c9d0a3b1-1a50-4af4-83b8-1d2b12a6d7c2",
    "event_type": "vessel_detected",
    "timestamp_utc": "2026-02-05T17:00:00+00:00",
    "sensor_mode": "SAR",
    "detections": [
        {"bbox_px": [132, 88, 198, 136], "confidence": 0.92, "class": "vessel"}
    ],
    "input": {"input_hash": "...", "image_size": [640, 640]},
    "model": {"model_name": "yolov8", "model_version": "best.pt#sha256", "runtime": "onnx-int8"},
    "latency_ms": {"preprocess": 8.2, "inference": 21.7, "postprocess": 4.1, "packaging": 1.5, "total": 35.5},
    "integrity": {"packet_hash": "...", "signature": "..."},
}

st.markdown("**Exemple d'event packet**")
st.code(json.dumps(example_packet, indent=2), language="json")
