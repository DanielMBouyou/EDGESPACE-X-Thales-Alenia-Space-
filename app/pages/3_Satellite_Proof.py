from __future__ import annotations

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header, metric_card
from app.utils import ROOT
from src.infer.runtime import model_size_mb

st.set_page_config(page_title="EDGE SPACE — Satellite Proof", layout="wide")
apply_theme()
init_state()

header("On-orbit equivalence", "Why the same code can run in orbit — evidence and specifications.")

st.write("")

# ── Ce qui change / ne change pas ────────────────────────────────────────────
st.markdown("### What changes in orbit (and what does not)")

col_same, col_diff = st.columns(2)
with col_same:
    st.markdown(
        """
<div class="edge-card">
  <div class="edge-pill">UNCHANGED</div>
  <ul style="margin-top:8px;color:#5c5e62;line-height:1.7;">
    <li>Inference code (same binary / container)</li>
    <li>ONNX model format</li>
    <li>Event packet format (signed JSON)</li>
    <li>Pipeline: ingest → preprocess → infer → packet</li>
    <li>Deterministic NMS algorithm</li>
    <li>SHA-256 hash and HMAC signature</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
with col_diff:
    st.markdown(
        """
<div class="edge-card">
  <div class="edge-pill">CHANGED</div>
  <ul style="margin-top:8px;color:#5c5e62;line-height:1.7;">
    <li>Power constraints (1–25 W vs 300 W)</li>
    <li>Memory constraints (0.5–2 GB vs 16+ GB)</li>
    <li>Downlink bandwidth (kbps – Mbps)</li>
    <li>Radiation and thermal environment</li>
    <li>Contact windows (minutes per orbit)</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ── LP / HP Switch ────────────────────────────────────────────────────────────
st.markdown("### Orbital compute profiles")

orbital_mode = st.radio(
    "Profile",
    ["Orbital-LP (Low Power)", "Orbital-HP (High Performance)"],
    horizontal=True,
)

if orbital_mode.startswith("Orbital-LP"):
    st.markdown(
        """
<div class="edge-card">
  <div style="font-weight:600;font-size:16px;margin-bottom:12px;letter-spacing:-0.01em;">
    LP profile — Ultra low-power AI accelerator
  </div>
  <div style="color:#5c5e62;font-size:14px;line-height:1.6;">
    <b>Reference:</b> Φ-Sat-2 / Intel Myriad X — flight-demonstrated for cloud detection CNN.<br/>
    <b>Business message:</b> useful AI inference can run on a few watts.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Power", "1 – 2 W", "Low-power AI accelerator")
    with c2:
        metric_card("RAM", "512 MB", "DDR / on-chip")
    with c3:
        metric_card("Inference", "500 – 1000 ms", "Per 640×640 tile")
    with c4:
        metric_card("Packet", "~1.2 kB", "Same format")

    st.markdown("**LP constraints:**")
    st.table(pd.DataFrame({
        "Parameter": ["Compute", "RAM", "Storage", "Power", "Inference / tile", "Max model", "OS"],
        "Value": [
            "Intel Myriad X / edge TPU",
            "256 – 512 MB",
            "8 – 32 GB eMMC",
            "1 – 2 W",
            "500 – 1000 ms",
            "~20 MB ONNX INT8",
            "Embedded Linux / RTOS",
        ],
    }))

else:
    st.markdown(
        """
<div class="edge-card">
  <div style="font-weight:600;font-size:16px;margin-bottom:12px;letter-spacing:-0.01em;">
    HP profile — Rugged x86 + GPU (avionics class)
  </div>
  <div style="color:#5c5e62;font-size:14px;line-height:1.6;">
    <b>Reference:</b> Moog Deep Delphi iX5 — AMD64, Linux, GPU compute ~77 GFLOP.<br/>
    <b>Business message:</b> a real edge compute can fly when the payload justifies it.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Power", "15 – 25 W", "GPU + CPU")
    with c2:
        metric_card("RAM", "2 GB ECC", "DDR3 ECC + 0.5 GB FPGA")
    with c3:
        metric_card("Inference", "30 – 80 ms", "Per 640×640 tile")
    with c4:
        metric_card("Packet", "~1.2 kB", "Same format")

    st.markdown("**HP constraints:**")
    st.table(pd.DataFrame({
        "Parameter": [
            "Compute", "RAM", "Storage", "GPU", "Power",
            "Inference / tile", "Max model", "OS",
        ],
        "Value": [
            "AMD64 (x86)",
            "2 GB DDR3 ECC + 0.5 GB FPGA",
            "eMMC + up to 768 GB SSD M.2",
            "~77 GFLOP",
            "15 – 25 W",
            "30 – 80 ms",
            "~50 MB ONNX FP16",
            "Linux",
        ],
    }))

st.divider()

# ── Compatibilité modèle ─────────────────────────────────────────────────────
st.markdown("### Current model compatibility")

onnx_fp32 = ROOT / "models" / "weights" / "best.onnx"
onnx_int8 = ROOT / "models" / "weights" / "best.int8.onnx"
pt_path = ROOT / "models" / "weights" / "best.pt"

compat_rows = []
for label, path, max_lp, max_hp in [
    ("best.pt", pt_path, 20, 50),
    ("best.onnx", onnx_fp32, 20, 50),
    ("best.int8.onnx", onnx_int8, 20, 50),
]:
    if path.exists():
        size = model_size_mb(path)
        compat_rows.append({
            "Model": label,
            "Size (MB)": f"{size:.1f}",
            "LP compatible": "Yes" if size <= max_lp else "No",
            "HP compatible": "Yes" if size <= max_hp else "Marginal",
        })

if compat_rows:
    st.table(pd.DataFrame(compat_rows))
else:
    st.info("No model available. Training may still be in progress.")

st.divider()

# ── Plateforme satellite ──────────────────────────────────────────────────────
st.markdown("### Satellite platform (hosted payload)")

st.markdown(
    """
<div class="edge-card">
  <div style="font-weight:600;font-size:15px;margin-bottom:10px;">
    Reference integration: D-Orbit ION Satellite Carrier (hosted payload)
  </div>
  <div style="color:#5c5e62;font-size:14px;line-height:1.6;">
    The mission does not require building a constellation. Compute and application are
    embedded on an existing platform.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.table(pd.DataFrame({
    "Parameter": [
        "Telecom S-band (omni)",
        "Telecom X-band (directional)",
        "Data interfaces",
        "OBDH storage",
        "In-orbit update",
        "Reference orbit",
    ],
    "Value": [
        "≈ 500 kbps — sufficient for event packets",
        "> 50 Mbps — backup for evidence and thumbnails",
        "Ethernet, USB/UART, SPI, I2C",
        "Up to 128 Gb + SSD M.2",
        "Supported (continuous improvement of the model)",
        "LEO 500–600 km, sun-synchronous",
    ],
}))

st.divider()

# ── Latence : justification quasi temps réel ──────────────────────────────────
st.markdown("### Near real-time — justification")

st.code(
    """
On-board inference  ->  Downlink S/X-band  ->  Ground station  ->  API webhook
T_infer                T_downlink              T_buffer            T_api
50 ms - 1 s            < 1 s                   variable            < 1 s
""",
    language="text",
)

st.markdown("""
**GEO relay reduces T_buffer:**
- **TDRS (NASA)**: LEO coverage ~15% → > 95% via GEO relay
- **SpaceDataHighway (ESA / Airbus)**: optical LEO → GEO relay, latency < 1 s
- **Commercial US relays**: real-time tasking and data dissemination
""")

st.table(pd.DataFrame({
    "Scenario": [
        "Direct ground station",
        "GEO relay",
    ],
    "T_infer": ["50 ms", "50 ms"],
    "T_buffer": ["~5 min (worst case)", "< 10 s"],
    "T_downlink": ["< 1 s", "< 1 s"],
    "T_api": ["< 1 s", "< 1 s"],
    "Total P50": ["~5 min", "< 15 sec"],
    "Total P95": ["~15 min", "< 60 sec"],
}))

st.caption("The bottleneck is T_buffer (contact-window wait), not the AI inference.")

st.divider()

# ── Key message ───────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="edge-card" style="text-align:center;padding:24px;">
  <div style="font-size:16px;font-weight:500;color:#171a20;line-height:1.6;">
    The PoC produces the same event packet as the orbital deployment.<br/>
    Only the transport changes — downlink simulator on the ground, S/X-band link in flight.
  </div>
</div>
""",
    unsafe_allow_html=True,
)
