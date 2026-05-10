from __future__ import annotations

import json

import streamlit as st

from app.ui import apply_theme, header, metric_card
from app.state import init_state

st.set_page_config(page_title="EDGE SPACE — Wildfire Detection", layout="wide")
apply_theme()
init_state()

# ── Hero ──────────────────────────────────────────────────────────────────────
header(
    "EDGE SPACE",
    "On-board AI. Verifiable event packets. Decision-grade alerts in minutes.",
)

st.write("")

st.markdown(
    """
<div class="edge-card" style="padding:32px;">
  <div style="font-size:22px;font-weight:600;color:#171a20;margin-bottom:12px;letter-spacing:-0.02em;">
    We do not downlink images. We downlink verifiable alerts.
  </div>
  <div style="font-size:15px;color:#5c5e62;line-height:1.6;">
    Wildfire detection from satellite imagery, executed on-board. Signed event packets,
    integrable through webhook or API.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── 3 KPIs visibles ──────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Event packet", "~1.2 kB", "vs ~50 MB raw image — 41,000× smaller")
with col2:
    metric_card("Orbit-to-ground latency", "< 90 sec", "inference + downlink + API webhook")
with col3:
    metric_card("Volume avoided", "99.99 %", "of data not transferred")

st.write("")
st.divider()

# ── Navigation rapide ─────────────────────────────────────────────────────────
st.markdown("### Navigation")

_NAV = [
    ("Live demo", "pages/1_Try_it.py"),
    ("KPIs", "pages/2_KPIs.py"),
    ("Satellite proof", "pages/3_Satellite_Proof.py"),
    ("Architecture", "pages/4_Architecture.py"),
    ("Security", "pages/5_Security.py"),
    ("API", "pages/6_API_Integration.py"),
    ("Logs", "pages/7_Logs.py"),
]

cols = st.columns(len(_NAV))
for col, (label, page) in zip(cols, _NAV):
    with col:
        if st.button(label, use_container_width=True):
            st.switch_page(page)

st.write("")
st.divider()

# ── Exemple Event Packet ─────────────────────────────────────────────────────
st.markdown("### Event packet sample")
st.caption("This is exactly what is transmitted from the satellite to the ground — not the image.")

example_packet = {
    "event_id": "c9d0a3b1-1a50-4af4-83b8-1d2b12a6d7c2",
    "event_type": "wildfire",
    "timestamp_utc": "2026-02-09T14:30:00+00:00",
    "sat_id": "EDGESPACE-SAT-01",
    "sensor_mode": "Optical/IR",
    "geolocation": {"lat": 36.778, "lon": -119.418, "geohash": "9q8yyk8yuv"},
    "detections": [
        {"bbox_px": [132, 88, 298, 236], "confidence": 0.94, "class": "fire", "centroid_px": [215, 162]}
    ],
    "evidence": {"thumbnail_b64": "<128x128 JPEG b64>", "thumbnail_hash": "sha256:a1b2c3..."},
    "input": {"input_hash": "sha256:...", "image_size": [640, 640], "tile_index": 0},
    "model": {"model_name": "yolo11s-fire", "model_version": "best.pt#sha256:...", "runtime": "onnx-fp16"},
    "latency_ms": {"preprocess": 5.2, "inference": 18.7, "postprocess": 3.1, "packaging": 1.5, "total": 28.5},
    "integrity": {"packet_hash": "sha256:...", "signature": "hmac-sha256:...", "model_hash": "sha256:..."},
}

col_j, col_e = st.columns([3, 2])
with col_j:
    st.code(json.dumps(example_packet, indent=2), language="json")
with col_e:
    st.markdown(
        """
**Key fields**

| Field | Role |
|---|---|
| `event_type` | wildfire / oil_spill / … |
| `sat_id` | Satellite identifier |
| `geolocation` | Lat / lon + geohash |
| `detections[]` | Bbox + confidence + class |
| `evidence` | Thumbnail 128×128 + hash |
| `integrity` | Packet hash + HMAC signature |
| `latency_ms` | Full timing breakdown |

Total transmitted: **~1.2 kB**. The image stays on board.
"""
    )

st.write("")
st.divider()

# ── Comparatif Image vs Packet ────────────────────────────────────────────────
st.markdown("### Raw image vs event packet")
left, right = st.columns(2)
with left:
    st.markdown(
        """
<div class="edge-card">
  <div class="edge-pill">CLASSIC</div>
  <b style="font-size:15px;color:#171a20;">Downlink raw images</b>
  <ul style="color:#5c5e62;margin-top:10px;font-size:14px;line-height:1.7;">
    <li>Raw image: <b>50 – 500 MB</b></li>
    <li>S-band downlink at 500 kbps: <b>13 – 130 min</b></li>
    <li>Contact window ~10 min per pass</li>
    <li>Ground processing: hours of additional delay</li>
    <li>Real-time coverage is not feasible</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
with right:
    st.markdown(
        """
<div class="edge-card" style="border-color:#171a20;border-width:2px;">
  <div class="edge-pill" style="background:#171a20;color:#ffffff;">EDGE SPACE</div>
  <b style="font-size:15px;color:#171a20;">Downlink event packets</b>
  <ul style="color:#5c5e62;margin-top:10px;font-size:14px;line-height:1.7;">
    <li>Event packet: <b>~1.2 kB</b></li>
    <li>S-band downlink: <b>&lt; 1 sec</b></li>
    <li>Multiple opportunities per orbit</li>
    <li>Webhook alert is instantaneous</li>
    <li>Near real-time end-to-end</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

st.write("")
st.caption("EDGE SPACE — Wildfire detection from satellite imagery · Thales Incubator")
