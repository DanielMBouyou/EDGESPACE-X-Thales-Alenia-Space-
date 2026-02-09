from __future__ import annotations

import json

import streamlit as st

from app.ui import apply_theme, header, metric_card
from app.state import init_state

st.set_page_config(page_title="EDGE SPACE — Wildfire Detection", page_icon="🔥", layout="wide")
apply_theme()
init_state()

# ── Hero ──────────────────────────────────────────────────────────────────────
header(
    "EDGE SPACE  🛰️🔥",
    "On-board AI → Event packets (kB) → webhook / API → décision en minutes.",
)

st.write("")

st.markdown(
    """
<div class="edge-card" style="text-align:center;padding:28px 32px;">
  <div style="font-size:22px;font-weight:700;color:#0b1a3a;margin-bottom:10px;">
    🎯 On ne downlink pas des images — on downlink des
    <span style="color:#e85d04;">alertes vérifiables</span>
  </div>
  <div style="font-size:15px;color:#4b4f6b;line-height:1.6;">
    Détection rapide des feux de forêt à partir d'images satellites et d'IA embarquée.<br/>
    Event packets signés, intégrables instantanément via webhook / API.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── 3 KPIs visibles ──────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("📦 Event Packet", "~1.2 kB", "vs ~50 MB image brute — ×41 000 plus petit")
with col2:
    metric_card("⏱️ Latence orbite → sol", "< 90 sec", "inférence + downlink + API webhook")
with col3:
    metric_card("📉 Volume évité", "99.99 %", "de données non transférées")

st.write("")
st.divider()

# ── Navigation rapide ─────────────────────────────────────────────────────────
st.markdown("### 🚀 Navigation rapide")
c1, c2, c3, c4 = st.columns(4)


def safe_page_link(label: str, *paths: str) -> None:
    for p in paths:
        try:
            st.page_link(p, label=label)
            return
        except Exception:
            continue
    st.button(label, disabled=True)


with c1:
    safe_page_link("🔬 Démo live", "pages/1_Try_it.py", "app/pages/1_Try_it.py")
with c2:
    safe_page_link("📊 KPIs", "pages/2_KPIs.py", "app/pages/2_KPIs.py")
with c3:
    safe_page_link("🛰️ Satellite Proof", "pages/3_Satellite_Proof.py", "app/pages/3_Satellite_Proof.py")
with c4:
    safe_page_link("🏗️ Architecture", "pages/4_Architecture.py", "app/pages/4_Architecture.py")

st.write("")
st.divider()

# ── Exemple Event Packet ─────────────────────────────────────────────────────
st.markdown("### 📋 Exemple d'Event Packet")
st.caption("C'est **exactement** ce qui est transmis du satellite au sol — pas l'image.")

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
**Champs clés**

| Champ | Rôle |
|---|---|
| `event_type` | wildfire / oil_spill / … |
| `sat_id` | Identifiant satellite |
| `geolocation` | Lat / lon + geohash |
| `detections[]` | Bbox + confiance + classe |
| `evidence` | Thumbnail 128×128 + hash |
| `integrity` | Hash packet + HMAC signature |
| `latency_ms` | Chronométrage complet |

**~1.2 kB** total transmis — pas l'image.
"""
    )

st.write("")
st.divider()

# ── Comparatif Image vs Packet ────────────────────────────────────────────────
st.markdown("### 📡 Image brute vs Event Packet")
left, right = st.columns(2)
with left:
    st.markdown(
        """
<div class="edge-card" style="border-left:4px solid #dc2626;">
  <b style="font-size:16px;">❌ Approche classique — downlink images</b>
  <ul style="color:#4b4f6b;margin-top:10px;font-size:14px;">
    <li>Image brute : <b>50 – 500 MB</b></li>
    <li>Downlink S-band 500 kbps → <b>13 – 130 min</b></li>
    <li>Fenêtre de contact ~10 min / passage</li>
    <li>Traitement au sol → heures de délai</li>
    <li>⚠️ Impossible de couvrir en temps réel</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
with right:
    st.markdown(
        """
<div class="edge-card" style="border-left:4px solid #16a34a;">
  <b style="font-size:16px;">✅ EDGE SPACE — event packets</b>
  <ul style="color:#4b4f6b;margin-top:10px;font-size:14px;">
    <li>Event packet : <b>~1.2 kB</b></li>
    <li>Downlink S-band → <b>< 1 sec</b></li>
    <li>Multiple opportunités par orbite</li>
    <li>Alerte webhook instantanée</li>
    <li>✅ Quasi temps réel bout-en-bout</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

st.write("")
st.caption("EDGE SPACE — Détection rapide des feux de forêt · Incubateur Thales")
