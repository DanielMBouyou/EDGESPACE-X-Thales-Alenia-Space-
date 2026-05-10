from __future__ import annotations

import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE — Architecture", layout="wide")
apply_theme()
init_state()

header("Architecture", "Three software blocks. Same code from PoC to orbit.")

st.write("")

# ── 3 blocs ───────────────────────────────────────────────────────────────────
st.markdown("### Three software blocks")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
<div class="edge-card" style="min-height:240px;">
  <div style="font-weight:600;font-size:15px;margin-bottom:10px;">01 &nbsp;UI Streamlit</div>
  <div style="color:#5c5e62;font-size:13px;line-height:1.7;">
    Showcase and test sandbox.<br/>
    Drag &amp; drop upload (single / batch ZIP).<br/>
    Five-step pipeline visualization.<br/>
    JSON export and webhook test.<br/><br/>
    <span class="edge-pill">DEMO ONLY</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
<div class="edge-card" style="min-height:240px;">
  <div style="font-weight:600;font-size:15px;margin-bottom:10px;">02 &nbsp;Inference engine</div>
  <div style="color:#5c5e62;font-size:13px;line-height:1.7;">
    Standalone Python library (<code>src/infer/</code>).<br/>
    ONNX or PyTorch runtime.<br/>
    Deterministic pre / post-processing.<br/>
    NMS and confidence filtering.<br/><br/>
    <span class="edge-pill">GROUND + ORBIT</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
<div class="edge-card" style="min-height:240px;">
  <div style="font-weight:600;font-size:15px;margin-bottom:10px;">03 &nbsp;Packetizer + signer</div>
  <div style="color:#5c5e62;font-size:13px;line-height:1.7;">
    JSON event packet generation.<br/>
    SHA-256 hash (input, model, packet).<br/>
    HMAC-SHA256 signature.<br/>
    Webhook client with idempotency key.<br/><br/>
    <span class="edge-pill">GROUND + ORBIT</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ── Pipeline ──────────────────────────────────────────────────────────────────
st.markdown("### Full pipeline")

st.code(
    """
Satellite tile (640x640)
    |
    v
+----------+   +-------------+   +----------+   +---------+   +--------+
| Ingest   |-->| Pre-process |-->| Inference|-->| Post-NMS|-->| Packet |
| load     |   | resize/norm |   | YOLO11s  |   | filter  |   | signer |
+----------+   +-------------+   | ONNX/PT  |   | cluster |   +---+----+
                                 +----------+   +---------+       |
                                                       +----------+
                                                       |          |
                                                       v          v
                                                +----------+ +---------+
                                                | Evidence | | Webhook |
                                                |thumb+hash| |POST API |
                                                +----------+ +---------+
""",
    language="text",
)

st.divider()

# ── Déploiement orbital ───────────────────────────────────────────────────────
st.markdown("### Orbital deployment")

st.markdown(
    """
<div class="edge-card">
  <div style="font-weight:600;font-size:15px;margin-bottom:12px;">Container packaging</div>
  <div style="color:#5c5e62;font-size:14px;line-height:1.6;">
    The <b>Inference engine</b> and <b>Packetizer</b> blocks are packaged as a lightweight container.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.code(
    """
# Sample orbital Dockerfile
FROM python:3.12-slim

COPY src/infer/ /app/infer/
COPY src/utils/ /app/utils/
COPY models/weights/best.onnx /app/models/

RUN pip install onnxruntime numpy pillow

ENTRYPOINT ["python", "-m", "app.infer.runtime"]
""",
    language="dockerfile",
)

st.markdown("""
**Same inputs and outputs:**
- **Input:** satellite tile (640×640)
- **Output:** signed JSON event packet (~1.2 kB)

**What changes:** the transport (filesystem / local API → S/X-band link).

| Profile | Compute | Runtime | Model |
|---|---|---|---|
| LP (Low Power) | Myriad X / edge TPU | ONNX INT8 | best.int8.onnx |
| HP (High Perf) | AMD64 + GPU | ONNX FP16 | best.onnx |
| Ground (demo) | Desktop GPU | PyTorch FP32 | best.pt |
""")

st.divider()

# ── Continuous improvement ────────────────────────────────────────────────────
st.markdown("### In-orbit continuous improvement")

st.markdown("""
Thanks to on-board storage (128 Gb+) and software-update capability:

1. **Upload** a new ONNX model from the ground station
2. **Validation** on-board (test on reference images)
3. **Switch** to the new model (rollback supported)
4. **Telemetry**: performance metrics returned through event packets

The model improves continuously without changing the hardware.
""")
