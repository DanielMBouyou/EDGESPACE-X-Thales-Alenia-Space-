from __future__ import annotations

import pandas as pd
import streamlit as st

from app.state import init_state
from app.ui import apply_theme, header

st.set_page_config(page_title="EDGE SPACE — Security", layout="wide")
apply_theme()
init_state()

header("Security & audit", "Reproducibility, integrity, full traceability.")

st.write("")

# ── Reproductibilité ─────────────────────────────────────────────────────────
st.markdown("### Reproducibility")
st.markdown(
    """
<div class="edge-card">
  <div style="color:#5c5e62;font-size:14px;line-height:1.8;">
    <b style="color:#171a20;">Same input → same output.</b> Guaranteed by:
    <ul>
      <li><b>Versioned model</b> — SHA-256 hash of the ONNX / PT file</li>
      <li><b>Frozen configuration</b> — confidence threshold, input size, NMS fixed</li>
      <li><b>Hashing throughout</b> — input, model, packet</li>
      <li><b>Deterministic NMS</b> — identical algorithm and ordering</li>
      <li><b>No randomness</b> — inference without augmentation</li>
    </ul>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ── Chaîne d'intégrité ───────────────────────────────────────────────────────
st.markdown("### Integrity chain")

st.code(
    """
+--------------------+
|  Input image       |
|  SHA-256 -> input_hash
+--------+-----------+
         |
         v
+--------------------+
|  ONNX model        |
|  SHA-256 -> model_hash
+--------+-----------+
         |
         v
+--------------------+
|  Event packet      |
|  SHA-256 -> packet_hash
+--------+-----------+
         |
         v
+--------------------+
|  Signature         |
|  HMAC-SHA256(secret, packet_hash)
|  -> integrity.signature
+--------------------+
""",
    language="text",
)

st.markdown("""
**Verification on the receiver side:**
1. Recompute `packet_hash` = SHA-256(packet without integrity)
2. Verify `signature` = HMAC-SHA256(shared_secret, packet_hash)
3. If matched → packet is authentic and untampered
""")

st.divider()

# ── Robustesse opérationnelle ─────────────────────────────────────────────────
st.markdown("### Operational robustness")

st.table(pd.DataFrame({
    "Scenario": [
        "No GPU available",
        "Corrupted / invalid image",
        "Batch of N images",
        "Model missing",
        "Webhook timeout",
        "Empty result (0 detections)",
    ],
    "Behavior": [
        "Automatic CPU fallback (ONNX Runtime)",
        "Reject + error log + skip",
        "Sequential processing, one packet per image",
        "Explicit error, no crash",
        "Three retries with backoff, log failure",
        "Event packet still generated (detections: [])",
    ],
    "Status": ["OK", "OK", "OK", "OK", "OK", "OK"],
}))

st.divider()

# ── Audit Trail ───────────────────────────────────────────────────────────────
st.markdown("### Audit trail")

st.markdown("""
Each event packet carries its own traceability:

```json
{
  "input": {
    "input_hash": "sha256:abc123...",
    "image_size": [640, 640]
  },
  "model": {
    "model_name": "yolo11s-fire",
    "model_version": "sha256:def456...",
    "runtime": "onnx-fp16"
  },
  "integrity": {
    "packet_hash": "sha256:789abc...",
    "signature": "hmac-sha256:...",
    "model_hash": "sha256:def456..."
  }
}
```

Logs are exportable — see the Logs page.
""")

st.divider()

# ── Séparation Compute / Transport ────────────────────────────────────────────
st.markdown("### Compute vs transport separation")

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
<div class="edge-card">
  <div class="edge-pill">COMPUTE</div>
  <b style="color:#171a20;">Identical on ground and in orbit</b>
  <ul style="color:#5c5e62;margin-top:8px;line-height:1.7;">
    <li>Image loading</li>
    <li>Pre-processing (resize 640)</li>
    <li>ONNX inference</li>
    <li>NMS and filtering</li>
    <li>Event packet packaging</li>
    <li>HMAC signature</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
<div class="edge-card">
  <div class="edge-pill">TRANSPORT</div>
  <b style="color:#171a20;">The only differing element</b>
  <ul style="color:#5c5e62;margin-top:8px;line-height:1.7;">
    <li><b>Ground (PoC):</b> HTTP POST webhook</li>
    <li><b>Orbit:</b> S/X-band link → ground station → API</li>
    <li>Same JSON payload in both cases</li>
    <li>Downlink simulator built into the PoC</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
